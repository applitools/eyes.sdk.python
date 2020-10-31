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


def test_get_urls_from_css_resource_imports():
    content = b'@import "1.css";@import url(2.css);@import url("3.css")'

    urls = parsers.get_urls_from_css_resource(content)

    assert urls == ["1.css", "2.css", "3.css"]


def test_get_urls_from_css_resource_fonts():
    content = b"""@font-face {
    font-family: "A";
    src: url(1);
    src: url("2") format("f1"), url("3") format("f2");}"""

    urls = parsers.get_urls_from_css_resource(content)

    assert urls == ["1", "2", "3"]


def test_get_urls_from_css_resource_background_img():
    content = b'p {background-image: url("1");} a {background-image: url(2);}'

    urls = parsers.get_urls_from_css_resource(content)

    assert urls == ["1", "2"]
