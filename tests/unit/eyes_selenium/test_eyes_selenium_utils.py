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
    assert eyes_selenium_utils.is_mobile_device(driver_mock)


@pytest.mark.parametrize("platform_name", ["Windows", "Winmo", "Linux", "macOs"])
def test_different_not_mobile_platform_names(driver_mock, platform_name):
    driver_mock.desired_capabilities["platformName"] = platform_name
    assert not eyes_selenium_utils.is_mobile_device(driver_mock)


def test_appium_webdriver(driver_mock):
    driver_mock.driver = mock.Mock(AppiumWebDriver)
    assert eyes_selenium_utils.is_mobile_device(driver_mock)
