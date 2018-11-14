from __future__ import absolute_import

import json
import typing as tp

import requests
import tinycss2
from tinycss2.ast import URLToken

from applitools.eyes_core import logger, Point
from applitools.eyes_core.utils import general_utils
from applitools.eyes_core.utils.compat import urljoin
from applitools.eyes_selenium.positioning import PositionProvider

if tp.TYPE_CHECKING:
    from applitools.eyes_selenium.webdriver import EyesWebDriver

_CAPTURE_CSSOM_SCRIPT = """
function extractCssResources() {
    return Array.from(document.querySelectorAll('link[rel="stylesheet"],style')).map(el => {
        if (el.tagName.toUpperCase() === 'LINK') {
            return "href:" + el.getAttribute('href');
        } else {
            return "text:" + el.textContent;
        }
    });
}

return extractCssResources();
"""
_CAPTURE_FRAME_SCRIPT = """
function captureFrame({styleProps, attributeProps, rectProps, ignoredTagNames}) {
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

return captureFrame(arguments[0]);
"""


def get_full_window_dom(driver, position_provider=None):
    # type: (EyesWebDriver, PositionProvider) -> str
    if position_provider:
        position_provider.push_state()
        position_provider.set_position(Point.create_top_left())

    dom = _get_window_dom(driver)
    dom_json = json.dumps(dom)

    if position_provider:
        position_provider.pop_state()
    return dom_json


def _get_window_dom(driver):
    args_obj = {
        'styleProps': [
            "background-color",
            "background-image",
            "background-size",
            "color",
            "border-width",
            "border-color",
            "border-style",
            "padding",
            "margin"
        ],
        'attributeProps': {
            'all': ['id', 'class'],
            'IMG': ['core'],
            'IFRAME': ['core'],
            'A': ['href']
        },
        'rectProps': [
            "width",
            "height",
            "top",
            "left",
            "bottom",
            "right"
        ],
        'ignoredTagNames': [
            "HEAD",
            "SCRIPT"
        ]
    }
    result = _get_frame_dom(driver, args_obj)
    return result


def _get_frame_dom(driver, args_obj):
    # type: (EyesWebDriver, tp.Dict) -> tp.Dict
    dom_tree = driver.execute_script(_CAPTURE_FRAME_SCRIPT, args_obj)
    base_url = driver.current_url  # type: ignore
    logger.debug('Traverse DOM Tree')
    _traverse_dom_tree(driver, args_obj, dom_tree, -1, base_url)
    return dom_tree


def _traverse_dom_tree(driver, args_obj, dom_tree, frame_index, base_url):
    # type: (EyesWebDriver, dict, dict, int, tp.Text) -> None
    logger.debug('Traverse DOM Tree: index_tree {}'.format(frame_index))

    tag_name = dom_tree.get('tagName', None)  # type: str
    if not tag_name:
        return None

    if frame_index > -1:
        driver.switch_to.frame(frame_index)
        dom = driver.execute_script(_CAPTURE_FRAME_SCRIPT, args_obj)
        dom_tree['childNodes'] = dom

        src_url = None
        attrs_node = dom_tree.get('attributes', None)
        if attrs_node:
            src_url = attrs_node.get('core', None)

        if src_url is None:
            logger.warning('IFRAME WITH NO SRC')

        _traverse_dom_tree(driver, args_obj, dom, -1, src_url)
        driver.switch_to.parent_frame()

    is_html = tag_name.upper() == 'HTML'
    if is_html:
        logger.debug('Traverse DOM Tree: Inside HTML')
        css = _get_frame_bundled_css(driver, base_url)
        dom_tree['css'] = css

    _loop(driver, args_obj, dom_tree, base_url)


def _loop(driver, args_obj, dom_tree, base_url):
    # type: (EyesWebDriver, dict, dict, tp.Text) -> None
    child_nodes = dom_tree.get('childNode', None)  # type: str
    if not child_nodes:
        return None

    index = 0
    for dom_sub_tree in child_nodes:
        if isinstance(dom_sub_tree, dict):
            tag_name = dom_sub_tree.get('tagName', None)
            is_iframe = tag_name.upper() == "IFRAME"
            if is_iframe:
                _traverse_dom_tree(driver, args_obj, dom_sub_tree, index, base_url)
                index += 1


def _get_frame_bundled_css(driver, base_url):
    # type: (EyesWebDriver, tp.Text) -> tp.Text
    if not general_utils.is_absolute_url(base_url):
        logger.warning('Base URL is not an absolute URL!')
    result = driver.execute_script(_CAPTURE_CSSOM_SCRIPT)
    css_string = ''
    for item in result:
        kind = item[0:5]
        value = item[5:]
        css = ''
        if kind == 'text:':
            css = value
        else:
            css = _download_css(base_url, value)

        stylesheet = tinycss2.parse_stylesheet(css, skip_comments=True,
                                               skip_whitespace=True)
        css = _serialize_css(base_url, stylesheet)
        css_string += css

    return css_string


def _serialize_css(base_url, stylesheet):
    # type: (tp.Text, tp.List) -> tp.Text
    css_string = ''
    for node in stylesheet:
        add_as_is = True
        if node.type == 'at-rule' and node.lower_at_keyword == 'import':
            logger.info("encountered @import rule")
            href = None
            for tag in node.prelude:
                if isinstance(tag, URLToken):
                    href = tag.value
            css = _download_css(base_url, href)
            css = css.strip()
            logger.info('imported CSS (whitespaces trimmed) length: {}'.format(len(css)))
            add_as_is = len(css) == 0
            if not add_as_is:
                css_string += css
        if add_as_is:
            css_string += node.serialize()
    return css_string


def _download_css(base_url, value):
    # type: (tp.Text, tp.Text) -> tp.Text
    logger.info("Given URL to download: {}".format(value))
    if (general_utils.is_absolute_url(value) and
            not general_utils.is_url_with_scheme(value)):
        url = urljoin('http://', value)
    else:
        url = urljoin(base_url, value)
    logger.info("Download CSS from {}".format(url))
    return requests.get(url).text
