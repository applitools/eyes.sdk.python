from __future__ import absolute_import

import os
import re
import sys
import typing
from collections import namedtuple
from distutils.util import strtobool
from itertools import chain

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import IEDriverManager

from applitools.selenium import Configuration, Eyes, StitchMode, logger
from applitools.selenium.__version__ import __version__
from applitools.selenium.visual_grid import VisualGridRunner
from tests.functional.eyes_selenium.selenium_utils import open_webdriver

try:
    from typing import TYPE_CHECKING, Generator, Iterable, Optional, Text
except ImportError:
    TYPE_CHECKING = False
    pass


if TYPE_CHECKING:
    from _pytest.fixtures import SubRequest

BROWSERS_WEBDRIVERS = {
    "firefox": (GeckoDriverManager, webdriver.Firefox, webdriver.FirefoxOptions),
    "chrome": (
        lambda: ChromeDriverManager(version="90.0.4430.24"),
        webdriver.Chrome,
        webdriver.ChromeOptions,
    ),
    "internet explorer": (IEDriverManager, webdriver.Ie, webdriver.IeOptions),
    "safari": (None, webdriver.Safari, None),
}

sys2platform_name = {
    "linux": "Linux",
    "linux2": "Linux",
    "darwin": "macOS 10.14",
    "win32": "Windows 10",
}


@pytest.fixture
def eyes_class():
    return Eyes


@pytest.fixture
def webdriver_module():
    return webdriver


def underscore_to_camelcase(text):
    return re.sub(r"(?:^|_)([a-z])", lambda m: m.group(1).upper(), text)


@pytest.fixture
def eyes_config_base():
    return (
        Configuration()
        .set_hide_scrollbars(True)
        .set_save_new_tests(False)
        .set_hide_caret(True)
    )


@pytest.fixture(scope="function")
def eyes_opened(request, eyes, driver, check_test_result):
    viewport_size = request.node.get_closest_marker("viewport_size")
    viewport_size = viewport_size.args[-1] if viewport_size else None

    test_suite_name = request.node.get_closest_marker("test_suite_name")
    test_suite_name = (
        test_suite_name.args[-1] if test_suite_name else "Python Selenium SDK"
    )
    # use camel case in method name for fit java sdk tests name if no test_name
    test_name = request.node.get_closest_marker("test_name")
    test_name = (
        test_name.args[-1]
        if test_name
        else underscore_to_camelcase(request.function.__name__)
    )

    eyes.add_property("Selenium Session ID", str(driver.session_id))
    eyes.add_property(
        "ForceFPS", "true" if eyes.force_full_page_screenshot else "false"
    )
    if isinstance(eyes._runner, VisualGridRunner):
        test_name += "_VG"
    elif eyes.stitch_mode == StitchMode.Scroll:
        test_name += "_Scroll"

    eyes.open(driver, test_suite_name, test_name, viewport_size=viewport_size)
    yield eyes
    test_result = eyes.close()
    check_test_result.send(test_result)


@pytest.yield_fixture(scope="function")
def driver(request, browser_config, webdriver_module):
    # type: (SubRequest, dict, webdriver) -> typing.Generator[dict]
    test_name = request.node.name
    test_page_url = request.node.get_closest_marker("test_page_url")
    test_page_url = test_page_url.args[-1] if test_page_url else None
    capabilities = request.node.get_closest_marker("capabilities")
    capabilities = capabilities.kwargs if capabilities else {}

    force_remote = bool(os.getenv("TEST_REMOTE", False))
    if "appiumVersion" in browser_config:
        force_remote = True

    if force_remote:
        sauce_url = (
            "https://{username}:{password}@ondemand.saucelabs.com:443/wd/hub".format(
                username=os.getenv("SAUCE_USERNAME", None),
                password=os.getenv("SAUCE_ACCESS_KEY", None),
            )
        )
        selenium_url = os.getenv("SELENIUM_SERVER_URL", sauce_url)
        logger.debug("SELENIUM_URL={}".format(selenium_url))

        desired_caps = browser_config.copy()
        desired_caps["build"] = os.getenv("BUILD_TAG", None)
        desired_caps["tunnelIdentifier"] = os.getenv("TUNNEL_IDENTIFIER", None)
        desired_caps.update(capabilities)
        desired_caps["name"] = test_name

        browser = open_webdriver(
            lambda: webdriver_module.Remote(
                command_executor=selenium_url, desired_capabilities=desired_caps
            ),
        )
    else:
        # Use local browser. Use ENV variable for driver binary or install if no one.
        driver_manager_class, webdriver_class, options = BROWSERS_WEBDRIVERS.get(
            browser_config["browserName"]
        )
        if options:
            headless = strtobool(os.getenv("TEST_BROWSER_HEADLESS", "True"))
            options = options()
            options.headless = bool(headless)

        if driver_manager_class:
            browser = open_webdriver(
                lambda: webdriver_class(
                    executable_path=driver_manager_class().install(),
                    options=options,
                ),
            )
        else:
            browser = open_webdriver(webdriver_class)

    if test_page_url:
        browser.get(test_page_url)
        logger.info("navigation to URL: {}".format(test_page_url))

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

        from selenium.webdriver import ChromeOptions, FirefoxOptions

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
        # print(
        #     "browser_name: {}\ncaps: {}\n self.browsers: {}".format(
        #         browser_name, browser_caps, self.browsers
        #     )
        # )
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
    Platform(name="iOS", version="", browsers=[], extra={"appiumVersion": "1.17.1"}),
    Platform(
        name="Android", version="", browsers=[], extra={"appiumVersion": "1.17.1"}
    ),
]
SUPPORTED_PLATFORMS_DICT = {
    platform.full_name: platform for platform in SUPPORTED_PLATFORMS
}
SUPPORTED_BROWSERS = set(
    chain(*[platform.browsers for platform in SUPPORTED_PLATFORMS])
)


def _get_capabilities(platform_name=None, browser_name=None, headless=False):
    platform = SUPPORTED_PLATFORMS_DICT[platform_name.strip('"')]
    if platform.is_appium_based:
        capabilities = [platform.platform_capabilities()]
    else:
        if browser_name:
            return [platform.get_browser_capabilities(browser_name, headless)]
        capabilities = list(platform.browsers_capabilities(headless))
    return capabilities


def _setup_env_vars_for_session():
    os.environ["APPLITOOLS_BATCH_NAME"] = "Py|Sel|{}|{}".format(
        __version__, os.getenv("TEST_PLATFORM")
    )


def pytest_generate_tests(metafunc):
    headless = strtobool(os.getenv("TEST_BROWSER_HEADLESS", "True"))

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
    platform_env = os.getenv("TEST_PLATFORM")
    if platform_marker and platform_env:
        platforms = platform_marker.args
        cmd_platform = platform_env.split()[0]  # remove platform version
        if cmd_platform and cmd_platform not in platforms:
            pytest.skip("test runs on platforms: %s" % " ".join(platforms))

    browser_marker = item.get_closest_marker("browser")
    browsers_env = os.getenv("TEST_BROWSERS", "").split(",")
    if browser_marker and browsers_env:
        browsers = browser_marker.args
        if bool(set(browsers_env).intersection(set(browsers))):
            pytest.skip("test requires browsers %s" % browsers_env)
