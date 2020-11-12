from typing import TYPE_CHECKING, Generator

import tinycss2
from lxml import etree

from applitools.common import logger

if TYPE_CHECKING:
    from typing import List, Text


def _url_from_tags(tags, url_tag_types):
    for tag in tags:
        if tag.type in url_tag_types:
            try:
                yield tag.value
            except Exception as e:
                logger.exception(e)


def get_urls_from_css_resource(bytes_text):
    # type: (bytes) -> List[Text]
    def is_import_node(n):
        return n.prelude and n.type == "at-rule" and n.lower_at_keyword == "import"

    try:
        rules, encoding = tinycss2.parse_stylesheet_bytes(
            css_bytes=bytes_text, skip_comments=True, skip_whitespace=True
        )
    except Exception:
        logger.error("Failed to read CSS string")
        return []
    urls = []
    for rule in rules:
        if is_import_node(rule):
            extracted = _url_from_tags(rule.prelude, ("url", "string"))
        elif rule.content:
            extracted = _url_from_tags(rule.content, ("url",))
        else:
            continue
        urls.extend(list(extracted))
    return urls


def get_urls_from_svg_resource(content):
    # type: (bytes) -> List[Text]
    xmlparser = etree.XMLParser(recover=True, ns_clean=True, remove_comments=True)
    xml = etree.HTML(content, xmlparser)
    root = xml.getroottree()
    nodes = root.xpath(".//*[@href]") + root.xpath(
        ".//*[@xlink:href]", namespaces={"xlink": "http://www.w3.org/1999/xlink"}
    )
    urls_from_svg = []
    for node in nodes:
        # node.attrib could contains href w key with namespace
        key = [key for key in node.attrib.keys() if key.endswith("href")][0]
        url = node.attrib[key]
        if url.startswith("data:") and url.startswith("javascript:"):
            continue
        urls_from_svg.append(url)
    return urls_from_svg


def collect_urls_from_(content_type, content):
    # type: (Text, bytes) -> Generator[Text]
    urls_from_css, urls_from_svg = [], []
    if content_type.startswith("text/css"):
        urls_from_css = get_urls_from_css_resource(content)
    if content_type.startswith("image/svg"):
        urls_from_svg = get_urls_from_svg_resource(content)
    for discovered_url in urls_from_css + urls_from_svg:
        if discovered_url.startswith("data:") or discovered_url.startswith("#"):
            # resource already in blob or not relevant
            continue
        yield discovered_url
