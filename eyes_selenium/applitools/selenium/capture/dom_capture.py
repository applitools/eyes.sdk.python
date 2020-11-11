from __future__ import absolute_import, unicode_literals

import json
import re
import threading
import typing as tp
from collections import OrderedDict
from concurrent.futures.thread import ThreadPoolExecutor
from itertools import chain
from typing import Dict, Generator, List, Optional, Text, Union

import attr
import requests
import tinycss2

from applitools.common import EyesError, logger
from applitools.common.utils import (
    datetime_utils,
    is_absolute_url,
    is_url_with_scheme,
    json_utils,
    urljoin,
)
from applitools.common.utils.efficient_string_replace import (
    clean_for_json,
    efficient_string_replace,
)
from applitools.common.utils.json_utils import JsonInclude
from applitools.selenium import eyes_selenium_utils
from applitools.selenium.positioning import ScrollPositionProvider
from applitools.selenium.resource import get_resource

if tp.TYPE_CHECKING:
    from applitools.common.utils.custom_types import AnyWebDriver
    from applitools.selenium.webdriver import EyesWebDriver

__all__ = ("get_full_window_dom",)
_CAPTURE_FRAME_SCRIPT = (
    get_resource("captureDomAndPoll.js") + "return __captureDomAndPoll();"
)
_CAPTURE_FRAME_SCRIPT_FOR_IE = (
    get_resource("captureDomAndPollForIE.js") + "return __captureDomAndPollForIE();"
)
DOM_EXTRACTION_TIMEOUT = 5 * 60 * 1000
CSS_DOWNLOAD_TIMEOUT = 30  # Secs


@attr.s
class Separators(object):
    separator = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    css_start_token = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    css_end_token = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    iframe_start_token = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    iframe_end_token = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text


class CssDownloader(object):
    def __init__(self):
        self.css_start_token = None
        self.css_end_token = None
        self._executor = ThreadPoolExecutor(4)
        self._results = []

    def fetch_css_files(self, base_url, css_start_token, css_end_token, urls):
        #  type: (Text, Text, Text, List[Text]) -> None
        if not is_absolute_url(base_url):
            logger.info("Base URL is not an absolute URL!")
        assert self.css_start_token is None or self.css_start_token == css_start_token
        assert self.css_end_token is None or self.css_end_token == css_end_token
        self.css_start_token = css_start_token
        self.css_end_token = css_end_token
        nodes = [CssNode.create(base_url, url) for url in urls]
        futures = self._executor.map(
            _download_jsonify_node, urls, nodes, timeout=CSS_DOWNLOAD_TIMEOUT
        )
        self._results.append(futures)

    def results(self):
        # type: () -> Dict[Text, Text]
        return {url: data for url, data in chain(*self._results)}

    def __enter__(self):
        self._executor.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._executor.__exit__(exc_type, exc_val, exc_tb)


def _parse_script_result(script_result):
    # type: (Text) -> (Separators, List, List, List)
    missing_css, missing_frames, data = [], [], []
    lines = re.split(r"\r?\n", script_result)
    separators = json_utils.attr_from_json(lines[0], Separators)
    blocks = [missing_css, missing_frames, data]
    block_index = 0
    for line in lines[1:]:
        if separators.separator == line:
            block_index += 1
        else:
            blocks[block_index].append(line)
    logger.info("missing css count: {}".format(len(missing_css)))
    logger.info("missing frames count: {}".format(len(missing_frames)))
    return separators, missing_css, missing_frames, data


def recurse_frames(driver, missing_frames_list, css_downoader):
    # type: (EyesWebDriver, List[Text], CssDownloader) -> Dict[Text, Text]
    frame_data = {}
    switch_to = driver.switch_to
    fc = driver.frame_chain.clone()
    for missing_frame_line in missing_frames_list:
        logger.info("Switching to frame line: {}".format(missing_frame_line))
        original_location = _frame_url(driver)
        try:
            for missing_frame_xpath in missing_frame_line.split(","):
                logger.info("Switching to specific frame: " + missing_frame_xpath)
                frame = driver.find_element_by_xpath(missing_frame_xpath)
                logger.info(
                    "Switched to frame({}) with src ({})".format(
                        missing_frame_xpath, frame.get_attribute("src")
                    )
                )
                switch_to.frame(frame)
            location_after_switch = _frame_url(driver)
            if location_after_switch == original_location:
                logger.info("Switching to frame failed")
                frame_data[missing_frame_line] = ""
                continue
            frame_data[missing_frame_line] = get_frame_dom(driver, css_downoader)
        except Exception:
            logger.exception("Failed to get frame dom")
            frame_data[missing_frame_line] = ""
        switch_to.frames(fc)
    return frame_data


def get_frame_dom(driver, css_downoader):
    # type: (EyesWebDriver, CssDownloader) -> Text
    is_ie = driver.user_agent.is_internet_explorer
    script = _CAPTURE_FRAME_SCRIPT_FOR_IE if is_ie else _CAPTURE_FRAME_SCRIPT
    script_result = get_dom_script_result(
        driver, DOM_EXTRACTION_TIMEOUT, "DomCapture_StopWatch", script
    )
    separators, missing_css, missing_frames, data = _parse_script_result(script_result)

    css_downoader.fetch_css_files(
        _frame_url(driver),
        separators.css_start_token,
        separators.css_end_token,
        missing_css,
    )
    frame_data = recurse_frames(driver, missing_frames, css_downoader)
    return efficient_string_replace(
        separators.iframe_start_token, separators.iframe_end_token, data[0], frame_data
    )


def get_dom(driver):
    # type: (EyesWebDriver) -> Text
    with CssDownloader() as css_downloader, driver.saved_frame_chain():
        dom = get_frame_dom(driver, css_downloader)
        return efficient_string_replace(
            css_downloader.css_start_token,
            css_downloader.css_end_token,
            dom,
            css_downloader.results(),
        )


@datetime_utils.timeit
def get_full_window_dom(driver, return_as_dict=False):
    # type: (EyesWebDriver, bool) -> Union[str, dict]
    current_root_element = eyes_selenium_utils.curr_frame_scroll_root_element(driver)

    with eyes_selenium_utils.get_and_restore_state(
        ScrollPositionProvider(driver, current_root_element)
    ):
        logger.debug("Traverse DOM Tree")
        script_result = get_dom(driver)

    return json.loads(script_result) if return_as_dict else script_result


def get_dom_script_result(driver, dom_extraction_timeout, timer_name, script_for_run):
    # type: (AnyWebDriver, int, Text, Text) -> Dict
    is_check_timer_timeout = []
    script_response = {}
    status = None

    def start_timer():
        def set_timer():
            is_check_timer_timeout.append(True)

        timer = threading.Timer(
            datetime_utils.to_sec(dom_extraction_timeout), set_timer
        )
        timer.daemon = True
        timer.setName(timer_name)
        timer.start()
        return timer

    timer = start_timer()
    while True:
        if status == "SUCCESS" or is_check_timer_timeout:
            del is_check_timer_timeout[:]
            break
        script_result_string = driver.execute_script(script_for_run)
        try:
            script_response = json.loads(
                script_result_string, object_pairs_hook=OrderedDict
            )
            status = script_response.get("status")
        except Exception as e:
            logger.exception(e)
        datetime_utils.sleep(1000, "Waiting for the end of DOM extraction")
    timer.cancel()
    script_result = script_response.get("value")
    if script_result is None or status == "ERROR":
        raise EyesError("Failed to capture script_result")
    return script_result


def _download_jsonify_node(url, node):
    # type: (Text, CssNode) -> (Text, Text)
    return url, clean_for_json(_process_raw_css_node(node, minimize_css=False))


def _process_raw_css_node(node, minimize_css=True):
    # type: (CssNode, bool) -> Text

    @datetime_utils.retry()
    def get_css(url):
        if url.startswith("blob:") or url.startswith("data:"):
            logger.warning("Passing blob URL: {}".format(url))
            return ""
        return requests.get(url, timeout=CSS_DOWNLOAD_TIMEOUT).text.strip()

    def iterate_css_sub_nodes(node, text=None):
        if text is None:
            text = node.text
            if node.text is None:
                text = get_css(node.url)

        for sub_node in _parse_and_serialize_css(node, text, minimize_css):
            if sub_node.url:
                text = get_css(sub_node.url)
                # yield from
                for res in iterate_css_sub_nodes(sub_node, text):
                    yield res
                continue
            yield sub_node.text

    return "".join(iterate_css_sub_nodes(node))


def _parse_and_serialize_css(node, text, minimize=False):  # noqa
    # type: (CssNode, Text, bool) -> Generator
    def is_import_node(n):
        return n.type == "at-rule" and n.lower_at_keyword == "import"

    stylesheet = tinycss2.parse_stylesheet(
        text, skip_comments=True, skip_whitespace=True
    )
    for style_node in stylesheet:
        if is_import_node(style_node):
            for tag in style_node.prelude:
                if tag.type in ("url", "string"):
                    logger.debug("The node has import")
                    yield CssNode.create_sub_node(parent_node=node, href=tag.value)
            continue
        if getattr(style_node, "kind", None) == "invalid":
            logger.warning(
                "Cannot serialize item: {}, ParseError: {}".format(
                    style_node, style_node.message
                )
            )
            continue
        try:
            if minimize and style_node and style_node.content:
                try:
                    # remove whitespaces inside blocks
                    style_node.content = [
                        tok for tok in style_node.content if tok.type != "whitespace"
                    ]
                except AttributeError as e:
                    logger.warning(
                        "Cannot serialize item: {}, cause error: {}".format(
                            style_node, str(e)
                        )
                    )
            serialized = style_node.serialize()
            if minimize:
                serialized = (
                    serialized.replace("\n", "").replace("/**/", " ").replace(" {", "{")
                )

        except TypeError as e:
            logger.warning(str(e))
            continue
        yield CssNode.create_serialized_node(text=serialized)


def _make_url(base_url, value):
    # type: (Text, Text) -> Text
    if is_absolute_url(value) and not is_url_with_scheme(value):  # noqa
        url = urljoin("http://", value)
    else:
        url = urljoin(base_url, value)
    return url


def _frame_url(driver):
    # type: (EyesWebDriver) -> Text
    return driver.execute_script("return document.location.href")


class CssNode(object):
    __slots__ = ("base_url", "url", "text")

    def __init__(self, base_url, url, text):
        # type: (Optional[Text], Optional[Text], Optional[Text]) -> None
        self.base_url = base_url
        self.url = url
        self.text = text

    @classmethod
    def create(cls, base_url, href=None, text=None):
        # type: (Text, Optional[Text], Optional[Text]) -> 'CssNode'
        url = _make_url(base_url, href) if href else None
        return cls(base_url, url, text)

    @classmethod
    def create_sub_node(cls, parent_node, href, text=None):
        # type: ('CssNode', Text, Optional[Text]) -> 'CssNode'
        url = _make_url(parent_node.url, href)
        return cls(parent_node.base_url, url, text)

    @classmethod
    def create_serialized_node(cls, text):
        # type: (Text) -> 'CssNode'
        return cls(base_url=None, url=None, text=text)
