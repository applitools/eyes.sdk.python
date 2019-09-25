import os

import pytest

from applitools.selenium import Region, StitchMode, Target


@pytest.mark.platform("Linux")
def test_quickstart_example(eyes, driver):
    required_viewport = {"width": 1200, "height": 800}
    eyes.set_viewport_size_static(driver, required_viewport)
    eyes.open(
        driver=driver,
        app_name="TestQuickstartExample",
        test_name="My first Selenium Python test!",
        viewport_size={"width": 800, "height": 600},
    )
    driver.get("https://applitools.com/helloworld")

    eyes.check_window("Hello!")

    driver.find_element_by_css_selector("button").click()
    eyes.check_window("Click!")

    eyes.check_region(Region(20, 20, 50, 50), "step")

    eyes.close()


@pytest.mark.browser("chrome")
@pytest.mark.platform("Linux")
def test_directly_set_viewport_size(eyes, driver):
    required_viewport = {"width": 800, "height": 600}
    eyes.set_viewport_size_static(driver, required_viewport)
    driver = eyes.open(driver, "Python SDK", "TestViewPort-DirectlySetViewportt")
    assert required_viewport == eyes.get_viewport_size_static(driver)
    eyes.close()


@pytest.mark.platform("Linux")
@pytest.mark.eyes(hide_scrollbars=True)
def test_check_window_with_send_dom(eyes, driver):
    eyes.open(
        driver,
        "Eyes Selenium SDK - Fluent API",
        "TestCheckWindowWithSendDom",
        {"width": 800, "height": 600},
    )
    driver.get("http://applitools.github.io/demo/TestPages/FramesTestPage/")
    driver.find_element_by_tag_name("input").send_keys("My Input")
    eyes.check(
        "Fluent - Window with Ignore region", Target.window().send_dom().use_dom()
    )
    assert "data-applitools-scroll" in driver.page_source
    assert "data-applitools-original-overflow" in driver.page_source
    eyes.close()


def test_abort_eyes(eyes, driver):
    driver.get("https://demo.applitools.com")
    eyes.open(driver, "Python VisualGrid", "TestAbortSeleniumEyes")
    eyes.check_window()
    eyes.abort()


@pytest.fixture
def ie_driver(webdriver_module):
    sauce_url = "https://{username}:{password}@ondemand.saucelabs.com:443/wd/hub".format(
        username=os.getenv("SAUCE_USERNAME", None),
        password=os.getenv("SAUCE_ACCESS_KEY", None),
    )
    driver = webdriver_module.Remote(
        command_executor=sauce_url,
        desired_capabilities={
            "browserName": "internet explorer",
            "platform": "Windows 10",
            "version": "11.285",
        },
    )
    return driver


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
def test_ie_viewport_screenshot_with_scrolling(eyes, ie_driver):
    ie_driver.get("http://applitools.github.io/demo/TestPages/FramesTestPage")

    test_name = "TestIEViewportScreenshot"
    if eyes.force_full_page_screenshot:
        test_name += "_FPS"
    test_name += "_%s" % eyes.stitch_mode.value
    eyes.open(ie_driver, "Python SDK", test_name)

    eyes.check_window()

    ie_driver.execute_script(
        "arguments[0].scrollIntoView();",
        ie_driver.find_element_by_id("overflowing-div-image"),
    )
    eyes.check_window()
    eyes.close()
