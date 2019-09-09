import os
import sys
import typing
from collections import namedtuple
from itertools import chain

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

try:
    from typing import Text, Optional, Generator, Iterable, TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False
    pass


if TYPE_CHECKING:
    from _pytest.fixtures import SubRequest

BROWSERS_WEBDRIVERS = {
    "firefox": (GeckoDriverManager, webdriver.Firefox, webdriver.FirefoxOptions),
    "chrome": (ChromeDriverManager, webdriver.Chrome, webdriver.ChromeOptions),
    "internet explorer": (IEDriverManager, webdriver.Ie, webdriver.IeOptions),
    "MicrosoftEdge": (EdgeDriverManager, webdriver.Edge, None),
    "safari": (None, webdriver.Safari, None),
}

sys2platform_name = {
    "linux": "Linux",
    "linux2": "Linux",
    "darwin": "macOS 10.14",
    "win32": "Windows 10",
}


def _setup_env_vars_for_session():
    os.environ["APPLITOOLS_BATCH_NAME"] = "Py|Sel|{}".format(__version__)


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

    batch_name = os.getenv("APPLITOOLS_BATCH_NAME")
    eyes.configuration.batch = BatchInfo(
        "{}|{}|{}".format(
            batch_name,
            os.getenv("TEST_PLATFORM", sys.platform.capitalize()),
            "Rem" if bool(os.getenv("TEST_REMOTE")) else "Loc",
        )
    )
    if eyes.force_full_page_screenshot:
        test_suite_name += " - ForceFPS"
        test_name += "_FPS"
    eyes_driver = eyes.open(
        driver, test_suite_name, test_name, viewport_size=viewport_size
    )
    eyes_driver.get(test_page_url)

    yield eyes, eyes_driver
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

    force_remote = request.config.getoption("remote")
    if force_remote is None:
        force_remote = bool(os.getenv("TEST_REMOTE", False))
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


class Platform(namedtuple("Platform", "name version browsers extra")):
    def platform_capabilities(self):
        # type: () -> Optional[Iterable[dict]]
        """
        Get capabilities for mobile platform
        """
        if not self.is_appium_based:
            return

        caps = {"platformName": self.name, "platformVersion": self.version}
        if isinstance(self.extra, dict):
            caps.update(self.extra)
        return caps

    def browsers_capabilities(self, headless=False):
        # type: (bool) -> Generator[dict]
        """
        Get all browsers capabilities for the platform
        :rtype: collections.Iterable[dict]
        """
        for browser_name, _ in self.browsers:
            yield self.get_browser_capabilities(browser_name, headless)

    def get_browser_capabilities(self, browser_name, headless=False):
        # type: (Text, bool) -> Optional[dict]
        """
        Get browser capabilities for specific browser with included options inside

        :param browser_name: browser name in lowercase
        :param headless: run browser without gui
        :return: capabilities for specific browser
        """
        if self.is_appium_based:
            return

        from selenium.webdriver import FirefoxOptions
        from selenium.webdriver import ChromeOptions

        # clean up from quotes for correct comparision; original bug on Windows where
        # string contains quotes
        browser_name = browser_name.strip("\"' ")

        options = None
        if "firefox" == browser_name:
            options = FirefoxOptions()
        elif "chrome" == browser_name:
            options = ChromeOptions()
            options.add_argument("disable-infobars")
        if options and headless:
            options.headless = True

        # huck for preventing overwriting 'platform' value in desired_capabilities by chrome options
        browser_caps = options.to_capabilities() if options else {}
        print(
            "browser_name: {}\ncaps: {}\n self.browsers: {}".format(
                browser_name, browser_caps, self.browsers
            )
        )
        browser_name, browser_version = [
            b for b in self.browsers if browser_name.lower() == b[0].lower()
        ][0]

        browser_caps.update(
            {
                "browserName": browser_name,
                "version": browser_version,
                "platform": self.full_name,
            }
        )
        if isinstance(self.extra, dict):
            browser_caps.update(self.extra)
        return browser_caps

    @property
    def is_appium_based(self):
        if self.extra and ("appiumVersion" in self.extra or "deviceName" in self.extra):
            return True
        return False

    @property
    def full_name(self):
        if self.version:
            return "{} {}".format(self.name, self.version)
        return self.name


COMMON_BROWSERS = [("chrome", "latest"), ("firefox", "latest")]
SUPPORTED_PLATFORMS = [
    Platform(
        name="Windows",
        version="10",
        browsers=COMMON_BROWSERS
        + [
            ("internet explorer", "latest"),
            # ("MicrosoftEdge", "latest")
        ],
        extra=None,
    ),
    Platform(name="Linux", version="", browsers=COMMON_BROWSERS, extra=None),
    Platform(
        name="macOS",
        version="10.14",
        browsers=COMMON_BROWSERS + [("safari", "latest")],
        extra=None,
    ),
    Platform(
        name="iOS",
        version="11.3",
        browsers=[],
        extra={
            "appiumVersion": "1.9.1",
            "deviceName": "Iphone Simulator",
            "deviceOrientation": "portrait",
            "browserName": "Safari",
        },
    ),
    Platform(
        name="Android",
        version="6.0",
        browsers=[],
        extra={
            "appiumVersion": "1.9.1",
            "deviceName": "Android Emulator",
            "deviceOrientation": "portrait",
            "browserName": "Chrome",
            "newCommandTimeout": 60 * 5,
        },
    ),  # Platform(name='Android', version='7.0', browsers=[], extra={
    #     "appiumVersion":     "1.9.1",
    #     "deviceName":        "Android Emulator",
    #     "deviceOrientation": "portrait",
    #     "browserName":       "Chrome",
    #     "newCommandTimeout": 60 * 5
    # }),
    # Platform(
    #     name="Android",
    #     version="9",
    #     browsers=[],
    #     extra={
    #         "appiumVersion": "1.9.1",
    #         "deviceName": "Samsung S9+",
    #         "deviceOrientation": "portrait",
    #         "browserName": "Chrome",
    #         "newCommandTimeout": 60 * 5,
    #     },
    # ),
]
SUPPORTED_PLATFORMS_DICT = {
    platform.full_name: platform for platform in SUPPORTED_PLATFORMS
}
SUPPORTED_BROWSERS = set(
    chain(*[platform.browsers for platform in SUPPORTED_PLATFORMS])
)


def _get_capabilities(platform_name=None, browser_name=None, headless=False):
    platform = SUPPORTED_PLATFORMS_DICT[platform_name]
    if platform.is_appium_based:
        capabilities = [platform.platform_capabilities()]
    else:
        if browser_name:
            return [platform.get_browser_capabilities(browser_name, headless)]
        capabilities = list(platform.browsers_capabilities(headless))
    return capabilities


def _setup_env_vars_for_session():
    import uuid

    # setup environment variables once per test run if not settled up
    # needed for multi thread run
    os.environ["APPLITOOLS_BATCH_ID"] = os.getenv(
        "APPLITOOLS_BATCH_ID", str(uuid.uuid4())
    )


def pytest_generate_tests(metafunc):
    headless = os.getenv("TEST_BROWSER_HEADLESS", True)

    platform_name = os.getenv("TEST_PLATFORM", None)
    if platform_name is None:
        platform_name = sys2platform_name[sys.platform]
        os.environ["TEST_PLATFORM"] = platform_name
    browsers = os.getenv("TEST_BROWSERS", "")

    _setup_env_vars_for_session()

    if platform_name:
        browsers = browsers.split(",")
        desired_caps = []
        for b_name in browsers:
            desired_caps.extend(_get_capabilities(platform_name, b_name, headless))
    else:
        raise ValueError(
            "Wrong parameters passed: "
            "\n\tplatform_name: {}"
            "\n\tbrowsers: {}".format(platform_name, browsers)
        )

    # update capabilities from capabilities marker
    if hasattr(metafunc, "function"):
        func_capabilities = getattr(metafunc.function, "capabilities", {})
        if func_capabilities:
            for caps in desired_caps:
                caps.update(func_capabilities.kwargs)

    # generate combinations of driver options before run
    if "driver" in metafunc.fixturenames:
        metafunc.parametrize(
            "browser_config",
            desired_caps,
            ids=_generate_param_ids(desired_caps),
            scope="function",
        )


def _generate_param_ids(desired_caps):
    results = []
    for caps in desired_caps:
        platform = caps.get("platform")
        browser = caps.get("browserName", "")
        if platform:
            browser_version = caps.get("version", "")
            browser += str(browser_version)
        else:
            platform = caps.get("platformName")
            platform_version = caps.get("version", "")
            platform += platform_version
        results.append("platform: {}, browser: {}".format(platform, browser))
    return results


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # this sets the result as a test attribute for SauceLabs reporting.
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set an report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)


def pytest_runtest_setup(item):
    """Skip tests that not fit for selected platform"""
    platform_marker = item.get_closest_marker("platform")
    platform_cmd = item.config.getoption("platform")
    if platform_marker and platform_cmd:
        platforms = platform_marker.args
        cmd_platform = platform_cmd.split()[0]  # remove platform version
        if cmd_platform and cmd_platform not in platforms:
            pytest.skip("test requires platform %s" % cmd_platform)

    browser_marker = item.get_closest_marker("browser")
    browser_cmd = item.config.getoption("browser")
    if browser_marker and browser_cmd:
        browsers = browser_marker.args
        if browser_cmd and browser_cmd not in browsers:
            pytest.skip("test requires browser %s" % browser_cmd)
