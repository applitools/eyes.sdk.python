import os

import pytest
from appium import webdriver as appium_webdriver

from . import sauce


@pytest.fixture(scope="function")
def orientation():
    return "portrait"


@pytest.fixture(scope="function")
def app():
    return ""


@pytest.fixture(scope="function")
def browser_name():
    return ""


@sauce.vm
@pytest.fixture(scope="function")
def pixel_3_xl(app, sauce_url, browser_name, orientation, name_of_test):
    desired_caps = {
        "deviceName": "Google Pixel 3 XL GoogleAPI Emulator",
        "platformVersion": "10.0",
        "platformName": "Android",
        "clearSystemFiles": True,
        "noReset": True,
        "automationName": "UiAutomator2",
        "name": name_of_test,
        "deviceOrientation": orientation,
        "appiumVersion": "1.20.2",
    }
    return appium(desired_caps, sauce_url, app=app, browser_name=browser_name)


@sauce.vm
@pytest.fixture(scope="function")
def pixel_3a_xl(app, sauce_url, browser_name, orientation, name_of_test):
    desired_caps = {
        "deviceName": "Google Pixel 3a XL GoogleAPI Emulator",
        "platformVersion": "10.0",
        "platformName": "Android",
        "clearSystemFiles": True,
        "noReset": True,
        "automationName": "UiAutomator2",
        "name": name_of_test,
        "appiumVersion": "1.20.2",
    }
    driver = appium(desired_caps, sauce_url, app=app, browser_name=browser_name)
    driver.orientation = orientation.upper()
    return driver


@sauce.vm
@pytest.fixture(scope="function")
def samsung_galaxy_s8(app, sauce_url, browser_name, orientation, name_of_test):
    desired_caps = {
        "deviceName": "Samsung Galaxy S8 FHD GoogleAPI Emulator",
        "platformVersion": "7.0",
        "platformName": "Android",
        "clearSystemFiles": True,
        "noReset": True,
        "automationName": "UiAutomator2",
        "name": name_of_test,
        "appiumVersion": "1.19.2",
    }
    driver = appium(desired_caps, sauce_url, app=app, browser_name=browser_name)
    driver.orientation = orientation.upper()
    return driver


@sauce.mac_vm
@pytest.fixture(scope="function")
def iphone_xs(app, sauce_url, browser_name, orientation, name_of_test):
    desired_caps = {
        "deviceName": "iPhone XS Simulator",
        "platformVersion": "13.0",
        "platformName": "iOS",
        "clearSystemFiles": True,
        "noReset": True,
        "automationName": "XCUITest",
        "name": name_of_test,
        "deviceOrientation": orientation,
        "appiumVersion": "1.19.2",
    }
    return appium(desired_caps, sauce_url, app=app, browser_name=browser_name)


def appium(desired_caps, sauce_url, app="", browser_name=""):
    if app and browser_name:
        raise Exception("Appium drivers shouldn't contain both app and browserName")
    if not app and not browser_name:
        raise Exception("Appium drivers should have app or browserName")
    if app:
        desired_caps["app"] = app
        desired_caps["NATIVE_APP"] = True
        desired_caps["browserName"] = ""
    if browser_name:
        desired_caps["browserName"] = browser_name

    selenium_url = os.getenv("SELENIUM_SERVER_URL", sauce_url)
    return appium_webdriver.Remote(
        command_executor=selenium_url, desired_capabilities=desired_caps
    )
