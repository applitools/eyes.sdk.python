import pytest
from appium import webdriver
from selenium.webdriver.common.by import By

from applitools.selenium import StitchMode, Target


@pytest.fixture
def webdriver_module():
    return webdriver


def _region_test_flow(eyes):
    eyes.configure.stitch_mode = StitchMode.Scroll
    eyes.check(
        "region-scroll",
        Target.region([By.CSS_SELECTOR, "#PhonePortraitBreak"]),
    )
    eyes.configure.stitch_mode = StitchMode.CSS
    eyes.check(
        "region-css",
        Target.region([By.CSS_SELECTOR, "#PhonePortraitBreak"]).timeout(0),
    )


@pytest.mark.platform("iOS")
@pytest.mark.capabilities(
    **{
        "platformName": "iOS",
        "browserName": "Safari",
        "deviceName": "iPhone 11",
        "platformVersion": "13.4",
    }
)
@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/MobileDemo/adaptive.html"
)
def test_region_capture_ios(eyes, driver):
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
@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/MobileDemo/adaptive.html"
)
def test_region_capture_android(eyes, driver):
    eyes.open(driver, "Mobile Web Tests", "TestRegionCapture_Android")
    _region_test_flow(eyes)
    eyes.close()
