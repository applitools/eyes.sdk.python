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
_CAPTURE_FRAME_SCRIPT = get_resource("captureDomAndPoll.js")
DOM_EXTRACTION_TIMEOUT = 5 * 60 * 1000


@attr.s
class Separator:
    separator = attr.ib(metadata={JsonInclude.THIS: True})
    css_start_token = attr.ib(metadata={JsonInclude.THIS: True})
    css_end_token = attr.ib(metadata={JsonInclude.THIS: True})
    iframe_start_token = attr.ib(metadata={JsonInclude.THIS: True})
    iframe_end_token = attr.ib(metadata={JsonInclude.THIS: True})


def _parse_script_result(script_result, missing_css, missing_frames, data):
    # type: (Text, List, List, List) -> Separator
    lines = re.split(r"\r?\n", script_result)
    try:
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
    except Exception as e:
        logger.exception(e)
    # TODO: probably need to add shouldWaitForPhaser
    return separators


def recurse_frames(frame_data):
    if not frame_data:
        return ""


def efficient_string_replace(ref_id_open_token, ref_id_end_token, input, replacements):
    if not replacements:
        return input


def get_frame_dom(driver):
    # type: (EyesWebDriver) -> Dict
    script_result = eyes_selenium_utils.get_dom_script_result(
        driver,
        DOM_EXTRACTION_TIMEOUT,
        "DomCapture_StopWatch",
        _CAPTURE_FRAME_SCRIPT + "return __captureDomAndPoll();",
    )
    missing_css = []
    missing_frames = []
    data = []
    separators = _parse_script_result(script_result, missing_css, missing_frames, data)

    # TODO: add fetch css func
    # fetch_css_files(missing_css)
    frame_data = recurse_frames(missing_frames)
    return efficient_string_replace(
        separators.iframe_start_token, separators.iframe_end_token, data[0], frame_data
    )


@datetime_utils.timeit
def get_full_window_dom(driver, return_as_dict=False):
    # type: (EyesWebDriver, bool) -> tp.Union[str, dict]
    current_root_element = eyes_selenium_utils.curr_frame_scroll_root_element(driver)

    with eyes_selenium_utils.get_and_restore_state(
        ScrollPositionProvider(driver, current_root_element)
    ):
        logger.debug("Traverse DOM Tree")
        script_result = get_frame_dom(driver)

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
