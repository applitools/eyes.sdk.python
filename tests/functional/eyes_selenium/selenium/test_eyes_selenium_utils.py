import pytest
import selenium
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from applitools.common import EyesError, RectangleSize
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
def sauce_ie11_w10_d3141(sauce_driver_url):
    capabilities = {
        "browserName": "internet explorer",
        "browserVersion": "11.285",
        "platformName": "Windows 10",
        "sauce:options": {
            "screenResolution": "1024x768",
            "iedriverVersion": "3.141.0",
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
def sauce_firefox_w10(sauce_driver_url):
    capabilities = {
        "browserName": "firefox",
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
def sauce_chrome_macos(sauce_driver_url):
    capabilities = {
        "browserName": "chrome",
        "browserVersion": "latest",
        "platformName": "macOS 11.00",
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
def sauce_firefox_macos(sauce_driver_url):
    capabilities = {
        "browserName": "firefox",
        "browserVersion": "latest",
        "platformName": "macOS 11.00",
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


@pytest.fixture
def sauce_safari12_osx1013_legacy(sauce_driver_url):
    capabilities = {
        "browserName": "safari",
        "platform": "macOS 10.13",
        "version": "12.1",
    }
    driver = webdriver.Remote(sauce_driver_url, capabilities)
    try:
        yield driver
    finally:
        driver.quit()


@pytest.fixture
def sauce_safari_latest(sauce_driver_url):
    capabilities = {
        "browserName": "safari",
        "browserVersion": "latest",
    }
    driver = webdriver.Remote(sauce_driver_url, capabilities)
    try:
        yield driver
    finally:
        driver.quit()


def test_set_viewport_size_win_chrome(sauce_chrome_w10):
    set_viewport_size(sauce_chrome_w10, RectangleSize(800, 600))

    assert get_viewport_size(sauce_chrome_w10) == RectangleSize(800, 600)


def test_set_minimal_viewport_size_win_chrome(sauce_chrome_w10):
    set_viewport_size(sauce_chrome_w10, RectangleSize(500, 300))

    assert get_viewport_size(sauce_chrome_w10) == RectangleSize(500, 300)


def test_set_viewport_size_maximized_win_chrome(sauce_chrome_w10):
    sauce_chrome_w10.maximize_window()

    set_viewport_size(sauce_chrome_w10, RectangleSize(800, 600))

    assert get_viewport_size(sauce_chrome_w10) == RectangleSize(800, 600)


def test_set_viewport_size_win_ie10_iedriver_314(sauce_ie10_w7_d314):
    set_viewport_size(sauce_ie10_w7_d314, RectangleSize(800, 600))

    assert get_viewport_size(sauce_ie10_w7_d314) == RectangleSize(800, 600)


def test_set_viewport_size_win_ie11_iedriver_3141(sauce_ie11_w10_d3141):
    set_viewport_size(sauce_ie11_w10_d3141, RectangleSize(800, 600))

    assert get_viewport_size(sauce_ie11_w10_d3141) == RectangleSize(800, 600)


def test_set_viewport_size_win_ie11_iedriver_3141_minimized(sauce_ie11_w10_d3141):
    sauce_ie11_w10_d3141.minimize_window()
    set_viewport_size(sauce_ie11_w10_d3141, RectangleSize(800, 600))

    assert get_viewport_size(sauce_ie11_w10_d3141) == RectangleSize(800, 600)


def test_set_minimal_viewport_size_win_ie11_iedriver_3141(sauce_ie11_w10_d3141):
    set_viewport_size(sauce_ie11_w10_d3141, RectangleSize(234, 100))

    assert get_viewport_size(sauce_ie11_w10_d3141) == RectangleSize(234, 100)


def test_set_minimal_viewport_size_win_ie11_iedriver_3141_minimized(
    sauce_ie11_w10_d3141,
):
    sauce_ie11_w10_d3141.minimize_window()
    set_viewport_size(sauce_ie11_w10_d3141, RectangleSize(234, 100))

    assert get_viewport_size(sauce_ie11_w10_d3141) == RectangleSize(234, 100)


def test_set_viewport_size_win_ie11_iedriver_3141(sauce_ie11_w10_d3141):
    set_viewport_size(sauce_ie11_w10_d3141, RectangleSize(800, 600))

    assert get_viewport_size(sauce_ie11_w10_d3141) == RectangleSize(800, 600)


def test_set_viewport_size_safari11_osx1013(sauce_safari11_osx1013):
    set_viewport_size(sauce_safari11_osx1013, RectangleSize(800, 600))

    assert get_viewport_size(sauce_safari11_osx1013) == RectangleSize(800, 600)


@pytest.mark.skipif(selenium.__version__ >= "4.", "Selenium 4 drops legacy")
def test_set_viewport_size_safari12_osx1013_legacy(sauce_safari12_osx1013_legacy):
    set_viewport_size(sauce_safari12_osx1013_legacy, RectangleSize(800, 600))

    assert get_viewport_size(sauce_safari12_osx1013_legacy) == RectangleSize(800, 600)


def test_driver_set_window_size_safari11_osx1013_fails(sauce_safari11_osx1013):
    # This test is needed to prove there are still browsers that don't support
    # set_window_size & set_window_position calls
    sauce_safari11_osx1013.set_window_rect(0, 0, 400, 300)
    assert sauce_safari11_osx1013.get_window_size() == {"width": 400, "height": 300}
    with pytest.raises(WebDriverException):
        sauce_safari11_osx1013.set_window_size(800, 600)
    with pytest.raises(WebDriverException):
        sauce_safari11_osx1013.set_window_position(0, 0)


@pytest.mark.skipif(selenium.__version__ >= "4.", "Selenium 4 drops legacy")
def test_driver_safari12_osx1013_set_window_rect_fails(sauce_safari12_osx1013_legacy):
    # This test is needed to prove there are still browsers that don't support
    # set_window_rect calls
    sauce_safari12_osx1013_legacy.set_window_position(0, 0)
    sauce_safari12_osx1013_legacy.set_window_size(400, 300)

    assert sauce_safari12_osx1013_legacy.get_window_size() == {
        "width": 400,
        "height": 300,
    }
    with pytest.raises(WebDriverException):
        sauce_safari12_osx1013_legacy.set_window_rect(0, 0, 800, 600)


def test_set_viewport_size_10_10_safari_latest(sauce_safari_latest):
    set_viewport_size(sauce_safari_latest, RectangleSize(10, 10))

    assert get_viewport_size(sauce_safari_latest) == RectangleSize(10, 10)


def test_set_viewport_size_10_10_win_chrome(sauce_chrome_w10):
    with pytest.raises(EyesError, match="Failed to set the viewport size"):
        set_viewport_size(sauce_chrome_w10, RectangleSize(10, 10))

    assert get_viewport_size(sauce_chrome_w10) == RectangleSize(500, 10)


def test_set_viewport_size_10_10_mac_chrome(sauce_chrome_macos):
    with pytest.raises(EyesError, match="Failed to set the viewport size"):
        set_viewport_size(sauce_chrome_macos, RectangleSize(10, 10))

    assert get_viewport_size(sauce_chrome_macos) == RectangleSize(500, 251)


def test_set_viewport_size_10_10_win_firefox(sauce_firefox_w10):
    with pytest.raises(EyesError, match="Failed to set the viewport size"):
        set_viewport_size(sauce_firefox_w10, RectangleSize(10, 10))

    assert get_viewport_size(sauce_firefox_w10) == RectangleSize(454, 68)


def test_set_viewport_size_10_10_mac_firefox(sauce_firefox_macos):
    with pytest.raises(EyesError, match="Failed to set the viewport size"):
        set_viewport_size(sauce_firefox_macos, RectangleSize(10, 10))

    assert get_viewport_size(sauce_firefox_macos) == RectangleSize(450, 63)
