import pytest

from applitools.common import Point
from applitools.selenium import Target
from applitools.selenium.viewport_locator import (
    Pattern,
    add_page_marker,
    device_viewport_location,
    remove_page_marker,
)


def test_add_remove_marker(chrome_driver, eyes):
    chrome_driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage/")
    device_pixel_ratio = chrome_driver.execute_script("return window.devicePixelRatio;")
    driver = eyes.open(
        chrome_driver,
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


@pytest.mark.test_page_url(
    "http://applitools.github.io/demo/TestPages/MobileDemo/adaptive.html"
)
def test_device_viewport_location(sauce_iphone8_ios14_driver):
    location = device_viewport_location(sauce_iphone8_ios14_driver)

    assert location == Point(0, 282)


@pytest.mark.test_page_url(
    "http://applitools.github.io/demo/TestPages/MobileDemo/adaptive.html"
)
def test_device_viewport_location_algorithm(sauce_iphone8_ios14_driver, eyes):
    eyes.open(
        sauce_iphone8_ios14_driver,
        "SafariViewportLocator",
        "SafariViewportLocatorAlgorithm",
    )
    eyes.check_window()
    eyes.close()


@pytest.mark.skip("The fallback algorithm is not stable anyway")
@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/SimpleTestPage/"
)
def test_device_viewport_location_algorithm_fallback(sauce_iphone8_ios14_driver, eyes):
    # This page does not have viewport meta tags and scaled so viewport
    # detection algorithm fails
    eyes.open(
        sauce_iphone8_ios14_driver,
        "SafariViewportLocator",
        "SafariViewportLocatorAlgorithmFallback",
    )
    eyes.check_window()
    eyes.close()
