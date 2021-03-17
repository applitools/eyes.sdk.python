import pytest
from selenium import webdriver

from applitools.common import RectangleSize
from applitools.selenium.eyes_selenium_utils import get_viewport_size, set_viewport_size


@pytest.fixture
def sauce_ie10_w7_d314(sauce_driver_url):
    capabilities = {
        "browserName": "internet explorer",
        "browserVersion": "10.0",
        "platformName": "Windows 7",
        "sauce:options": {
            "screenResolution": "1024x768",
            "iedriverVersion": "3.14.0",
        },
    }
    driver = webdriver.Remote(sauce_driver_url, capabilities)
    try:
        yield driver
    finally:
        driver.quit()


@pytest.fixture
def sauce_chrome_w10(sauce_driver_url):
    capabilities = {
        "browserName": "chrome",
        "browserVersion": "latest",
        "platformName": "Windows 10",
        "sauce:options": {
            "screenResolution": "1024x768",
        },
    }
    driver = webdriver.Remote(sauce_driver_url, capabilities)
    try:
        yield driver
    finally:
        driver.quit()


@pytest.fixture
def sauce_safari11_osx1013(sauce_driver_url):
    capabilities = {
        "browserName": "safari",
        "browserVersion": "11.1",
        "platformName": "macOS 10.13",
        "sauce:options": {
            "screenResolution": "1024x768",
        },
    }
    driver = webdriver.Remote(sauce_driver_url, capabilities)
    try:
        yield driver
    finally:
        driver.quit()


def test_set_viewport_size_win_chrome(sauce_chrome_w10):
    set_viewport_size(sauce_chrome_w10, RectangleSize(800, 600))

    assert get_viewport_size(sauce_chrome_w10) == RectangleSize(800, 600)


def test_set_viewport_size_maximized_win_chrome(sauce_chrome_w10):
    sauce_chrome_w10.maximize_window()

    set_viewport_size(sauce_chrome_w10, RectangleSize(800, 600))

    assert get_viewport_size(sauce_chrome_w10) == RectangleSize(800, 600)


def test_set_viewport_size_win_ie10_iedriver_314(sauce_ie10_w7_d314):
    set_viewport_size(sauce_ie10_w7_d314, RectangleSize(800, 600))

    assert get_viewport_size(sauce_ie10_w7_d314) == RectangleSize(800, 600)


def test_set_viewport_size_safari11_osx1013(sauce_safari11_osx1013):
    set_viewport_size(sauce_safari11_osx1013, RectangleSize(800, 600))

    assert get_viewport_size(sauce_safari11_osx1013) == RectangleSize(800, 600)
