import os

import pytest
from appium import webdriver

from applitools.common import Point
from applitools.selenium import Target
from applitools.selenium.viewport_locator import (
    Pattern,
    add_page_marker,
    device_viewport_location,
    remove_page_marker,
)


@pytest.fixture
def mobile_safari_driver():
    sauce_driver_url = (
        "https://{SAUCE_USERNAME}:{SAUCE_ACCESS_KEY}@"
        "ondemand.saucelabs.com:443/wd/hub".format(**os.environ)
    )
    caps = {
        "browserName": "Safari",
        "appiumVersion": "1.19.2",
        "deviceName": "iPhone XS Simulator",
        "deviceOrientation": "portrait",
        "platformVersion": "13.0",
        "platformName": "iOS",
    }
    driver = webdriver.Remote(sauce_driver_url, caps)
    try:
        yield driver
    finally:
        driver.quit()


def test_add_remove_marker(driver, eyes):
    driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage/")
    device_pixel_ratio = driver.execute_script("return window.devicePixelRatio;")
    eyes.open(
        driver,
        "Viewport locator tests",
        "Add and remove marker",
        {"width": 500, "height": 300},
    )
    marker = add_page_marker(driver)
    eyes.check("Marker added", Target.window())
    remove_page_marker(driver)
    eyes.check("Marker removed", Target.window())
    eyes.close()
    assert marker == Pattern(device_pixel_ratio, device_pixel_ratio * 3, [0, 1, 0])


def test_device_viewport_location(mobile_safari_driver):
    mobile_safari_driver.get(
        "http://applitools.github.io/demo/TestPages/MobileDemo/adaptive.html"
    )

    location = device_viewport_location(mobile_safari_driver)

    assert location == Point(0, 282)


def test_device_viewport_location_algorithm(mobile_safari_driver, eyes):
    mobile_safari_driver.get(
        "http://applitools.github.io/demo/TestPages/MobileDemo/adaptive.html"
    )

    eyes.open(
        mobile_safari_driver, "SafariViewportLocator", "SafariViewportLocatorAlgorithm"
    )
    eyes.check_window()
    eyes.close()


@pytest.mark.skip("The fallback algorithm is not stable anyway")
def test_device_viewport_location_algorithm_fallback(mobile_safari_driver, eyes):
    # This page does not have viewport meta tags and scaled so viewport
    # detection algorithm fails
    mobile_safari_driver.get(
        "https://applitools.github.io/demo/TestPages/SimpleTestPage/"
    )

    eyes.open(
        mobile_safari_driver,
        "SafariViewportLocator",
        "SafariViewportLocatorAlgorithmFallback",
    )
    eyes.check_window()
    eyes.close()
