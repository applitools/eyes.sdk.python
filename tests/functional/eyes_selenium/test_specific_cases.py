import pytest
from selenium.webdriver.common.by import By

from applitools.selenium import Region, StitchMode, Target


@pytest.mark.platform("Linux")
def test_quickstart_example(eyes, driver):
    required_viewport = {"width": 450, "height": 300}
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


@pytest.mark.platform("Linux")
@pytest.mark.eyes(force_full_page_screenshot=True, stitch_mode=StitchMode.CSS)
def test_sample_script(eyes, driver):
    driver = eyes.open(
        driver, "Python app", "TestSampleScript", {"width": 600, "height": 400}
    )
    driver.get("https://www.google.com/")
    eyes.check_window(
        "Search page",
        target=(Target.window().ignore((By.CLASS_NAME, "fbar")).send_dom().use_dom()),
    )

    hero = driver.find_element_by_id("body")
    eyes.check_region_by_element(
        hero,
        "Search",
        target=(Target.window().ignore(Region(20, 20, 50, 50), Region(40, 40, 10, 20))),
    )
    eyes.close()


@pytest.mark.platform("Linux")
@pytest.mark.eyes(force_full_page_screenshot=True)
def test_check_window_with_ignore_region_fluent(eyes, driver):
    eyes.open(
        driver,
        "Eyes Selenium SDK - Fluent API",
        "TestCheckWindowWithIgnoreRegion_Fluent",
        {"width": 800, "height": 600},
    )
    driver.get("http://applitools.github.io/demo/TestPages/FramesTestPage/")
    driver.find_element_by_tag_name("input").send_keys("My Input")
    eyes.check_window(
        "Fluent - Window with Ignore region",
        target=Target().ignore(Region(left=50, top=50, width=100, height=100)),
    )
    eyes.close()


@pytest.mark.browser("chrome")
@pytest.mark.platform("Linux")
def test_directly_set_viewport_size(eyes, driver):
    required_viewport = {"width": 800, "height": 600}
    eyes.set_viewport_size_static(driver, required_viewport)
    driver = eyes.open(driver, "Python SDK", "TestViewPort-DirectlySetViewportt")
    assert required_viewport == eyes.get_viewport_size_static(driver)


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
    eyes.check_window(
        "Fluent - Window with Ignore region",
        target=Target.window().send_dom().use_dom(),
    )
    assert "data-applitools-scroll" in driver.page_source
    assert "data-applitools-original-overflow" in driver.page_source
    eyes.close()
