from __future__ import absolute_import, unicode_literals

import json
import typing as tp
from collections import OrderedDict
from concurrent.futures.thread import ThreadPoolExecutor

import requests
import tinycss2

from applitools.common import logger
from applitools.common.utils import datetime_utils, general_utils
from applitools.common.utils.compat import urljoin
from applitools.selenium import eyes_selenium_utils
from applitools.selenium.positioning import ScrollPositionProvider

if tp.TYPE_CHECKING:
    from applitools.selenium.webdriver import EyesWebDriver

__all__ = ("get_full_window_dom",)
_CAPTURE_CSSOM_SCRIPT = """
function extractCssResources() {
    cssAndText = Array.from(document.querySelectorAll(
    'link[rel="stylesheet"],style')).map(el => {
        if (el.tagName.toUpperCase() === 'LINK') {
            return [null, el.getAttribute('href')];
        } else {
            return [el.textContent, null];
        }
    });
    return cssAndText
}
return extractCssResources();
"""
_CAPTURE_FRAME_SCRIPT = """
function captureFrame({ styleProps, attributeProps, rectProps, ignoredTagNames }) {
  const NODE_TYPES = {
    ELEMENT: 1,
    TEXT: 3,
  };

  function filter(x) {
    return !!x;
  }

  function notEmptyObj(obj) {
    return Object.keys(obj).length ? obj : undefined;
  }

  function iframeToJSON(el) {
    const obj = elementToJSON(el);
    try {
      if (el.contentDocument) {
        obj.childNodes = [captureNode(el.contentDocument.documentElement)];
      }
    } catch (ex) {
    } finally {
      return obj;
    }
  }

  function elementToJSON(el) {
    const tagName = el.tagName.toUpperCase();
    if (ignoredTagNames.indexOf(tagName) > -1) return null;
    const computedStyle = window.getComputedStyle(el);
    const boundingClientRect = el.getBoundingClientRect();

    const style = {};
    for (const p of styleProps) style[p] = computedStyle.getPropertyValue(p);

    const rect = {};
    for (const p of rectProps) rect[p] = boundingClientRect[p];

    const attributes = {};

    if (!attributeProps) {
      if (el.hasAttributes()) {
        var attrs = el.attributes;
        for (const p of attrs) {
          attributes[p.name] = p.value;
        }
      }
    }
    else {
      if (attributeProps.all) {
        for (const p of attributeProps.all) {
          if (el.hasAttribute(p)) attributes[p] = el.getAttribute(p);
        }
      }

      if (attributeProps[tagName]) {
        for (const p of attributeProps[tagName]) {
          if (el.hasAttribute(p)) attributes[p] = el.getAttribute(p);
        }
      }
    }
    return {
      tagName,
      style: notEmptyObj(style),
      rect: notEmptyObj(rect),
      attributes: notEmptyObj(attributes),
      childNodes: Array.prototype.map.call(el.childNodes, captureNode).filter(filter),
    };
  }

  function captureTextNode(node) {
    return {
      tagName: '#text',
      text: node.textContent,
    };
  }

  function captureNode(node) {
    switch (node.nodeType) {
      case NODE_TYPES.TEXT:
        return captureTextNode(node);
      case NODE_TYPES.ELEMENT:
        if (node.tagName.toUpperCase() === 'IFRAME') {
          return iframeToJSON(node);
        } else {
          return elementToJSON(node);
        }
      default:
        return null;
    }
  }

  return captureNode(document.documentElement);
}

return JSON.stringify(captureFrame(arguments[0]));
"""
_ARGS_OBJ = {
    "styleProps": [
        "background-color",
        "background-image",
        "background-size",
        "color",
        "border-width",
        "border-color",
        "border-style",
        "padding",
        "margin",
    ],
    "attributeProps": None,
    "rectProps": ["width", "height", "top", "left"],
    "ignoredTagNames": ["HEAD", "SCRIPT"],
}
CSS_DOWNLOAD_TIMEOUT = 3  # Secs


@datetime_utils.timeit
def get_full_window_dom(driver, return_as_dict=False):
    # type: (EyesWebDriver, bool) -> tp.Union[str, dict]

    dom_tree = json.loads(
        driver.execute_script(_CAPTURE_FRAME_SCRIPT, _ARGS_OBJ),
        object_pairs_hook=OrderedDict,
    )
    current_root_element = eyes_selenium_utils.curr_frame_scroll_root_element(driver)

    with eyes_selenium_utils.get_and_restore_state(
        ScrollPositionProvider(driver, current_root_element)
    ):
        logger.debug("Traverse DOM Tree")
        _traverse_dom_tree(driver, {"childNodes": [dom_tree], "tagName": "OUTER_HTML"})

    if return_as_dict:
        return dom_tree

    return json.dumps(dom_tree)


class DomNode(object):
    __slots__ = ("tag_name", "child_nodes", "is_html", "is_iframe")

    def __init__(self, tag_name, child_nodes):
        # type: (tp.Text, tp.List) -> None
        self.tag_name = tag_name
        self.child_nodes = child_nodes
        self.is_html = bool(self.tag_name == "HTML")
        self.is_iframe = bool(self.tag_name == "IFRAME")

    @classmethod
    def create_from_dom_tree(cls, node):
        # type: (tp.Dict) -> DomNode
        tag_name = node.get("tagName", "").upper()
        child_nodes = node.get("childNodes", [])
        return cls(tag_name, child_nodes)


def _traverse_dom_tree(driver, dom_tree):
    # type: (EyesWebDriver, tp.Dict) -> None
    """
    Walk through all IFRAMEs and add CSS to them
    """
    node = DomNode.create_from_dom_tree(dom_tree)
    if not node.tag_name:
        return None
    for index, sub_dom_tree in enumerate(_loop(driver, dom_tree)):
        # Reduce recursion optimization. Save from extra _loop calls
        if not sub_dom_tree["childNodes"]:
            continue
        with driver.switch_to.frame_and_back(index):
            _traverse_dom_tree(driver, sub_dom_tree)


def _loop(driver, dom_tree):
    # type: (EyesWebDriver, tp.Dict) -> tp.Iterable
    node = DomNode.create_from_dom_tree(dom_tree)
    if not node.child_nodes:
        return []

    def iterate_child_nodes(child_nodes):
        for sub_dom_tree in child_nodes:
            sub_node = DomNode.create_from_dom_tree(sub_dom_tree)
            if sub_node.is_iframe:
                yield sub_dom_tree
                continue

            if sub_node.is_html:
                sub_dom_tree["css"] = _get_frame_bundled_css(driver)
            if sub_node.child_nodes:
                # yield from iterate_child_nodes() in python 3
                for sub in iterate_child_nodes(sub_node.child_nodes):
                    yield sub

    return iterate_child_nodes(node.child_nodes)


@datetime_utils.timeit
def _get_frame_bundled_css(driver):
    # type: (EyesWebDriver) -> tp.Text
    base_url = driver.current_url  # type: ignore
    if not general_utils.is_absolute_url(base_url):
        logger.info("Base URL is not an absolute URL!")

    cssom_results = driver.execute_script(_CAPTURE_CSSOM_SCRIPT)
    raw_css_nodes = [
        CssNode.create(base_url, css_href, css_text)
        for css_text, css_href in cssom_results
    ]

    if len(raw_css_nodes) > 5:
        with ThreadPoolExecutor() as executor:
            results = executor.map(_process_raw_css_node, raw_css_nodes)
    else:
        results = [_process_raw_css_node(node) for node in raw_css_nodes]
    return "".join(results)


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
            if minimize:
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
    if general_utils.is_absolute_url(
        value
    ) and not general_utils.is_url_with_scheme(  # noqa
        value
    ):
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
