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
# Download driver during module import to avoid racy downloads by xdist workers
GECKO_DRIVER = GeckoDriverManager().install()
CHROME_DRIVER = ChromeDriverManager().install()


@pytest.fixture(scope="function")
def chrome(execution_grid):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    if execution_grid:
        url = os.environ.get("EXECUTION_GRID_URL")
        if LEGACY_SELENIUM:
            options.capabilities.pop("platform")
            options.capabilities.pop("version")
        return webdriver.Remote(command_executor=url, options=options)
    else:
        return start_chrome_driver(options)


@pytest.fixture(scope="function")
def firefox():
    options = webdriver.FirefoxOptions()
    options.headless = True
    if LEGACY_SELENIUM:
        return webdriver.Firefox(executable_path=GECKO_DRIVER, options=options)
    else:
        from selenium.webdriver.firefox.service import Service

        return webdriver.Firefox(service=Service(GECKO_DRIVER), options=options)


@sauce.vm
@pytest.fixture(scope="function")
def firefox_48(sauce_url, legacy, name_of_test):
    if LEGACY_SELENIUM:
        if legacy:
            options = webdriver.FirefoxOptions()
            options.set_capability("name", name_of_test)
            options.set_capability("platform", "Windows 10")
            options.set_capability("version", "48.0")
            return webdriver.Remote(command_executor=sauce_url, options=options)
        else:
            raise Exception("Firefox 48 can only be accessed in legacy protocol")
    else:
        pytest.skip("Firefox 48 can only be accessed in legacy Selenium")


@sauce.vm
@pytest.fixture(scope="function")
def ie_11(sauce_url, name_of_test):
    options = webdriver.IeOptions()
    options.set_capability("browserVersion", "11.285")
    options.set_capability("platformName", "Windows 10")
    options.set_capability("sauce:options", {"name": name_of_test})
    return webdriver.Remote(command_executor=sauce_url, options=options)


@sauce.vm
@pytest.fixture(scope="function")
def edge_18(sauce_url, name_of_test):
    if LEGACY_SELENIUM:
        capabilities = {
            "browserName": "MicrosoftEdge",
            "browserVersion": "18.17763",
            "platformName": "Windows 10",
            "sauce:options": {"screenResolution": "1920x1080", "name": name_of_test},
        }
        return webdriver.Remote(sauce_url, capabilities)
    else:
        options = webdriver.EdgeOptions()
        options.browser_version = "18.17763"
        options.platform_name = "Windows 10"
        options.set_capability(
            "sauce:options", {"screenResolution": "1920x1080", "name": name_of_test}
        )
        return webdriver.Remote(command_executor=sauce_url, options=options)


@sauce.mac_vm
@pytest.fixture(scope="function")
def safari_11(sauce_url, legacy, name_of_test):
    if LEGACY_SELENIUM:
        if legacy:
            capabilities = {
                "browserName": "safari",
                "name": name_of_test,
                "platform": "macOS 10.13",
                "version": "11.1",
            }
        else:
            raise NotImplementedError
        return webdriver.Remote(sauce_url, capabilities)
    else:
        if legacy:
            pytest.skip("Legacy Safari 11 driver is not functional in Selenium 4")
        else:
            raise NotImplementedError


@sauce.mac_vm
@pytest.fixture(scope="function")
def safari_12(sauce_url, legacy, name_of_test):
    if LEGACY_SELENIUM:
        if legacy:
            capabilities = {
                "browserName": "safari",
                "name": name_of_test,
                "platform": "macOS 10.13",
                "seleniumVersion": "3.4.0",
                "version": "12.1",
            }
        else:
            raise NotImplementedError
        return webdriver.Remote(sauce_url, capabilities)
    else:
        if legacy:
            from selenium.webdriver.safari.options import Options

            options = Options()
            options.set_capability("name", name_of_test)
            options.set_capability("platform", "macOS 10.13")
            options.set_capability("seleniumVersion", "3.4.0")
            options.set_capability("version", "12.1")
        else:
            raise NotImplementedError
        return webdriver.Remote(command_executor=sauce_url, options=options)


@pytest.fixture(scope="function")
def chrome_emulator():
    options = webdriver.ChromeOptions()
    mobile_emulation = {
        "deviceMetrics": {"width": 384, "height": 512, "pixelRatio": 2.0},
        "userAgent": "Mozilla/5.0 (Linux; Android 8.0.0; "
        "Android SDK built for x86_64 Build/OSR1.180418.004) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/69.0.3497.100 Mobile "
        "Safari/537.36",
    }
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    options.add_argument("--headless")
    return start_chrome_driver(options)


def start_chrome_driver(options):
    if LEGACY_SELENIUM:
        return webdriver.Chrome(executable_path=CHROME_DRIVER, options=options)
    else:
        from selenium.webdriver.chrome.service import Service

        return webdriver.Chrome(service=Service(CHROME_DRIVER), options=options)
