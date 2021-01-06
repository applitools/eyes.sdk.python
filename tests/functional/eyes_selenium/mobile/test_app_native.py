import pytest
from appium import webdriver as appium_webdriver

from applitools.core import Feature

ANDROID_CAPS = {
    "app": "http://saucelabs.com/example_files/ContactManager.apk",
    "clearSystemFiles": True,
    "noReset": True,
    "browserName": "",
    "automationName": "UiAutomator2",
    "platformName": "Android",
    "platformVersion": "6.0",
    "appiumVersion": "1.13.0",
    "deviceName": "Android Emulator",
    "deviceOrientation": "portrait",
}

IOS_CAPS = {
    "app": "http://174.138.1.48/doc/Demo_Application.zip",
    "clearSystemFiles": True,
    "noReset": True,
    "browserName": "",
    "platformName": "iOS",
    "platformVersion": "13.4",
    "automationName": "XCUITest",
    "appiumVersion": "1.13.0",
    "deviceName": "iPhone XR Simulator",
    "deviceOrientation": "portrait",
}


@pytest.fixture
def webdriver_module():
    return appium_webdriver


@pytest.mark.platform("Android")
@pytest.mark.capabilities(**ANDROID_CAPS)
@pytest.mark.eyes_config(hide_scrollbars=False)
def test_android_native(eyes, driver):
    eyes.open(driver, "Mobile Native Tests", "Android Native App 1")
    eyes.check_window("Contact list")
    eyes.close()


@pytest.mark.platform("Android")
@pytest.mark.capabilities(**ANDROID_CAPS)
@pytest.mark.eyes_config(hide_scrollbars=False)
def test_android_native_scale_app_native_feature(eyes, driver):
    eyes.configure.set_features(Feature.SCALE_MOBILE_APP)
    eyes.open(
        driver, "Mobile Native Tests", "Android Native App 1 Scale Native Feature"
    )
    eyes.check_window("Contact list")
    eyes.close()


@pytest.mark.platform("iOS")
@pytest.mark.capabilities(**IOS_CAPS)
@pytest.mark.eyes_config(hide_scrollbars=False)
def test_ios_native(eyes, driver):
    eyes.open(driver, "Mobile Native Tests", "My first Appium Python test!")
    eyes.check_window("Contact list")
    eyes.close()


@pytest.mark.platform("iOS")
@pytest.mark.capabilities(**IOS_CAPS)
@pytest.mark.eyes_config(hide_scrollbars=False)
def test_ios_native_scale_app_native_feature(eyes, driver):
    eyes.configure.set_features(Feature.SCALE_MOBILE_APP)
    eyes.open(
        driver,
        "Mobile Native Tests",
        "My first Appium Python test! Scale Native Feature",
    )
    eyes.check_window("Contact list")
    eyes.close()
