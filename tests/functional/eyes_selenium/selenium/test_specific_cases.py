import pytest
from selenium.webdriver.common.by import By

from applitools.selenium import Region, StitchMode, Target


@pytest.mark.platform("Linux")
@pytest.mark.test_page_url("https://applitools.com/helloworld")
def test_quickstart_example(eyes, driver):
    required_viewport = {"width": 1200, "height": 800}
    eyes.set_viewport_size(driver, required_viewport)
    eyes.open(
        driver=driver,
        app_name="TestQuickstartExample",
        test_name="My first Selenium Python test!",
        viewport_size={"width": 800, "height": 600},
    )

    eyes.check_window("Hello!")

    driver.find_element_by_css_selector("button").click()
    eyes.check_window("Click!")

    eyes.check_region(Region(20, 20, 50, 50), "step")

    eyes.close()


@pytest.mark.browser("chrome")
@pytest.mark.platform("Linux")
def test_directly_set_viewport_size(eyes, driver):
    required_viewport = {"width": 800, "height": 600}
    eyes.set_viewport_size(driver, required_viewport)
    driver = eyes.open(driver, "Python SDK", "TestViewPort-DirectlySetViewportt")
    assert required_viewport == eyes.get_viewport_size(driver)
    eyes.close()


@pytest.mark.browser("chrome")
@pytest.mark.platform("Linux")
@pytest.mark.eyes_config(hide_scrollbars=True)
@pytest.mark.test_page_url("http://applitools.github.io/demo/TestPages/FramesTestPage/")
def test_check_window_with_send_dom(eyes, driver):
    eyes.open(
        driver,
        "Eyes Selenium SDK - Fluent API",
        "TestCheckWindowWithSendDom",
        {"width": 800, "height": 600},
    )
    driver.find_element_by_tag_name("input").send_keys("My Input")
    eyes.check(
        "Fluent - Window with Ignore region",
        Target.window().send_dom().use_dom().ignore_caret(),
    )
    assert "data-applitools-scroll" in driver.page_source
    assert "data-applitools-original-overflow" in driver.page_source
    eyes.close()


@pytest.mark.test_page_url("https://demo.applitools.com/")
def test_abort_eyes(eyes, driver):
    eyes.open(driver, "Python | VisualGrid", "TestAbortSeleniumEyes")
    eyes.check_window()
    eyes.abort()


@pytest.mark.platform("Linux")
@pytest.mark.test_page_url("https://applitools.com/helloworld")
def test_coordinates_resolving(eyes, driver):
    driver = eyes.open(
        driver,
        "Python Selenium",
        "TestCoordinatesResolving",
        {"width": 800, "height": 600},
    )
    element = driver.find_element_by_css_selector("button")
    left = element.location["x"]
    top = element.location["y"]
    width = element.size["width"]
    height = element.size["height"]

    eyes.check("web element", Target.region(element))
    eyes.check("coordinates", Target.region(Region(left, top, width, height)))

    eyes.close()


@pytest.mark.parametrize(
    "eyes",
    [
        {"force_full_page_screenshot": True, "stitch_mode": StitchMode.CSS},
        {"force_full_page_screenshot": False, "stitch_mode": StitchMode.CSS},
        {"force_full_page_screenshot": True, "stitch_mode": StitchMode.Scroll},
        {"force_full_page_screenshot": False, "stitch_mode": StitchMode.Scroll},
    ],
    indirect=True,
    ids=lambda o: "CSS" if o["stitch_mode"] == StitchMode.CSS else "Scroll",
)
@pytest.mark.platform("Windows")
@pytest.mark.browser("internet explorer")
@pytest.mark.test_page_url("http://applitools.github.io/demo/TestPages/FramesTestPage")
def test_ie_viewport_screenshot_with_scrolling(eyes, driver):
    test_name = "TestIEViewportScreenshot"
    if eyes.force_full_page_screenshot:
        test_name += "_FPS"
    test_name += "_%s" % eyes.stitch_mode.value
    eyes.open(driver, "Python SDK", test_name)

    eyes.check_window()

    driver.execute_script(
        "arguments[0].scrollIntoView();",
        driver.find_element_by_id("overflowing-div-image"),
    )
    eyes.check_window()
    eyes.close()


@pytest.mark.test_page_url("http://applitools.github.io/demo/TestPages/FramesTestPage/")
def test_switch_back_to_frame_after_check(eyes, driver):
    eyes_driver = eyes.open(
        driver,
        "Python Selenium",
        "TestSwitchBackToFrameAfterCheck",
        {"width": 800, "height": 600},
    )

    # switch driver context to frame
    frame = driver.find_element_by_css_selector("body > iframe")
    eyes_driver.switch_to.frame(frame)

    # locate element inside the frame - succeed
    eyes_driver.find_element_by_css_selector("#inner-frame-div")

    # take screenshot
    eyes.check("step name", Target.window())

    # locate the same element inside the frame - failed
    eyes_driver.find_element_by_css_selector("#inner-frame-div")
    eyes.close()


@pytest.mark.test_page_url("http://applitools.github.io/demo/TestPages/FramesTestPage/")
def test_region_selector_in_check_fluent_interface(eyes, driver):
    eyes_driver = eyes.open(
        driver,
        "Python Selenium",
        "TestRegionSelectorInCheckFluentInterface",
        {"width": 800, "height": 600},
    )
    eyes.check("By CSS Selector", Target.region([By.CSS_SELECTOR, "#overflowing-div"]))
    eyes.check("By XPATH", Target.region([By.XPATH, '//*[@id="overflowing-div"]']))
    eyes.close()
