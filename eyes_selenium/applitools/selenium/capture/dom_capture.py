from __future__ import absolute_import, unicode_literals

import json
import re
import typing as tp
from typing import Dict, List, Text

import attr
import requests
import tinycss2

from applitools.common import logger
from applitools.common.utils import (
    datetime_utils,
    is_absolute_url,
    is_url_with_scheme,
    json_utils,
    urljoin,
)
from applitools.common.utils.json_utils import JsonInclude
from applitools.selenium import eyes_selenium_utils
from applitools.selenium.positioning import ScrollPositionProvider
from applitools.selenium.resource import get_resource

if tp.TYPE_CHECKING:
    from applitools.selenium.webdriver import EyesWebDriver

__all__ = ("get_full_window_dom",)
_CAPTURE_FRAME_SCRIPT = (
    get_resource("captureDomAndPoll.js") + "return __captureDomAndPoll();"
)
_CAPTURE_FRAME_SCRIPT_IE = (
    get_resource("captureDomAndPollForIE.js") + "return __captureDomAndPollForIE();"
)
DOM_EXTRACTION_TIMEOUT = 5 * 60 * 1000
CSS_DOWNLOAD_TIMEOUT = 3  # Secs


@attr.s
class Separator:
    separator = attr.ib(metadata={JsonInclude.THIS: True})
    css_start_token = attr.ib(metadata={JsonInclude.THIS: True})
    css_end_token = attr.ib(metadata={JsonInclude.THIS: True})
    iframe_start_token = attr.ib(metadata={JsonInclude.THIS: True})
    iframe_end_token = attr.ib(metadata={JsonInclude.THIS: True})


class CssDownloader:
    def __init__(self):
        self.css_urls = []

    def fetch_css_files(self, css_start_token, css_end_token, urls):
        self.css_start_token = css_start_token
        self.css_end_token = css_end_token
        self.css_urls.extend(urls)

    def results(self):
        return {
            url: clean_for_json(_process_raw_css_node(CssNode(None, url, None)))
            for url in self.css_urls
        }


def _parse_script_result(script_result):
    # type: (Text) -> (Separator, List, List, List)
    missing_css, missing_frames, data = [], [], []
    lines = re.split(r"\r?\n", script_result)
    separators = json_utils.attr_from_json(lines[0], Separator)
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
    frame_data = {}
    switch_to = driver.switch_to
    fc = driver.frame_chain.clone()
    for missing_frame_line in missing_frames_list:
        logger.info("Switching to frame line: {}".format(missing_frame_line))
        original_location = driver.execute_script("return document.location.href")
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
                location_after_switch = driver.execute_script(
                    "return document.location.href"
                )
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


def efficient_string_replace(ref_id_open_token, ref_id_end_token, input, replacements):
    res = input
    for ph, replacement in replacements.items():
        res = res.replace(ref_id_open_token + ph + ref_id_end_token, replacement)
    return res


def clean_for_json(s):
    # make json array and remove [" and "]
    return json.dumps([s])[2:-2]


def get_frame_dom(driver, css_downoader):
    # type: (EyesWebDriver, CssDownloader) -> Dict
    script_result = eyes_selenium_utils.get_dom_script_result(
        driver, DOM_EXTRACTION_TIMEOUT, "DomCapture_StopWatch", _CAPTURE_FRAME_SCRIPT,
    )
    separators, missing_css, missing_frames, data = _parse_script_result(script_result)

    css_downoader.fetch_css_files(
        separators.css_start_token, separators.css_end_token, missing_css
    )
    frame_data = recurse_frames(driver, missing_frames, css_downoader)
    return efficient_string_replace(
        separators.iframe_start_token, separators.iframe_end_token, data[0], frame_data
    )


def get_dom(driver):
    # type: (EyesWebDriver) -> Text
    original_fc = driver.frame_chain.clone()
    css_downloader = CssDownloader()
    dom = get_frame_dom(driver, css_downloader)
    if original_fc is not None:
        driver.switch_to.frames(original_fc)
    return efficient_string_replace(
        css_downloader.css_start_token,
        css_downloader.css_end_token,
        dom,
        css_downloader.results(),
    )


@datetime_utils.timeit
def get_full_window_dom(driver, return_as_dict=False):
    # type: (EyesWebDriver, bool) -> tp.Union[str, dict]
    current_root_element = eyes_selenium_utils.curr_frame_scroll_root_element(driver)

    with eyes_selenium_utils.get_and_restore_state(
        ScrollPositionProvider(driver, current_root_element)
    ):
        logger.debug("Traverse DOM Tree")
        script_result = get_dom(driver)

    return json.loads(script_result) if return_as_dict else script_result


def _process_raw_css_node(node, minimize_css=True):
    # type: (CssNode, bool) -> tp.Text

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


def _parse_and_serialize_css(node, text, minimize=False):
    # type: (CssNode, tp.Text, bool) -> tp.Generator
    def is_import_node(n):
        return n.type == "at-rule" and n.lower_at_keyword == "import"

    stylesheet = tinycss2.parse_stylesheet(
        text, skip_comments=True, skip_whitespace=True
    )
    for style_node in stylesheet:
        if is_import_node(style_node):
            for tag in style_node.prelude:
                if tag.type == "url":
                    logger.debug("The node has import")
                    yield CssNode.create_sub_node(parent_node=node, href=tag.value)
            continue

        try:
            if minimize and style_node.content:
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
    # type: (tp.Text, tp.Text) -> tp.Text
    if is_absolute_url(value) and not is_url_with_scheme(value):  # noqa
        url = urljoin("http://", value)
    else:
        url = urljoin(base_url, value)
    return url


class CssNode(object):
    __slots__ = ("base_url", "url", "text")

    def __init__(self, base_url, url, text):
        # type: (tp.Optional[tp.Text], tp.Optional[tp.Text], tp.Optional[tp.Text]) -> None
        self.base_url = base_url
        self.url = url
        self.text = text

    @classmethod
    def create(cls, base_url, href=None, text=None):
        # type: (tp.Text, tp.Optional[tp.Text], tp.Optional[tp.Text]) -> 'CssNode'
        url = _make_url(base_url, href) if href else None
        return cls(base_url, url, text)

    @classmethod
    def create_sub_node(cls, parent_node, href, text=None):
        # type: ('CssNode', tp.Text, tp.Optional[tp.Text]) -> 'CssNode'
        url = _make_url(parent_node.base_url, href)
        return cls(parent_node.base_url, url, text)

    @classmethod
    def create_serialized_node(cls, text):
        # type: (tp.Text) -> 'CssNode'
        return cls(base_url=None, url=None, text=text)
