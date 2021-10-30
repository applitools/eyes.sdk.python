from copy import copy

import pytest
from appium import webdriver as appium_webdriver

from tests.utils import get_pytest_marker


@pytest.fixture
def webdriver_module():
    return appium_webdriver


def _create_mobile_driver(request, remote_url, capabilities, webdriver):
    capabilities = copy(capabilities)
    test_page_url = get_pytest_marker(request, "test_page_url")
    native_app = get_pytest_marker(request, "native_app")
    if test_page_url and native_app:
        raise ValueError
    if native_app:
        capabilities["app"] = native_app
        capabilities["NATIVE_APP"] = True
        capabilities.pop("browserName")

    driver = webdriver.Remote(remote_url, capabilities)
    if test_page_url:
        driver.get(test_page_url)
    return driver


@pytest.fixture
def sauce_iphone8_ios14_driver(request, sauce_driver_url, webdriver_module):
    capabilities = {
        "browserName": "Safari",
        "deviceName": "iPhone 8 Simulator",
        "deviceOrientation": "portrait",
        "platformName": "iOS",
        "platformVersion": "14.3",
    }
    driver = _create_mobile_driver(
        request, sauce_driver_url, capabilities, webdriver_module
    )
    try:
        yield driver
    finally:
        driver.quit()


@pytest.fixture
def sauce_galaxy_s9_android9_driver(request, sauce_driver_url, webdriver_module):
    capabilities = {
        "platformName": "Android",
        "deviceName": "Samsung Galaxy S9 HD GoogleAPI Emulator",
        "platformVersion": "9.0",
        "browserName": "Chrome",
    }
    driver = _create_mobile_driver(
        request, sauce_driver_url, capabilities, webdriver_module
    )
    try:
        yield driver
    finally:
        driver.quit()
