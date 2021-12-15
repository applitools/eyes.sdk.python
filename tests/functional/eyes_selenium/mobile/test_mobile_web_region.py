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
        Target.region([By.TAG_NAME, "footer"]),
    )
    eyes.configure.stitch_mode = StitchMode.CSS
    eyes.check(
        "region-css",
        Target.region([By.TAG_NAME, "footer"]).timeout(0),
    )


def _region_fully_test_flow(eyes):
    eyes.configure.stitch_mode = StitchMode.Scroll
    eyes.check(
        "region-scroll",
        Target.region([By.TAG_NAME, "footer"]),
    )
    eyes.configure.stitch_mode = StitchMode.CSS
    eyes.check(
        "region-css",
        Target.region([By.TAG_NAME, "footer"]).fully().timeout(0),
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
    "https://applitools.github.io/demo/TestPages/RegionOutOfViewport/"
)
def test_region_capture_ios(eyes, driver):
    eyes.configure.is_simulator = True
    eyes.open(driver, "Mobile Web Tests", "TestRegionCapture_iOS")
    _region_test_flow(eyes)
    eyes.close()


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
    "https://applitools.github.io/demo/TestPages/RegionOutOfViewport/"
)
def test_region_fully_capture_ios(eyes, driver):
    eyes.configure.is_simulator = True
    eyes.open(driver, "Mobile Web Tests", "TestRegionFullyCapture_iOS")
    _region_fully_test_flow(eyes)
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
    "https://applitools.github.io/demo/TestPages/RegionOutOfViewport/"
)
@pytest.mark.skip("USDK Difference, probably different emulator")
def test_region_capture_android(eyes, driver):
    eyes.configure.is_simulator = True
    eyes.open(driver, "Mobile Web Tests", "TestRegionCapture_Android")
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
    "https://applitools.github.io/demo/TestPages/RegionOutOfViewport/"
)
@pytest.mark.skip("USDK Difference, additional space below")
def test_region_fully_capture_android(eyes, driver):
    eyes.configure.is_simulator = True
    eyes.open(driver, "Mobile Web Tests", "TestRegionFullyCapture_Android")
    _region_fully_test_flow(eyes)
    eyes.close()
