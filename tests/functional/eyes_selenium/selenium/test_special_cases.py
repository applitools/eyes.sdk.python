import pytest
from selenium.webdriver.common.by import By

from applitools.selenium import StitchMode, Target

pytestmark = [
    pytest.mark.platform("Linux", "Windows", "macOS"),
    pytest.mark.viewport_size({"width": 700, "height": 460}),
    pytest.mark.test_suite_name("Eyes Selenium SDK - Special Cases"),
    pytest.mark.test_page_url(
        "http://applitools.github.io/demo/TestPages/WixLikeTestPage/index.html"
    ),
    pytest.mark.parametrize(
        "eyes",
        [dict(stitch_mode=StitchMode.CSS), dict(stitch_mode=StitchMode.Scroll)],
        indirect=True,
    ),
]


def test_check_region_in_a_very_big_frame(eyes_opened):
    eyes_opened.check("map", Target.frame("frame1").region([By.TAG_NAME, "img"]))


def test_check_region_in_a_very_big_frame_after_manual_switch_frame(eyes_opened):
    eyes_opened.driver.switch_to.frame("frame1")

    element = eyes_opened.driver.find_element(By.CSS_SELECTOR, "img")
    eyes_opened.driver.execute_script(
        "arguments[0].scrollIntoView(true);", element.element
    )
    eyes_opened.check("", Target.region([By.CSS_SELECTOR, "img"]))
