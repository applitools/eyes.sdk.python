import os
import time

import pytest
import selenium
from pkg_resources import parse_version
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from . import sauce

LEGACY_SELENIUM = parse_version(selenium.__version__) < parse_version("4")


@pytest.fixture(scope="function")
def chrome(execution_grid):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    if execution_grid:
        url = os.environ.get("EXECUTION_GRID_URL")
        return webdriver.Remote(command_executor=url, options=options)
    else:
        return start_chrome_driver(options)


@pytest.fixture(scope="function")
def firefox():
    options = webdriver.FirefoxOptions()
    options.headless = True
    if LEGACY_SELENIUM:
        return webdriver.Firefox(
            executable_path=GeckoDriverManager().install(),
            options=options,
        )
    else:
        from selenium.webdriver.firefox.service import Service

        return webdriver.Firefox(
            service=Service(GeckoDriverManager().install()),
            options=options,
        )


@sauce.vm
@pytest.fixture(scope="function")
def firefox_48(sauce_url, legacy, name_of_test):
    if legacy:
        if not LEGACY_SELENIUM:
            pytest.skip("Firefox 48 can only be accessed in legacy Selenium")
        capabilities = {
            "browserName": "firefox",
            "platform": "Windows 10",
            "version": "48.0",
            "name": name_of_test,
        }
    else:
        raise Exception("Unsupported browser version for W3C")
    return webdriver.Remote(
        command_executor=sauce_url, desired_capabilities=capabilities
    )


@sauce.vm
@pytest.fixture(scope="function")
def ie_11(sauce_url, name_of_test):
    capabilities = {
        "browserName": "internet explorer",
        "browserVersion": "11.285",
        "platformName": "Windows 10",
        "sauce:options": {"name": name_of_test},
    }
    return webdriver.Remote(
        command_executor=sauce_url, desired_capabilities=capabilities
    )


@sauce.vm
@pytest.fixture(scope="function")
def edge_18(sauce_url, name_of_test):
    capabilities = {
        "browserName": "MicrosoftEdge",
        "browserVersion": "18.17763",
        "platformName": "Windows 10",
        "screenResolution": "1920x1080",
        "sauce:options": {"name": name_of_test},
    }
    return webdriver.Remote(
        command_executor=sauce_url, desired_capabilities=capabilities
    )


@sauce.mac_vm
@pytest.fixture(scope="function")
def safari_11(sauce_url, legacy, name_of_test):
    if legacy:
        if not LEGACY_SELENIUM:
            pytest.skip("Legacy Safari 11 driver is not functional in Selenium 4")
        capabilities = {
            "browserName": "safari",
            "platform": "macOS 10.13",
            "version": "11.1",
            "name": name_of_test,
        }
    else:
        capabilities = {
            "browserName": "safari",
            "browserVersion": "11.1",
            "platformName": "macOS 10.13",
            "sauce:options": {"name": name_of_test},
        }
    return webdriver.Remote(
        command_executor=sauce_url, desired_capabilities=capabilities
    )


@sauce.mac_vm
@pytest.fixture(scope="function")
def safari_12(sauce_url, legacy, name_of_test):
    if legacy:
        capabilities = {}
        capabilities["browserName"] = "safari"
        capabilities["platform"] = "macOS 10.13"
        capabilities["version"] = "12.1"
        capabilities["seleniumVersion"] = "3.4.0"
        capabilities["name"] = name_of_test
    else:
        capabilities = {
            "browserName": "safari",
            "browserVersion": "12.1",
            "platformName": "macOS 10.13",
            "sauce:options": {"name": name_of_test},
        }
    return webdriver.Remote(
        command_executor=sauce_url, desired_capabilities=capabilities
    )


@pytest.fixture(scope="function")
def chrome_emulator():
    options = webdriver.ChromeOptions()
    mobile_emulation = {
        "deviceMetrics": {"width": 384, "height": 512, "pixelRatio": 2.0},
        "userAgent": "Mozilla/5.0 (Linux; Android 8.0.0; Android SDK built for x86_64 Build/OSR1.180418.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36",
    }
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    options.add_argument("--headless")
    return start_chrome_driver(options)


def start_chrome_driver(options):
    if LEGACY_SELENIUM:
        return webdriver.Chrome(
            executable_path=ChromeDriverManager().install(),
            options=options,
        )
    else:
        from selenium.webdriver.chrome.service import Service

        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
        )
