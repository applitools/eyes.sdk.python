from typing import TYPE_CHECKING

import tinycss2

from applitools.common import logger
from applitools.common.utils import urlparse

if TYPE_CHECKING:
    from typing import List, Text


def _url_from_tags(tags):
    for tag in tags:
        if tag.type == "url":
            try:
                url = urlparse(tag.value)
                if url.scheme in ["http", "https"]:
                    yield url.geturl()
            except Exception as e:
                logger.exception(e)


def get_urls_from_css_resource(bytes_text):
    # type: (bytes) -> List[Text]
    def is_import_node(n):
        return n.type == "at-rule" and n.lower_at_keyword == "import"

    def is_font_node(n):
        return n.type == "at-rule" and n.lower_at_keyword == "font-face"

    try:
        rules, encoding = tinycss2.parse_stylesheet_bytes(
            css_bytes=bytes_text, skip_comments=True, skip_whitespace=True
        )
    except Exception:
        logger.error("Failed to read CSS string")
        return []
    urls = []
    for rule in rules:
        tags = rule.content
        if is_import_node(rule):
            logger.debug("The node has @import")
            tags = rule.prelude
        if is_font_node(rule):
            logger.debug("The node has @font-face")
            tags = rule.content
        if tags:
            urls.extend(list(_url_from_tags(tags)))
    return urls
