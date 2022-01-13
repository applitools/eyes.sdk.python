import time

import pytest

from applitools.selenium import Eyes, Region, StitchMode, Target


@pytest.mark.skip("Old test. test_hello_world implemented instead of this one")
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


@pytest.mark.test_page_url("data:text/html,<p>Test</p>")
def test_abort_eyes(eyes, driver):
    eyes.open(driver, "Test Abort", "Test Abort", {"width": 1200, "height": 800})
    eyes.check("SEL", Target.window())
    time.sleep(15)
    eyes.abort()


@pytest.mark.platform("Linux")
@pytest.mark.test_page_url("https://applitools.com/helloworld")
@pytest.mark.eyes_config(branch_name="master_python")
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


@pytest.mark.test_page_url("http://applitools.github.io/demo/TestPages/FramesTestPage/")
@pytest.mark.eyes_config(parent_branch_name="master", branch_name="master_python")
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


def test_capture_element_on_pre_scrolled_down_page(eyes, driver):
    driver.get(
        "http://applitools.github.io/demo/TestPages/FramesTestPage/longframe.html"
    )
    eyes.open(
        driver=driver,
        app_name="Applitools Eyes SDK",
        test_name="Test capture element on pre scrolled down page",
        viewport_size={"width": 800, "height": 600},
    )
    driver.execute_script("window.scrollTo(0, 300)")
    eyes.check("Row 10", Target.region("body > table > tr:nth-child(10)"))
    eyes.check("Row 20", Target.region("body > table > tr:nth-child(20)"))
    eyes.close()
