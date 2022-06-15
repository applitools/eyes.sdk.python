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
    capabilities = {
        "appium:automationName": "UIAutomator2",
        "appium:clearSystemFiles": True,
        "appium:deviceName": "Google Pixel 3 XL GoogleAPI Emulator",
        "appium:platformVersion": "10.0",
        "platformName": "Android",
        "sauce:options": {
            "appiumVersion": "1.20.2",
            "deviceOrientation": orientation.upper(),
            "name": name_of_test,
            "noReset": True,
        },
    }
    return appium(capabilities, sauce_url, app=app, browser_name=browser_name)


@sauce.vm
@pytest.fixture(scope="function")
def pixel_3a_xl(app, sauce_url, browser_name, orientation, name_of_test):
    capabilities = {
        "appium:automationName": "UIAutomator2",
        "appium:clearSystemFiles": True,
        "appium:deviceName": "Google Pixel 3a XL GoogleAPI Emulator",
        "appium:platformVersion": "10.0",
        "platformName": "Android",
        "sauce:options": {
            "appiumVersion": "1.20.2",
            "deviceOrientation": orientation.upper(),
            "name": name_of_test,
            "noReset": True,
        },
    }
    return appium(capabilities, sauce_url, app=app, browser_name=browser_name)


@sauce.vm
@pytest.fixture(scope="function")
def samsung_galaxy_s8(app, sauce_url, browser_name, orientation, name_of_test):
    capabilities = {
        "appium:automationName": "UIAutomator2",
        "appium:clearSystemFiles": True,
        "appium:deviceName": "Samsung Galaxy S8 FHD GoogleAPI Emulator",
        "appium:platformVersion": "7.0",
        "platformName": "Android",
        "sauce:options": {
            "appiumVersion": "1.19.2",
            "deviceOrientation": orientation.upper(),
            "name": name_of_test,
            "noReset": True,
        },
    }
    return appium(capabilities, sauce_url, app=app, browser_name=browser_name)


@sauce.mac_vm
@pytest.fixture(scope="function")
def iphone_xs(app, sauce_url, browser_name, orientation, name_of_test):
    capabilities = {
        "appium:automationName": "XCUITest",
        "appium:clearSystemFiles": True,
        "appium:deviceName": "iPhone XS Simulator",
        "appium:platformVersion": "13.0",
        "platformName": "iOS",
        "sauce:options": {
            "appiumVersion": "1.19.2",
            "deviceOrientation": orientation.upper(),
            "name": name_of_test,
            "noReset": True,
        },
    }
    return appium(capabilities, sauce_url, app=app, browser_name=browser_name)


def appium(desired_caps, sauce_url, app="", browser_name=""):
    if app and browser_name:
        raise Exception("Appium drivers shouldn't contain both app and browserName")
    if not app and not browser_name:
        raise Exception("Appium drivers should have app or browserName")
    if app:
        desired_caps["appium:app"] = app
        desired_caps["appium:NATIVE_APP"] = True
    if browser_name:
        desired_caps["browserName"] = browser_name

    selenium_url = os.getenv("SELENIUM_SERVER_URL", sauce_url)
    return appium_webdriver.Remote(
        command_executor=selenium_url, desired_capabilities=desired_caps
    )
