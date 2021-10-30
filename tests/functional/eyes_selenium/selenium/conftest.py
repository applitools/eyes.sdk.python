import json
from os import path

import pytest
from selenium import webdriver

samples_dir = path.join(path.dirname(__file__), "resources")


@pytest.fixture
def expected_json_data(request):
    """Loads expected result from json file"""
    mark = request.node.get_closest_marker("expected_json")
    file_name = mark.args[0] if mark else request.node.originalname
    with open(path.join(samples_dir, file_name + ".json"), "rb") as f:
        return f.read()


@pytest.fixture
def expected_json(expected_json_data):
    return json.loads(expected_json_data)


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
        "version": "latest",
    }
    driver = webdriver.Remote(sauce_driver_url, capabilities)
    try:
        yield driver
    finally:
        driver.quit()
