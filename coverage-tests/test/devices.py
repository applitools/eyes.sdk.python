import os

import pytest
from appium import webdriver as appium_webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions

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
    sauce_options = {
        "appiumVersion": "1.20.2",
        "deviceOrientation": orientation.upper(),
        "name": name_of_test,
        "noReset": True,
    }
    options = (
        UiAutomator2Options()
        .set_capability("clearSystemFiles", True)
        .set_capability("deviceName", "Google Pixel 3 XL GoogleAPI Emulator")
        .set_capability("platformVersion", "10.0")
        .set_capability("sauce:options", sauce_options)
    )
    return _appium(options, sauce_url, app=app, browser_name=browser_name)


@sauce.vm
@pytest.fixture(scope="function")
def pixel_3a_xl(app, sauce_url, browser_name, orientation, name_of_test):
    sauce_options = {
        "appiumVersion": "1.20.2",
        "deviceOrientation": orientation.upper(),
        "name": name_of_test,
        "noReset": True,
    }
    options = (
        UiAutomator2Options()
        .set_capability("clearSystemFiles", True)
        .set_capability("deviceName", "Google Pixel 3a XL GoogleAPI Emulator")
        .set_capability("platformVersion", "10.0")
        .set_capability("sauce:options", sauce_options)
    )
    return _appium(options, sauce_url, app=app, browser_name=browser_name)


@sauce.vm
@pytest.fixture(scope="function")
def samsung_galaxy_s8(app, sauce_url, browser_name, orientation, name_of_test):
    sauce_options = {
        "appiumVersion": "1.19.2",
        "deviceOrientation": orientation.upper(),
        "name": name_of_test,
        "noReset": True,
    }
    options = (
        UiAutomator2Options()
        .set_capability("clearSystemFiles", True)
        .set_capability("deviceName", "Samsung Galaxy S8 FHD GoogleAPI Emulator")
        .set_capability("platformVersion", "7.0")
        .set_capability("sauce:options", sauce_options)
    )
    return _appium(options, sauce_url, app=app, browser_name=browser_name)


@sauce.mac_vm
@pytest.fixture(scope="function")
def iphone_xs(app, sauce_url, browser_name, orientation, name_of_test):
    sauce_options = {
        "appiumVersion": "1.19.2",
        "deviceOrientation": orientation.upper(),
        "name": name_of_test,
        "noReset": True,
    }
    options = (
        XCUITestOptions()
        .set_capability("clearSystemFiles", True)
        .set_capability("deviceName", "iPhone XS Simulator")
        .set_capability("platformVersion", "13.0")
        .set_capability("sauce:options", sauce_options)
    )
    return _appium(options, sauce_url, app=app, browser_name=browser_name)


def _appium(options, sauce_url, app="", browser_name=""):
    if app and browser_name:
        raise Exception("Appium drivers shouldn't contain both app and browserName")
    if not app and not browser_name:
        raise Exception("Appium drivers should have app or browserName")
    if app:
        options = options.set_capability("app", app).set_capability("NATIVE_APP", True)
    if browser_name:
        options = options.set_capability("browserName", browser_name)

    selenium_url = os.getenv("SELENIUM_SERVER_URL", sauce_url)
    return appium_webdriver.Remote(command_executor=selenium_url, options=options)
