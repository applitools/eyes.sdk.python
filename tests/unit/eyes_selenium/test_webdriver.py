import pytest
from mock import MagicMock

from applitools.selenium import EyesWebDriver
from applitools.selenium.useragent import OSNames


@pytest.mark.parametrize("version, major, minor", [("9", 9, -1), ("9.1", 9, 1)])
def test_driver_useragent_splits_version(version, major, minor):
    driver_mock, eyes_mock = MagicMock(), MagicMock()
    driver_mock.desired_capabilities = {
        "platformName": "Android",
        "deviceName": "Pixel",
        "platformVersion": version,
        "app": "a.apk",
    }
    webderiver = EyesWebDriver(driver_mock, eyes_mock)

    assert webderiver.user_agent.os_major_version == major
    assert webderiver.user_agent.os_minor_version == minor


def test_driver_app_useragent_lowercase_os():
    driver_mock, eyes_mock = MagicMock(), MagicMock()
    driver_mock.desired_capabilities = {
        "app": "1.zip",
        "platformName": "ios",
        "platformVersion": "13.4",
        "automationName": "XCUITest",
        "appiumVersion": "1.17.1",
        "deviceName": "iPhone XR Simulator",
        "deviceOrientation": "portrait",
    }
    webderiver = EyesWebDriver(driver_mock, eyes_mock)

    assert webderiver.user_agent.os == OSNames.IOS
    assert webderiver.user_agent.os_major_version == 13
    assert webderiver.user_agent.os_minor_version == 4
