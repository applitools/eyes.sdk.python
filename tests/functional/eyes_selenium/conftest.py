import os
import typing

from selenium import webdriver
from selenium.common.exceptions import WebDriverException

import pytest
from applitools.common import BatchInfo, logger
from applitools.selenium import Eyes, EyesWebDriver, eyes_selenium_utils
from applitools.selenium.__version__ import __version__
from applitools.selenium.visual_grid import VisualGridRunner
from mock import MagicMock
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeDriverManager, IEDriverManager

if typing.TYPE_CHECKING:
    from _pytest.fixtures import SubRequest

BROWSERS_WEBDRIVERS = {
    "firefox": (GeckoDriverManager, webdriver.Firefox, webdriver.FirefoxOptions),
    "chrome": (ChromeDriverManager, webdriver.Chrome, webdriver.ChromeOptions),
    "internet explorer": (IEDriverManager, webdriver.Ie, webdriver.IeOptions),
    "MicrosoftEdge": (EdgeDriverManager, webdriver.Edge, None),
    "safari": (None, webdriver.Safari, None),
}


def _setup_env_vars_for_session():
    os.environ["APPLITOOLS_BATCH_NAME"] = "Python | Selenium SDK {}".format(__version__)


def pytest_generate_tests(metafunc):
    _setup_env_vars_for_session()


@pytest.fixture
def eyes_class():
    return Eyes


@pytest.fixture
def webdriver_module():
    return webdriver


@pytest.fixture(scope="function")
def eyes_open(request, eyes, driver):
    test_page_url = request.node.get_closest_marker("test_page_url").args[-1]

    viewport_size = request.node.get_closest_marker("viewport_size")
    viewport_size = viewport_size.args[-1] if viewport_size else None

    test_suite_name = request.node.get_closest_marker("test_suite_name")
    test_suite_name = (
        test_suite_name.args[-1] if test_suite_name else "Python Selenium SDK"
    )
    test_name_pattern = request.node.get_closest_marker("test_name_pattern")
    test_name_pattern = (
        test_name_pattern.args[-1] if test_name_pattern else {"from": "", "to": ""}
    )
    # use camel case in method name for fit java sdk tests name
    test_name = request.function.__name__.title().replace("_", "")
    test_name = test_name.replace(test_name_pattern["from"], test_name_pattern["to"])

    if eyes.force_full_page_screenshot:
        test_suite_name += " - ForceFPS"
        test_name += "_FPS"
    driver = eyes.open(driver, test_suite_name, test_name, viewport_size=viewport_size)
    driver.get(test_page_url)

    yield eyes, driver
    results = eyes.close()
    print(results)


@pytest.fixture(scope="function")
def eyes_for_class(request, eyes_open):
    # TODO: implement eyes.setDebugScreenshotsPrefix("Java_" + testName + "_");

    eyes, driver = eyes_open
    request.cls.eyes = eyes
    request.cls.driver = driver
    yield


@pytest.fixture(scope="function")
def driver_for_class(request, driver):
    test_page_url = request.node.get_closest_marker("test_page_url").args[0]
    viewport_size = request.node.get_closest_marker("viewport_size").args[0]

    driver = EyesWebDriver(driver, MagicMock(Eyes))
    driver.quit = MagicMock()
    if viewport_size:
        eyes_selenium_utils.set_browser_size(driver, viewport_size)
    request.cls.driver = driver

    driver.get(test_page_url)
    yield
    driver.quit()


@pytest.yield_fixture(scope="function")
def driver(request, browser_config, webdriver_module):
    # type: (SubRequest, dict, webdriver) -> typing.Generator[dict]
    test_name = request.node.name

    force_remote = request.config.getoption("remote", default=False)
    if "appiumVersion" in browser_config:
        force_remote = True

    if force_remote:
        sauce_url = "https://{username}:{password}@ondemand.saucelabs.com:443/wd/hub".format(
            username=os.getenv("SAUCE_USERNAME", None),
            password=os.getenv("SAUCE_ACCESS_KEY", None),
        )
        selenium_url = os.getenv("SELENIUM_SERVER_URL", sauce_url)
        logger.debug("SELENIUM_URL={}".format(selenium_url))

        desired_caps = browser_config.copy()
        desired_caps["build"] = os.getenv("BUILD_TAG", None)
        desired_caps["tunnelIdentifier"] = os.getenv("TUNNEL_IDENTIFIER", None)
        desired_caps["name"] = test_name

        browser = webdriver_module.Remote(
            command_executor=selenium_url, desired_capabilities=desired_caps
        )
    else:
        # Use local browser. Use ENV variable for driver binary or install if no one.
        driver_manager_class, webdriver_class, options = BROWSERS_WEBDRIVERS.get(
            browser_config["browserName"]
        )
        if options:
            headless = request.config.getoption("headless")
            options = options()
            options.headless = bool(headless)
        if driver_manager_class:
            browser = webdriver_class(
                executable_path=driver_manager_class().install(), options=options
            )
        else:
            browser = webdriver_class()

    if browser is None:
        raise WebDriverException("Never created!")

    yield browser

    # report results
    try:
        browser.execute_script(
            "sauce:job-result=%s" % str(not request.node.rep_call.failed).lower()
        )
    except WebDriverException:
        # we can ignore the exceptions of WebDriverException type -> We're done with tests.
        logger.info(
            "Warning: The driver failed to quit properly. Check test and server side logs."
        )
    finally:
        browser.quit()


@pytest.fixture
def vg_runner():
    vg = VisualGridRunner(10)
    return vg


@pytest.fixture
def batch_info():
    batch_info = BatchInfo("hello world batch")
    batch_info.id = "hw_VG_Batch_ID"
    return batch_info


@pytest.fixture
def eyes_vg(vg_runner, sel_config, driver, request, test_page_url):
    app_name = request.node.get_closest_marker("app_name")
    if app_name:
        app_name = app_name.args[0]
    test_name = request.node.get_closest_marker("test_name")
    if test_name:
        test_name = test_name.args[0]
    viewport_size = request.node.get_closest_marker("viewport_size")
    if viewport_size:
        viewport_size = viewport_size.args[0]
    else:
        viewport_size = None

    eyes = Eyes(vg_runner)
    eyes.server_url = "https://eyes.applitools.com/"
    eyes.configuration = sel_config

    app_name = app_name or eyes.configuration.app_name
    test_name = test_name or eyes.configuration.test_name
    viewport_size = viewport_size or eyes.configuration.viewport_size

    driver.get(test_page_url)
    eyes.open(driver, app_name, test_name, viewport_size)
    yield eyes
    logger.debug("closing WebDriver for url {}".format(test_page_url))
    eyes.close()
    # TODO: print VG test results
