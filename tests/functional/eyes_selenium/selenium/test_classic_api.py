import pytest
from selenium.webdriver.common.by import By

from applitools.selenium import StitchMode


@pytest.mark.platform("Linux", "Windows", "macOS")
@pytest.mark.usefixtures("eyes_for_class")
@pytest.mark.viewport_size({"width": 700, "height": 460})
@pytest.mark.eyes(stitch_mode=StitchMode.CSS)
@pytest.mark.test_page_url("http://applitools.github.io/demo/TestPages/FramesTestPage/")
@pytest.mark.test_suite_name("Eyes Selenium SDK - Classic API")
class TestClassicAPI(object):
    def test_check_window(self):
        self.eyes.check_window("Window")

    def test_check_window_fully(self):
        self.eyes.check_window("Full Window", fully=True)

    def test_check_window_viewport(self):
        self.eyes.check_window("Viewport Window")

    def test_check_region(self):
        self.eyes.check_region(
            [By.ID, "overflowing-div"], tag="Region", stitch_content=True
        )

    def test_check_region2(self):
        self.eyes.check_region(
            [By.ID, "overflowing-div-image"], tag="minions", stitch_content=True
        )

    def test_check_frame(self):
        self.eyes.check_frame("frame1", tag="frame1")

    def test_check_region_in_frame(self):
        self.eyes.check_region_in_frame(
            "frame1",
            [By.ID, "inner-frame-div"],
            tag="Inner frame div",
            stitch_content=True,
        )

    def test_check_inner_frame(self):
        self.eyes.hide_scrollbars = False
        self.driver.execute_script("document.documentElement.scrollTo(0,350);")
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(self.driver.find_element_by_name("frame1"))
        self.eyes.check_frame("frame1-1", "inner-frame")
        # TODO: add eyes.logger.log?()
        # self.eyes.log("Validating (1) ...")
        self.eyes.check_window("window after check frame")
        # self.eyes.log("Validating (2) ...")
        inner_frame_body = self.driver.find_element_by_tag_name("body")
        self.driver.execute_script(
            "arguments[0].style.background='red';", inner_frame_body
        )
        self.eyes.check_window("window after change background color of inner frame")

    def test_check_window_after_scroll(self):
        self.driver.execute_script("document.documentElement.scrollTo(0,350);")
        self.eyes.check_window("viewport after scroll")

    def test_double_check_window(self):
        self.eyes.check_window("first")
        self.eyes.check_window("second")
