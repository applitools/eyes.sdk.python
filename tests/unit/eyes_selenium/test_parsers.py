from applitools.selenium import parsers

from os import path

tests_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))


def get_resource(name):
    resource_dir = path.join(tests_dir, "resources")
    pth = path.join(resource_dir, name)
    with open(pth, "rb") as f:
        return f.read()


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
