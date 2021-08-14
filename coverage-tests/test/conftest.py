import os
import time
from copy import copy

import pytest
from appium import webdriver as appium_webdriver
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from applitools.selenium import (
    BatchInfo,
    BrowserType,
    ClassicRunner,
    Configuration,
    Eyes,
    Region,
    StitchMode,
    Target,
    VisualGridRunner,
)


@pytest.fixture(scope="session")
def batch_info():
    return BatchInfo("Python Generated tests")


def pytest_generate_tests(metafunc):
    import uuid

    # setup environment variables once per test run if not settled up
    # needed for multi thread run


#     os.environ["APPLITOOLS_BATCH_ID"] = os.getenv(
#         "APPLITOOLS_BATCH_ID", str(uuid.uuid4())
#     )


@pytest.fixture(scope="function")
def eyes_runner_class():
    return None


@pytest.fixture(scope="function")
def options():
    return webdriver.ChromeOptions()


@pytest.fixture(scope="function")
def browser_type():
    return "Chrome"


@pytest.fixture(scope="function")
def legacy():
    return False


@pytest.fixture(scope="function")
def desired_caps():
    return None


@pytest.fixture(scope="function")
def execution_grid():
    return False


@pytest.fixture(scope="function")
def sauce_url():
    return "https://{username}:{password}@ondemand.saucelabs.com:443/wd/hub".format(
        username=os.getenv("SAUCE_USERNAME", None),
        password=os.getenv("SAUCE_ACCESS_KEY", None),
    )


@pytest.yield_fixture(scope="function")
def android_desired_capabilities(request, dev, app):
    desired_caps = copy(getattr(request, "param", {}))  # browser_config.copy()
    desired_caps["app"] = app
    desired_caps["NATIVE_APP"] = True
    desired_caps["browserName"] = ""
    desired_caps["deviceName"] = "Samsung Galaxy S8 WQHD GoogleAPI Emulator"
    desired_caps["platformVersion"] = "8.1"
    desired_caps["platformName"] = "Android"
    desired_caps["clearSystemFiles"] = True
    desired_caps["noReset"] = True
    desired_caps["automationName"] = "UiAutomator2"
    desired_caps["name"] = "AndroidNativeApp checkWindow"
    desired_caps["deviceOrientation"] = "portrait"
    desired_caps["appiumVersion"] = "1.19.2"
    return desired_caps


@pytest.yield_fixture(scope="function")
def ios_desired_capabilities(request, dev, app):
    desired_caps = copy(getattr(request, "param", {}))
    desired_caps["app"] = app
    desired_caps["NATIVE_APP"] = True
    desired_caps["browserName"] = ""
    desired_caps["deviceName"] = "iPhone XS Simulator"
    desired_caps["platformVersion"] = "13.4"
    desired_caps["platformName"] = "iOS"
    desired_caps["clearSystemFiles"] = True
    desired_caps["noReset"] = True
    desired_caps["automationName"] = "XCUITest"
    desired_caps["name"] = "iOSNativeApp checkWindow"
    desired_caps["deviceOrientation"] = "portrait"
    desired_caps["appiumVersion"] = "1.19.2"
    return desired_caps


@pytest.fixture(scope="function")
def appium(desired_caps, sauce_url):
    selenium_url = os.getenv("SELENIUM_SERVER_URL", sauce_url)
    return appium_webdriver.Remote(
        command_executor=selenium_url, desired_capabilities=desired_caps
    )


@pytest.fixture(scope="function")
def chrome(options, execution_grid):
    options.add_argument("--headless")
    if execution_grid:
        url = os.environ.get("EXECUTION_GRID_URL")
        caps = options.to_capabilities()
        driver = webdriver.Remote(command_executor=url, desired_capabilities=caps)
    else:
        for _ in range(5):
            try:
                driver = webdriver.Chrome(
                    executable_path=ChromeDriverManager().install(),
                    options=options,
                )
            except Exception as e:
                print("Tried to start browser. It was exception {}".format(e))
            time.sleep(1.0)
    return driver


@pytest.fixture(scope="function")
def firefox(options):
    options.add_argument("--headless")
    caps = options.to_capabilities()
    for _ in range(5):
        try:
            driver = webdriver.Firefox(
                executable_path=GeckoDriverManager().install(),
                desired_capabilities=caps,
            )
        except Exception as e:
            print("Tried to start browser. It was exception {}".format(e))
        time.sleep(1.0)
    return driver


@pytest.fixture(scope="function")
def firefox48(sauce_url):
    if legacy:
        capabilities = {}
        capabilities["browserName"] = "firefox"
        capabilities["platform"] = "Windows 10"
        capabilities["version"] = "48.0"
    else:
        capabilities = {
            "browserName": "firefox",
            "browserVersion": "48.0",
            "platformName": "Windows 10",
        }
    driver = webdriver.Remote(
        command_executor=sauce_url, desired_capabilities=capabilities
    )
    return driver


@pytest.fixture(scope="function")
def ie11(sauce_url):
    capabilities = {
        "browserName": "internet explorer",
        "browserVersion": "11.285",
        "platformName": "Windows 10",
    }
    driver = webdriver.Remote(
        command_executor=sauce_url, desired_capabilities=capabilities
    )
    return driver


@pytest.fixture(scope="function")
def edge(sauce_url):
    capabilities = {
        "browserName": "MicrosoftEdge",
        "browserVersion": "18.17763",
        "platformName": "Windows 10",
        "screenResolution": "1920x1080",
    }
    driver = webdriver.Remote(
        command_executor=sauce_url, desired_capabilities=capabilities
    )
    return driver


@pytest.fixture(scope="function")
def safari11(sauce_url):
    if legacy:
        capabilities = {}
        capabilities["browserName"] = "safari"
        capabilities["platform"] = "macOS 10.12"
        capabilities["version"] = "11.0"
    else:
        capabilities = {
            "browserName": "safari",
            "browserVersion": "11.0",
            "platformName": "macOS 10.12",
        }
    driver = webdriver.Remote(
        command_executor=sauce_url, desired_capabilities=capabilities
    )
    return driver


@pytest.fixture(scope="function")
def safari12(sauce_url):
    if legacy:
        capabilities = {}
        capabilities["browserName"] = "safari"
        capabilities["platform"] = "macOS 10.13"
        capabilities["version"] = "12.1"
    else:
        capabilities = {
            "browserName": "safari",
            "browserVersion": "12.1",
            "platformName": "macOS 10.13",
        }
    driver = webdriver.Remote(
        command_executor=sauce_url, desired_capabilities=capabilities
    )
    return driver


@pytest.fixture(scope="function")
def chrome_emulator(options):
    mobile_emulation = {
        "deviceMetrics": {"width": 384, "height": 512, "pixelRatio": 2.0},
        "userAgent": "Mozilla/5.0 (Linux; Android 8.0.0; Android SDK built for x86_64 Build/OSR1.180418.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36",
    }
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    options.add_argument("--headless")
    driver = webdriver.Chrome(
        executable_path=ChromeDriverManager().install(),
        options=options,
    )
    return driver


@pytest.fixture(scope="function")
def driver_builder(chrome):
    return chrome


@pytest.fixture(name="driver", scope="function")
def driver_setup(driver_builder):
    # supported browser types
    #     "Appium": appium,
    #     "Chrome": chrome,
    #     "Firefox": firefox,
    #     "Firefox48": firefox48,
    #     "IE11": ie11,
    #     "Edge": edge,
    #     "Safari11": safari11,
    #     "Safari12": safari12,
    #     "ChromeEmulator": chrome_emulator,
    #

    driver = driver_builder
    yield driver
    # Close the browser.
    try:
        if driver is not None:
            driver.quit()
    except WebDriverException:
        print("Driver was already closed")


@pytest.fixture(name="runner", scope="function")
def runner_setup(eyes_runner_class):
    runner = eyes_runner_class
    yield runner


#     all_test_results = runner.get_all_test_results()
#     print(all_test_results)


@pytest.fixture(scope="function")
def stitch_mode():
    return StitchMode.Scroll


@pytest.fixture(scope="function")
def emulation():
    is_emulation = False
    orientation = ""
    page = ""
    return is_emulation, orientation, page


@pytest.fixture(name="eyes", scope="function")
def eyes_setup(runner, batch_info, stitch_mode, emulation):
    """
    Basic Eyes setup. It'll abort test if wasn't closed properly.
    """
    eyes = Eyes(runner)
    # Initialize the eyes SDK and set your private API key.
    eyes.api_key = os.environ["APPLITOOLS_API_KEY"]
    eyes.configure.batch = batch_info
    eyes.configure.branch_name = "master"
    eyes.configure.parent_branch_name = "master"
    eyes.configure.set_stitch_mode(stitch_mode)
    eyes.configure.set_save_new_tests(False)
    eyes.configure.set_hide_caret(True)
    eyes.configure.set_hide_scrollbars(True)
    eyes.add_property(
        "ForceFPS", "true" if eyes.force_full_page_screenshot else "false"
    )
    is_emulation, orientation, page = emulation
    if is_emulation:
        eyes.add_property("Orientation", orientation)
        eyes.add_property("Page", page)
    yield eyes
    # If the test was aborted before eyes.close was called, ends the test as aborted.
    eyes.abort()
    if runner is not None:
        runner.get_all_test_results(False)
