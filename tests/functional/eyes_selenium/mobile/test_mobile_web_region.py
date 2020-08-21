import pytest
from selenium.webdriver.common.by import By

from applitools.selenium import Target, StitchMode


def _region_test_flow(eyes):
    eyes.configure.stitch_mode = StitchMode.Scroll
    eyes.check(
        "region-scroll", Target.region([By.CSS_SELECTOR, "#footer-menus"]),
    )
    eyes.configure.stitch_mode = StitchMode.CSS
    eyes.check(
        "region-css", Target.region([By.CSS_SELECTOR, "#footer-menus"]),
    )


@pytest.mark.platform("iOS")
@pytest.mark.capabilities(
    **{
        "platformName": "iOS",
        "browserName": "Safari",
        "deviceName": "iPhone 11",
        "platformVersion": "13.2",
    }
)
def test_region_capture_ios(eyes, driver):
    driver.get("https://applitools.com")
    eyes.open(driver, "Mobile Web Tests", "TestRegionCapture_iOS")
    _region_test_flow(eyes)
    eyes.close()


@pytest.mark.platform("Android")
@pytest.mark.capabilities(
    **{
        "platformName": "Android",
        "browserName": "Chrome",
        "deviceName": "Samsung Galaxy S9 HD GoogleAPI Emulator",
        "platformVersion": "9.0",
    }
)
def test_region_capture_android(eyes, driver):
    driver.get("https://applitools.com")
    eyes.open(driver, "Mobile Web Tests", "TestRegionCapture_Android")
    _region_test_flow(eyes)
    eyes.close()
