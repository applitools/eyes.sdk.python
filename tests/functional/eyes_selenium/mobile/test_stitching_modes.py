import pytest
from selenium import webdriver

from applitools.common import StitchMode
from applitools.selenium import Eyes, Target


@pytest.fixture
def sauce_iphone8_ios14_driver(sauce_driver_url):
    capabilities = {
        "browserName": "Safari",
        "deviceName": "iPhone 8 Simulator",
        "deviceOrientation": "portrait",
        "platformName": "iOS",
        "platformVersion": "14.3",
    }
    driver = webdriver.Remote(sauce_driver_url, capabilities)
    try:
        yield driver
    finally:
        driver.quit()


def test_eyes_mobile_scroll_stitching(sauce_iphone8_ios14_driver, eyes):
    sauce_iphone8_ios14_driver.get("https://demo.applitools.com/")
    eyes.stitch_mode = StitchMode.Scroll
    eyes.open(sauce_iphone8_ios14_driver, "Tests", "ios14 scroll stitching")

    eyes.check("step", Target.window().fully())

    eyes.close()


def test_eyes_mobile_css_stitching(sauce_iphone8_ios14_driver, eyes):
    sauce_iphone8_ios14_driver.get("https://demo.applitools.com/")
    eyes.stitch_mode = StitchMode.CSS
    eyes.open(sauce_iphone8_ios14_driver, "Tests", "ios14 css stitching")

    eyes.check("step", Target.window().fully())

    eyes.close()
