import pytest

from applitools.selenium import Target

pytestmark = [
    pytest.mark.platform("Linux"),
    pytest.mark.test_suite_name("Eyes Selenium SDK - Page With Header"),
    pytest.mark.viewport_size({"width": 700, "height": 460}),
    pytest.mark.test_page_url(
        "https://applitools.github.io/demo/TestPages/PageWithHeader/index.html"
    ),
]


def test_check_page_with_header__window(eyes_opened):
    eyes_opened.check("Page with header", Target.window().fully(False))


def test_check_page_with_header__window__fully(eyes_opened):
    eyes_opened.check("Page with header - fully", Target.window().fully(True))


def test_check_page_without_header__region(eyes_opened):
    eyes_opened.check(
        "Region without the header", Target.region("div.page").fully(False)
    )


def test_check_page_without_header__region__fully(eyes_opened):
    eyes_opened.check(
        "Region without the header - fully", Target.region("div.page").fully(True)
    )
