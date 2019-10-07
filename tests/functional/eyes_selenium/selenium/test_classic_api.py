import pytest
from selenium.webdriver.common.by import By

from applitools.selenium import StitchMode

pytestmark = [
    pytest.mark.platform("Linux", "Windows", "macOS"),
    pytest.mark.viewport_size({"width": 700, "height": 460}),
    pytest.mark.test_suite_name("Eyes Selenium SDK - Classic API"),
    pytest.mark.test_page_url(
        "http://applitools.github.io/demo/TestPages/FramesTestPage/"
    ),
    pytest.mark.parametrize(
        "eyes_opened",
        [dict(stitch_mode=StitchMode.CSS), dict(stitch_mode=StitchMode.Scroll)],
        indirect=True,
    ),
]


def test_check_window(eyes_opened):
    eyes_opened.check_window("Window")


def test_check_window_fully(eyes_opened):
    eyes_opened.check_window("Full Window", fully=True)


def test_check_window_viewport(eyes_opened):
    eyes_opened.check_window("Viewport Window")


def test_check_region(eyes_opened):
    eyes_opened.check_region(
        [By.ID, "overflowing-div"], tag="Region", stitch_content=True
    )


def test_check_region2(eyes_opened):
    eyes_opened.check_region(
        [By.ID, "overflowing-div-image"], tag="minions", stitch_content=True
    )


def test_check_frame(eyes_opened):
    eyes_opened.check_frame("frame1", tag="frame1")


def test_check_region_in_frame(eyes_opened):
    eyes_opened.check_region_in_frame(
        "frame1", [By.ID, "inner-frame-div"], tag="Inner frame div", stitch_content=True
    )


def test_check_inner_frame(eyes_opened):
    eyes_opened.hide_scrollbars = False
    eyes_opened.driver.execute_script("document.documentElement.scrollTo(0,350);")
    eyes_opened.driver.switch_to.default_content()
    eyes_opened.driver.switch_to.frame(
        eyes_opened.driver.find_element_by_name("frame1")
    )
    eyes_opened.check_frame("frame1-1", "inner-frame")
    # TODO: add eyes.logger.log?()
    # eyes_opened.log("Validating (1) ...")
    eyes_opened.check_window("window after check frame")
    # eyes_opened.log("Validating (2) ...")
    inner_frame_body = eyes_opened.driver.find_element_by_tag_name("body")
    eyes_opened.driver.execute_script(
        "arguments[0].style.background='red';", inner_frame_body.element
    )
    eyes_opened.check_window("window after change background color of inner frame")


def test_check_window_after_scroll(eyes_opened):
    eyes_opened.driver.execute_script("document.documentElement.scrollTo(0,350);")
    eyes_opened.check_window("viewport after scroll")


def test_double_check_window(eyes_opened):
    eyes_opened.check_window("first")
    eyes_opened.check_window("second")
