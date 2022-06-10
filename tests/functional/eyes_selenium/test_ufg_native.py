import pytest
from appium.webdriver import Remote

from applitools.common import IosDeviceInfo, IosDeviceName, ScreenOrientation
from applitools.common.ultrafastgrid import (
    AndroidDeviceInfo,
    AndroidDeviceName,
    AndroidVersion,
)
from applitools.selenium import Eyes, VisualGridRunner


@pytest.mark.sauce
def test_ufg_native_ios_basic(sauce_driver_url):
    caps = {
        "app": "https://applitools.jfrog.io/artifactory/Examples/DuckDuckGo-instrumented.app.zip",
        "deviceName": "iPhone 12 Pro Simulator",
        "platformName": "iOS",
        "platformVersion": "15.2",
        "deviceOrientation": "portrait",
        "processArguments": {
            "args": [],
            "env": {
                "DYLD_INSERT_LIBRARIES": "@executable_path/Frameworks/UFG_lib.xcframework/ios-arm64_x86_64-simulator/UFG_lib.framework/UFG_lib"
            },
        },
    }
    with Remote(sauce_driver_url, caps) as driver:
        runner = VisualGridRunner()
        eyes = Eyes(runner)
        eyes.configure.add_mobile_device(
            IosDeviceInfo(IosDeviceName.iPhone_12, ScreenOrientation.PORTRAIT)
        )
        eyes.open(driver, "USDK Test", "UFG native iOS basic test")
        eyes.check_window()
        eyes.close()

        all_results = runner.get_all_test_results()

        assert all_results.passed == 1


@pytest.mark.skip("Skip until test working build of test app is available")
@pytest.mark.sauce
def test_ufg_android_basic(sauce_driver_url):
    caps = {
        "app": "https://applitools.jfrog.io/artifactory/Examples/ufg-native-example.apk",
        "deviceName": "Google Pixel 3a XL GoogleAPI Emulator",
        "platformVersion": "10.0",
        "platformName": "Android",
        "clearSystemFiles": True,
        "noReset": True,
        "automationName": "UiAutomator2",
        "name": "Pixel 3a xl (Python)",
        "appiumVersion": "1.20.2",
    }
    with Remote(sauce_driver_url, caps) as driver:
        runner = VisualGridRunner()
        eyes = Eyes(runner)
        eyes.configure.add_mobile_device(
            AndroidDeviceInfo(
                AndroidDeviceName.Pixel_4_XL, android_version=AndroidVersion.LATEST
            )
        )
        eyes.open(driver, "USDK Test", "UFG native Android basic test")
        eyes.check_window()
        eyes.close()

        all_results = runner.get_all_test_results()

        assert all_results.passed == 1
