import os
import sys
from collections import namedtuple
from itertools import chain

import pytest
from common_fixtures import *  # noqa

try:
    from typing import Text, Optional, Generator, Iterable
except ImportError:
    pass


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
        + [("internet explorer", "latest"), ("MicrosoftEdge", "latest")],
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


def pytest_addoption(parser):
    parser.addoption("--platform", action="store")
    parser.addoption("--browser", action="store")
    parser.addoption("--headless", action="store")
    parser.addoption("--remote", action="store")


def _get_capabilities(platform_name=None, browser_name=None, headless=False):
    if platform_name is None:
        sys2platform_name = {
            "linux": "Linux",
            "linux2": "Linux",
            "darwin": "macOS 10.14",
            "win32": "Windows 10",
        }
        platform_name = sys2platform_name[sys.platform]
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
    platform_name = metafunc.config.getoption("platform")
    browser_name = metafunc.config.getoption("browser", "chrome")
    headless = metafunc.config.getoption("headless")

    _setup_env_vars_for_session()

    if platform_name or browser_name:
        desired_caps = _get_capabilities(platform_name, browser_name, headless)
    else:
        desired_caps = []
        platforms = getattr(metafunc.function, "platform", [])
        if platforms:
            platforms = platforms.args

        for platform in SUPPORTED_PLATFORMS:
            if platform.name not in platforms:
                continue
            desired_caps.extend(
                _get_capabilities(platform.full_name, headless=headless)
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
