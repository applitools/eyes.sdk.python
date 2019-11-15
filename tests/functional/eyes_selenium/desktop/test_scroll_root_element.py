import pytest

from applitools.selenium import Target

pytestmark = [
    pytest.mark.platform("Linux", "Windows", "macOS"),
    pytest.mark.viewport_size({"width": 700, "height": 460}),
    pytest.mark.test_suite_name("Eyes Selenium SDK - Scroll Root Element"),
]


@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/SimpleTestPage/index.html"
)
def test_check_window__simple__body(eyes_opened):
    eyes_opened.check(
        "Body ({}) stitching".format(eyes_opened.stitch_mode.value),
        Target.window().scroll_root_element("body").fully(),
    )


@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/SimpleTestPage/index.html"
)
def test_check_window__simple__html(eyes_opened):
    eyes_opened.check(
        "Html ({}) stitching".format(eyes_opened.stitch_mode.value),
        Target.window().scroll_root_element("html").fully(),
    )


@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/SimpleTestPage/scrollablebody.html"
)
def test_check_window__html(eyes_opened):
    eyes_opened.check(
        "Html ({}) stitching".format(eyes_opened.stitch_mode.value),
        Target.window().scroll_root_element("html").fully(),
    )


@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/SimpleTestPage/scrollablebody.html"
)
def test_check_window__body(eyes_opened):
    eyes_opened.check(
        "Body ({}) stitching".format(eyes_opened.stitch_mode.value),
        Target.window().scroll_root_element("body").fully(),
    )
