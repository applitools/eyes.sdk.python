import mock
import pytest
from appium.webdriver import Remote as AppiumWebDriver

from applitools.common import EyesError
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
@pytest.mark.parametrize(
    "param", ["app", "appActivity", "appPackage", "bundleId", "appName"]
)
def test_using_mobile_app(driver_mock, platform_name, param):
    driver_mock.desired_capabilities[param] = "some_app"
    driver_mock.desired_capabilities["platformName"] = platform_name
    assert eyes_selenium_utils.is_mobile_app(driver_mock)
    assert not eyes_selenium_utils.is_mobile_web(driver_mock)


def test_get_app_name_missing(driver_mock):
    assert eyes_selenium_utils.get_app_name(driver_mock) is None


def test_get_app_name_android(driver_mock):
    driver_mock.desired_capabilities["appPackage"] = "com.example.appid"

    assert eyes_selenium_utils.get_app_name(driver_mock) == "com.example.appid"


def test_get_app_name_ios(driver_mock):
    driver_mock.desired_capabilities["app"] = "https://host/dir/app_1_0.zip"

    assert eyes_selenium_utils.get_app_name(driver_mock) == "app_1_0.zip"


def test_get_app_domain(driver_mock):
    driver_mock.current_url = "https://example.com/page.html"

    assert eyes_selenium_utils.get_webapp_domain(driver_mock) == "example.com"


def test_check_source_mobile(driver_mock):
    driver_mock.desired_capabilities["appPackage"] = "com.example.appid"
    driver_mock.desired_capabilities["platformName"] = "Android"

    assert eyes_selenium_utils.get_check_source(driver_mock) == "com.example.appid"


def test_get_check_source_source_web(driver_mock):
    driver_mock.current_url = "https://example.com/page.html"

    assert eyes_selenium_utils.get_check_source(driver_mock) == "example.com"


def test_set_viewport_size_minimize_window_called(driver_mock):
    driver_mock.minimize_window = mock.Mock()
    set_browser_size_by_viewport_size = mock.Mock()
    set_browser_size_by_viewport_size.side_effect = [
        {"width": 600, "height": 850},
        {"width": 600, "height": 650},
    ]

    with mock.patch(
        "applitools.selenium.eyes_selenium_utils.get_viewport_size",
        return_value={"width": 600, "height": 850},
    ):
        with mock.patch(
            "applitools.selenium.eyes_selenium_utils.set_browser_size_by_viewport_size",
            new=set_browser_size_by_viewport_size,
        ):
            eyes_selenium_utils.set_viewport_size(
                driver_mock, {"width": 600, "height": 650}
            )
    assert driver_mock.minimize_window.called
