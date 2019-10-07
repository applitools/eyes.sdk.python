import pytest

from applitools.selenium import StitchMode, Target

pytestmark = [
    pytest.mark.platform("Linux", "Windows", "macOS"),
    pytest.mark.viewport_size({"width": 700, "height": 460}),
    pytest.mark.test_suite_name("Eyes Selenium SDK - Page With Header"),
    pytest.mark.test_page_url(
        "https://applitools.github.io/demo/TestPages/PageWithHeader/index.html"
    ),
    pytest.mark.parametrize(
        "eyes",
        [dict(stitch_mode=StitchMode.CSS), dict(stitch_mode=StitchMode.Scroll)],
        indirect=True,
    ),
]


def test_check_page_with_header__window(eyes_opened):
    eyes_opened.check("Page with header", Target.window().fully(False))


def test_check_page_with_header__window__fully(eyes_opened):
    eyes_opened.check("Page with header - fully", Target.window().fully(True))


def test_check_page_with_header__region(eyes_opened):
    eyes_opened.check("Page with header", Target.region("div.page").fully(False))


def test_check_page_with_header__region__fully(eyes_opened):
    eyes_opened.check("Page with header - fully", Target.region("div.page").fully(True))
