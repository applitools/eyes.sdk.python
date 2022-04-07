import os

from appium.webdriver import Remote

from applitools.common import IosDeviceInfo, IosDeviceName, ScreenOrientation
from applitools.common.ultrafastgrid import (
    AndroidDeviceInfo,
    AndroidDeviceName,
    AndroidVersion,
)
from applitools.selenium import Eyes, VisualGridRunner


def test_ufg_native_ios_basic():
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
    sauce_url = (
        "https://{username}:{password}@ondemand.saucelabs.com:443/wd/hub".format(
            username=os.environ["SAUCE_USERNAME"],
            password=os.environ["SAUCE_ACCESS_KEY"],
        )
    )
    with Remote(sauce_url, caps) as driver:
        runner = VisualGridRunner()
        eyes = Eyes(runner)
        eyes.configure.add_browser(
            IosDeviceInfo(IosDeviceName.iPhone_12, ScreenOrientation.PORTRAIT)
        )
        eyes.open(driver, "USDK Test", "UFG native iOS basic test")
        eyes.check_window()
        eyes.close(False)


def test_ufg_android_basic():
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
    sauce_url = (
        "https://{username}:{password}@ondemand.saucelabs.com:443/wd/hub".format(
            username=os.environ["SAUCE_USERNAME"],
            password=os.environ["SAUCE_ACCESS_KEY"],
        )
    )
    with Remote(sauce_url, caps) as driver:
        runner = VisualGridRunner()
        eyes = Eyes(runner)
        eyes.configure.add_browser(
            AndroidDeviceInfo(
                AndroidDeviceName.Pixel_4_XL, android_version=AndroidVersion.LATEST
            )
        )
        eyes.open(driver, "USDK Test", "UFG native Android basic test")
        eyes.check_window()
        eyes.close(False)
