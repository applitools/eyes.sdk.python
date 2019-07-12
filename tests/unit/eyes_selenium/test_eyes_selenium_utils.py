import mock
import pytest
from appium.webdriver import Remote as AppiumWebDriver

from applitools.selenium import eyes_selenium_utils


@pytest.mark.parametrize(
    "platform_name",
    [
        "Android",
        "android",
        " Android",
        "androId ",
        "android 6",
        "iOs",
        "ios",
        "IOS",
        "ios 11",
    ],
)
def test_different_mobile_platform_names(driver_mock, platform_name):
    driver_mock.desired_capabilities["platformName"] = platform_name
    driver_mock.desired_capabilities["browserName"] = "someBrowser"
    assert eyes_selenium_utils.is_mobile_web(driver_mock)
    assert not eyes_selenium_utils.is_mobile_app(driver_mock)


@pytest.mark.parametrize("platform_name", ["Windows", "Winmo", "Linux", "macOs"])
def test_different_not_mobile_platform_names(driver_mock, platform_name):
    driver_mock.desired_capabilities["platformName"] = platform_name
    driver_mock.desired_capabilities["browserName"] = "someBrowser"
    assert not eyes_selenium_utils.is_mobile_web(driver_mock)
    assert not eyes_selenium_utils.is_mobile_app(driver_mock)
    assert not eyes_selenium_utils.is_mobile_platform(driver_mock)


def test_appium_webdriver(driver_mock):
    driver_mock._driver = mock.Mock(AppiumWebDriver)
    assert eyes_selenium_utils.is_mobile_platform(driver_mock)


@pytest.mark.parametrize("platform_name", ["Android", "ios 11"])
def test_using_mobile_app(driver_mock, platform_name):
    driver_mock.desired_capabilities["app"] = "some_app"
    driver_mock.desired_capabilities["platformName"] = platform_name
    assert eyes_selenium_utils.is_mobile_app(driver_mock)
    assert not eyes_selenium_utils.is_mobile_web(driver_mock)
