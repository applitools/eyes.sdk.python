import os
from time import sleep

import pytest
from appium.webdriver import Remote

from applitools.common import (
    AndroidDeviceInfo,
    AndroidDeviceName,
    AndroidVersion,
    BatchInfo,
    IosDeviceInfo,
    IosDeviceName,
    ProxySettings,
    ScreenOrientation,
)
from applitools.selenium import Eyes, Target, VisualGridRunner

batch = BatchInfo("Python E2E UFG Native")


@pytest.fixture(scope="function")
def driver(request):
    platform, version, locality, orientation = request.param.split(" ")
    assert platform in ("android", "ios")
    assert locality in ("local", "sauce")
    assert orientation in ("portrait", "landscape")
    if locality == "local":
        driver_url = "http://localhost:4723/wd/hub"
        ios_device_name = "iPhone 12 Pro"
    else:
        driver_url = "https://{}:{}@ondemand.saucelabs.com:443/wd/hub".format(
            os.environ["SAUCE_USERNAME"], os.environ["SAUCE_ACCESS_KEY"]
        )
        ios_device_name = "iPhone 12 Pro Simulator"
    if platform == "android":
        caps = {
            "app": "https://applitools.jfrog.io/artifactory/Examples/"
            "duckduckgo-5.87.0-play-debug_latest.apk",
            "appPackage": "com.duckduckgo.mobile.android.debug",
            "appActivity": "com.duckduckgo.app.launch.Launcher",
            "deviceName": "Google Pixel 3a XL GoogleAPI Emulator",
            "autoGrantPermissions": True,
            "platformVersion": version,
            "platformName": "Android",
            "clearSystemFiles": True,
            "noReset": True,
            "automationName": "UiAutomator2",
            "name": "Pixel 3a xl (Python)",
            "appiumVersion": "1.20.2",
            "sauce:options": {"name": "{} {}".format(batch.name, request.node.name)},
        }
    else:
        caps = {
            "app": "https://applitools.jfrog.io/artifactory/Examples/"
            "DuckDuckGo-instrumented.app.zip",
            "deviceName": ios_device_name,
            "platformName": "iOS",
            "platformVersion": version,
            "processArguments": {
                "args": [],
                "env": {
                    "DYLD_INSERT_LIBRARIES": "@executable_path/Frameworks/UFG_lib.xcframework/"
                    "ios-arm64_x86_64-simulator/UFG_lib.framework/UFG_lib"
                },
            },
            "deviceOrientation": orientation.upper(),
        }
    with Remote(driver_url, caps) as driver:
        if locality == "sauce":
            driver.execute_script(
                "sauce:job-name={} {}".format(batch.name, request.node.name)
            )
        if platform == "android":
            driver.orientation = orientation
        sleep(5)
        yield driver


@pytest.fixture(scope="function")
def eyes(driver):
    eyes = Eyes(VisualGridRunner())
    orientation = ScreenOrientation(driver.orientation.lower())
    if driver.capabilities["platformName"].lower() == "ios":
        eyes.configure.add_mobile_device(
            IosDeviceInfo(IosDeviceName.iPhone_8, orientation)
        )
        eyes.configure.add_mobile_device(
            IosDeviceInfo(IosDeviceName.iPhone_SE, orientation)
        )
    else:
        eyes.configure.add_mobile_device(
            AndroidDeviceInfo(AndroidDeviceName.Pixel_4_XL, orientation)
        )
    eyes.configure.set_batch(batch)
    yield eyes


all_combinations = [
    " ".join((plat, loc, orient))
    for loc in ("local", "sauce")
    for plat in ("android 10", "ios 15.2")
    for orient in ("portrait", "landscape")
]


@pytest.mark.parametrize("driver", all_combinations, indirect=True)
def test_check_main_screen_fully(driver, eyes, request):
    eyes.open(driver, "E2E suite", request.node.name)
    eyes.check(Target.window())
    eyes.close()


@pytest.mark.parametrize("driver", all_combinations, indirect=True)
def test_check_main_screen_non_fully(driver, eyes, request):
    eyes.open(driver, "E2E suite", request.node.name)
    eyes.check(Target.window().fully(False))
    eyes.close()


@pytest.mark.parametrize("driver", all_combinations, indirect=True)
def test_check_main_two_checks(driver, eyes, request):
    eyes.open(driver, "E2E suite", request.node.name)
    eyes.check(Target.window())
    eyes.check(Target.window())
    eyes.close()


@pytest.mark.parametrize(
    "driver", ["android 10 local portrait", "ios 15.2 local portrait"], indirect=True
)
def test_check_main_check_via_proxy(driver, eyes, request):
    eyes.configure.set_proxy(ProxySettings("192.168.31.11", 9090))
    eyes.open(driver, "E2E suite", request.node.name)
    eyes.check(Target.window())
    eyes.close()
