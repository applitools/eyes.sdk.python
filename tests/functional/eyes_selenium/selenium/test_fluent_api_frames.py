import pytest
from selenium.webdriver.common.by import By

from applitools.selenium import Region, StitchMode, Target


@pytest.mark.platform("Linux", "Windows", "macOS")
@pytest.mark.usefixtures("eyes_for_class")
@pytest.mark.viewport_size({"width": 700, "height": 460})
@pytest.mark.eyes(stitch_mode=StitchMode.CSS)
@pytest.mark.test_suite_name("Eyes Selenium SDK - Fluent API")
@pytest.mark.test_page_url("http://applitools.github.io/demo/TestPages/FramesTestPage/")
class TestFluentAPIFrames(object):
    def test_check_frame__fully__fluent(self):
        self.eyes.check("Fluent - Full Frame", Target.frame("frame1").fully())

    def test_check_frame__fluent(self):
        self.eyes.hide_scrollbars = False
        self.eyes.check("Fluent - Frame", Target.frame("frame1"))

    def test_check_frame_in_frame__fully__fluent(self):
        self.eyes.check(
            "Fluent - Full Frame in Frame",
            Target.frame("frame1").frame("frame1-1").fully(),
        )

    def test_check_region_in_frame__fluent(self):
        self.eyes.check(
            "Fluent - Region in Frame in Frame",
            Target.frame("frame1").region([By.ID, "inner-frame-div"]).fully(),
        )

    def test_check_region_in_frame_in_frame__fluent(self):
        self.eyes.check(
            "Fluent - Region in Frame in Frame",
            Target.frame("frame1").frame("frame1-1").region("img").fully(),
        )

    def test_check_region_in_frame2__fluent(self):
        self.eyes.check(
            "Fluent - Inner frame div 1",
            Target.frame("frame1")
            .region("#inner-frame-div")
            .fully()
            .timeout(5000)
            .ignore(Region(50, 50, 100, 100)),
        )

        self.eyes.check(
            "Fluent - Inner frame div 2",
            Target.frame("frame1")
            .region("#inner-frame-div")
            .fully()
            .ignore(Region(50, 50, 100, 100))
            .ignore(Region(70, 170, 90, 90)),
        )

        self.eyes.check(
            "Fluent - Inner frame div 3",
            Target.frame("frame1").region("#inner-frame-div").fully().timeout(5000),
        )

        self.eyes.check(
            "Fluent - Inner frame div 4",
            Target.frame("frame1").region("#inner-frame-div").fully(),
        )

        self.eyes.check(
            "Fluent - Full frame with floating region",
            Target.frame("frame1")
            .fully()
            .layout()
            .floating(25, Region(200, 200, 150, 150)),
        )

    def test_check_region_in_frame3__fluent(self):
        self.eyes.check(
            "Fluent - Full frame with floating region",
            Target.frame("frame1")
            .fully()
            .layout()
            .floating(25, Region(200, 200, 150, 150)),
        )

    def test_check_region_by_coordinate_in_frame__fully__fluent(self):
        self.eyes.check(
            "Fluent - Inner frame coordinates",
            Target.frame("frame1").region(Region(30, 40, 400, 1200)).fully(),
        )

    def test_check_region_by_coordinate_in_frame__fluent(self):
        self.eyes.hide_scrollbars = False
        self.eyes.check(
            "Fluent - Inner frame coordinates",
            Target.frame("frame1").region(Region(30, 40, 400, 1200)),
        )

    def test_check_frame_in_frame__fully__fluent2(self):
        self.eyes.check("Fluent - Window", Target.window().fully())
        self.eyes.check(
            "Fluent - Full Frame in Frame 2",
            Target.frame("frame1").frame("frame1-1").fully(),
        )

    def test_manual_switch_frame(self):
        self.driver.switch_to.frame("frame1")
        self.eyes.check("", Target.region("#inner-frame-div"))


@pytest.mark.platform("Linux", "Windows", "macOS")
@pytest.mark.usefixtures("eyes_for_class")
@pytest.mark.viewport_size({"width": 700, "height": 460})
@pytest.mark.eyes(stitch_mode=StitchMode.CSS)
@pytest.mark.test_suite_name("Eyes Selenium SDK - Special Cases")
@pytest.mark.test_page_url(
    "http://applitools.github.io/demo/TestPages/WixLikeTestPage/index.html"
)
class TestSpecialCases(object):
    def test_check_region_in_a_very_big_frame(self):
        self.eyes.check("map", Target.frame("frame1").region([By.TAG_NAME, "img"]))

    def test_check_region_in_a_very_big_frame_after_manual_switch_frame(self):
        self.driver.switch_to.frame("frame1")

        element = self.driver.find_element(By.CSS_SELECTOR, "img")
        self.driver.execute_script(
            "arguments[0].scrollIntoView(true);", element.element
        )
        self.eyes.check("", Target.region([By.CSS_SELECTOR, "img"]))
