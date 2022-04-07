import os

from appium.webdriver import Remote

from applitools.common import IosDeviceInfo, IosDeviceName, ScreenOrientation
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
