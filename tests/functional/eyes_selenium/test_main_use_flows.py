import pytest
from applitools.selenium import Region, Target
from selenium.webdriver.common.by import By


@pytest.mark.platform("Linux", "Windows", "macOS")
@pytest.mark.usefixtures("eyes_for_class")
@pytest.mark.parametrize(
    "eyes",
    [{"force_full_page_screenshot": True}, {"force_full_page_screenshot": False}],
    indirect=True,
    ids=lambda o: "with FSP" if o["force_full_page_screenshot"] else "no FSP",
)
@pytest.mark.viewport_size({"width": 800, "height": 600})
@pytest.mark.test_page_url("http://applitools.github.io/demo/TestPages/FramesTestPage/")
class TestSetup(object):
    pass


@pytest.mark.test_suite_name("Eyes Selenium SDK - Classic API")
class TestClassicAPI(TestSetup):
    def test_check_window(self):
        self.eyes.check_window(tag="Window")

    def test_check_region(self):
        self.eyes.check_region_by_selector(
            By.ID, "overflowing-div", tag="Region", stitch_content=True
        )

    @pytest.mark.skip("Not implemented yet")
    def test_check_frame(self):
        self.eyes.check_frame("frame1", "frame1", stitch_content=True)

    def test_check_region_in_frame(self):
        self.eyes.check_region_in_frame_by_selector(
            "frame1",
            By.ID,
            "inner-frame-div",
            tag="Inner frame div",
            stitch_content=True,
        )

    def test_check_region2(self):
        self.eyes.check_region_by_selector(
            By.ID, "overflowing-div-image", tag="minions", stitch_content=True
        )


@pytest.mark.skip("Not implemented yet")
@pytest.mark.test_suite_name("Eyes Selenium SDK - Fluent API")
class TestFluentAPI(TestSetup):
    def test_check_window_with_ignore_region_fluent(self):
        self.eyes.check(
            "Fluent - Window with Ignore region", Target.window()
        ).fully().timeout(5000).ignore(Region(left=50, top=50, width=100, height=100))

    def test_check_region_with_ignore_region_fluent(self):
        self.eyes.check(
            "Fluent - Region with Ignore region",
            Target.region(By.ID, "overflowing-div"),
        ).ignore(Region(left=50, top=50, width=100, height=100))

    def test_check_frame_fully_fluent(self):
        self.eyes.check("Fluent - Full Frame", Target.frame("frame1").fully())

    def test_check_frame_fluent(self):
        self.eyes.check("Fluent - Frame", Target.frame("frame1"))

    def test_check_frame_in_frame_fully_fluent(self):
        self.eyes.check(
            "Fluent - Full Frame in Frame",
            Target.frame("frame1").frame("frame1-1").fully(),
        )

    def test_check_region_in_frame_fluent(self):
        self.eyes.check(
            "Fluent - Region in Frame in Frame",
            Target.frame("frame1").frame("frame1-1").region(By.TAG_NAME, "img").fully(),
        )

    def test_check_frame_in_frame_fully_fluent2(self):
        self.eyes.check("Fluent - Window with Ignore region 2", Target.window().fully())
        self.eyes.check(
            "Fluent - Full Frame in Frame 2",
            Target.frame("frame1").frame("frame1-1").fully(),
        )

    def test_check_window_with_ignore_by_selector_fluent(self):
        self.eyes.check(
            "Fluent - Window with ignore region by selector",
            Target.window().ignore(By.ID, "overflowing-div"),
        )

    def test_check_window_with_floating_by_selector_fluent(self):
        self.eyes.check(
            "Fluent - Window with floating region by selector",
            Target.window().floating(By.ID, "overflowing-div", 3, 3, 20, 30),
        )

    def test_check_window_with_floating_by_region_fluent(self):
        self.eyes.check(
            "Fluent - Window with floating region by selector",
            Target.window().floating(By.ID, "overflowing-div", 3, 3, 20, 30),
        )

    def test_check_element_fully_fluent(self):
        element = self.driver.find_element(By.ID, "overflowing-div-image")
        self.eyes.check(
            "Fluent - Region by element - fully", Target.region(element).fully()
        )

    def test_check_element_with_ignore_region_by_element_fluent(self):
        element = self.driver.find_element(By.ID, "overflowing-div-image")
        ignore_element = self.driver.find_element(By.ID, "overflowing-div")
        self.eye.check(
            "Fluent - Region by element - fully",
            Target.region(element).ignore(ignore_element),
        )

    def test_check_element_fluent(self):
        element = self.driver.find_element(By.ID, "overflowing-div-image")
        self.eyes.check("Fluent - Region by element", Target.region(element))


@pytest.mark.skip("Depending on Fluent API. Not implemented yet")
@pytest.mark.test_suite_name("Eyes Selenium SDK - Special Cases")
@pytest.mark.test_page_url(
    "http://applitools.github.io/demo/TestPages/WixLikeTestPage/index.html"
)
class TestSpecialCases(TestSetup):
    def test_check_region_in_a_very_big_frame(self):
        self.eyes.check("map", Target.frame("frame1").region(By.TAG_NAME, "img"))

    def test_check_region_in_a_very_big_frame_after_manual_switch_frame(self):
        with self.driver.switch_to.frame_and_back("frame1"):
            element = self.driver.find_element(By.CSS_SELECTOR, "img")
            # TODO #112: fix bug execute_script method calling with EyesWebElement
            self.driver.execute_script(
                "arguments[0].scrollIntoView(true);", element.element
            )
            self.eyes.check("", Target.region(By.CSS_SELECTOR, "img"))


@pytest.mark.skip("Not runnable in java sdk")
@pytest.mark.test_suite_name("Eyes Selenium SDK - ElementsFrames")
class ElementsFramesTest(TestSetup):
    def test_home1(self):
        self.driver.get("https://astappev.github.io/test-html-pages/")
        self.eyes.check_window("Initial")
        element = self.driver.find_element(By.ID, "overflowing-div")
        self.eyes.check_region_by_element(element, "Initial")

        self.eyes.check_region_in_frame_by_selector(
            "frame1", By.ID, "inner-frame-div", "Inner frame div"
        )

        element = self.driver.find_element(By.ID, "overflowing-div-image")
        self.eyes.check_region_by_element(element, "minions")

    def test_playbuzz(self):
        self.driver.get(
            "http://alpha.playbuzz.com/plabuzz1010/automation-test-story-default"
        )
        self.driver.find_element(
            By.CSS_SELECTOR,
            "#pb-story > pb-story > div > div.bottom-share-bar-container.ng-scope.ng-isolate-scope > button",
        ).click()
        self.eyes.check_region_by_selector(
            By.CSS_SELECTOR,
            "body > div.modal.fade.ng-isolate-scope.embed-modal.in > div > div",
        )
