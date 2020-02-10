from applitools.selenium import parsers

from tests.utils import get_resource


def test_parse_valid_svg():
    content = get_resource("chevron.svg")
    parsers.get_urls_from_svg_resource(content)


def test_parse_valid_svg_with_links():
    content = get_resource("applitools_logo_combined.svg")
    urls = parsers.get_urls_from_svg_resource(content)
    assert urls == ["slogan.svg", "logo.svg", "company_name.png"]


def test_parse_valid_svg_with_bom():
    content = get_resource("ios.svg")
    parsers.get_urls_from_svg_resource(content)


def test_parse_invalid_svg_with_comment_on_top():
    content = get_resource("fa-regular-400.svg")
    parsers.get_urls_from_svg_resource(content)
