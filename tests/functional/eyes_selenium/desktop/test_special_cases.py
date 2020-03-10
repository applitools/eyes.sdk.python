import pytest
from selenium.webdriver.common.by import By

from applitools.selenium import Target

pytestmark = [
    pytest.mark.selenium_only,
    pytest.mark.platform("Linux"),
    pytest.mark.viewport_size({"width": 700, "height": 460}),
    pytest.mark.test_suite_name("Eyes Selenium SDK - Special Cases"),
    pytest.mark.test_page_url(
        "http://applitools.github.io/demo/TestPages/WixLikeTestPage/index.html"
    ),
]


def test_check_region_in_a_very_big_frame(eyes_opened):
    eyes_opened.check("map", Target.frame("frame1").region([By.TAG_NAME, "img"]))


def test_check_region_in_a_very_big_frame_after_manual_switch_to_frame(eyes_opened):
    eyes_opened.driver.switch_to.frame("frame1")

    element = eyes_opened.driver.find_element_by_tag_name("img")
    eyes_opened.driver.execute_script(
        "arguments[0].scrollIntoView(true);", element.element
    )
    eyes_opened.check("", Target.region([By.CSS_SELECTOR, "img"]))
