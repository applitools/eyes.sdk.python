import os
from time import sleep

import pytest
from appium.webdriver import Remote
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.ui import WebDriverWait

from applitools.common import (
    AndroidDeviceInfo,
    AndroidDeviceName,
    BatchInfo,
    IosDeviceInfo,
    IosDeviceName,
    ProxySettings,
    ScreenOrientation,
)
from applitools.selenium import ClassicRunner, Eyes, Target, VisualGridRunner

batch = BatchInfo("Python E2E UFG Native")


def parametrize(**kwargs):
    def apply(test_func):
        for param, values in kwargs.items():
            test_func = pytest.mark.parametrize(param, values, indirect=True)(test_func)
        return test_func

    return apply


@pytest.fixture(scope="module")
def vg_runner():
    runner = VisualGridRunner()
    try:
        yield runner
    finally:
        runner.get_all_test_results(False)


@pytest.fixture(scope="module")
def classic_runner():
    runner = ClassicRunner()
    try:
        yield runner
    finally:
        runner.get_all_test_results(False)


@pytest.fixture
def platform(request):
    assert request.param in ("android", "ios")
    return request.param


@pytest.fixture
def locality(request):
    assert request.param in ("local", "sauce")
    return request.param


@pytest.fixture
def orientation(request):
    assert request.param in ("portrait", "landscape")
    return request.param


@pytest.fixture
def runner(vg_runner, classic_runner, request):
    assert request.param in ("classic", "vg")
    return request.param


@pytest.fixture
def driver(platform, locality, orientation, request):
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
            "platformVersion": "10",
            "platformName": "Android",
            "clearSystemFiles": True,
            "automationName": "UiAutomator2",
            "name": "Pixel 3a xl (Python)",
            "appiumVersion": "1.20.2",
        }
    else:
        caps = {
            "app": "https://applitools.jfrog.io/artifactory/Examples/"
            "DuckDuckGo-instrumented.app.zip",
            "deviceName": ios_device_name,
            "platformName": "iOS",
            "platformVersion": "15.2",
            "processArguments": {
                "args": [],
                "env": {
                    "DYLD_INSERT_LIBRARIES": "@executable_path/Frameworks/UFG_lib.xcframework/"
                    "ios-arm64_x86_64-simulator/UFG_lib.framework/UFG_lib"
                },
            },
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


@pytest.fixture
def eyes(platform, orientation, driver, runner, classic_runner, vg_runner):
    orientation = ScreenOrientation(orientation)
    eyes = Eyes(vg_runner if runner == "vg" else classic_runner)
    if runner == "vg":
        if platform == "ios":
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


@parametrize(
    locality=["local", "sauce"],
    platform=["android", "ios"],
    orientation=["portrait", "landscape"],
    runner=["classic", "vg"],
)
def test_check_main_screen_fully(driver, eyes, request):
    eyes.open(driver, "E2E suite", request.node.name)
    eyes.check(Target.window())
    eyes.close()


@parametrize(
    locality=["local"],
    platform=["android", "ios"],
    orientation=["portrait", "landscape"],
    runner=["classic", "vg"],
)
def test_check_main_screen_non_fully(driver, eyes, request):
    eyes.open(driver, "E2E suite", request.node.name)
    eyes.check(Target.window().fully(False))
    eyes.close()


@parametrize(
    locality=["local"],
    platform=["android", "ios"],
    orientation=["portrait", "landscape"],
    runner=["classic", "vg"],
)
def test_check_main_two_checks(driver, eyes, request):
    eyes.open(driver, "E2E suite", request.node.name)
    eyes.check(Target.window())
    eyes.check(Target.window().fully(False))
    eyes.close()


@parametrize(
    locality=["local"],
    platform=["android", "ios"],
    orientation=["portrait"],
    runner=["classic", "vg"],
)
def test_check_main_check_via_proxy(driver, eyes, request):
    eyes.configure.set_proxy(ProxySettings("192.168.31.11", 9090))
    eyes.open(driver, "E2E suite", request.node.name)
    eyes.check(Target.window())
    eyes.close()


@parametrize(
    locality=["local"],
    platform=["android", "ios"],
    orientation=["portrait", "landscape"],
    runner=["classic", "vg"],
)
def test_check_search_results_fully(platform, driver, eyes, request):
    if platform == "ios":
        duckduckgo_search_ios(driver, "Tor")
    else:
        duckduckgo_search_android(driver, "Tor")
    eyes.open(driver, "E2E suite", request.node.name)
    eyes.check(Target.window())
    eyes.close()


@parametrize(
    locality=["local"], platform=["ios"], orientation=["portrait"], runner=["classic"]
)
def test_check_search_results_region(platform, driver, eyes, request):
    duckduckgo_search_ios(driver, "Tor")
    region = [MobileBy.XPATH, "//XCUIElementTypeWebView"]
    eyes.open(driver, "E2E suite", request.node.name)
    eyes.check(Target.region(region).fully())
    eyes.close()


def wait_for_element(driver, strategy, locator):
    wait = WebDriverWait(driver, 20)
    return wait.until(presence_of_element_located((strategy, locator)))


def duckduckgo_search_ios(driver, query):
    wait_for_element(
        driver,
        MobileBy.IOS_PREDICATE,
        'label == "Let’s Do It!" AND type == "XCUIElementTypeButton"',
    ).click()
    wait_for_element(
        driver,
        MobileBy.IOS_PREDICATE,
        'label == "Skip" AND type == "XCUIElementTypeButton"',
    ).click()
    wait_for_element(driver, MobileBy.IOS_PREDICATE, 'name == "searchEntry"').send_keys(
        query + "\n"
    )
    sleep(1)
    wait_for_element(
        driver,
        MobileBy.IOS_PREDICATE,
        'label == "Phew!" AND name == "Phew!" AND type == "XCUIElementTypeButton"',
    ).click()
    wait_for_element(driver, MobileBy.XPATH, "//XCUIElementTypeWebView")


def duckduckgo_search_android(driver, query):
    wait_for_element(
        driver, MobileBy.ID, "com.duckduckgo.mobile.android.debug:id/primaryCta"
    ).click()
    wait_for_element(driver, MobileBy.ID, "android:id/button2").click()
    wait_for_element(
        driver, MobileBy.ID, "com.duckduckgo.mobile.android.debug:id/omnibarTextInput"
    ).send_keys(query)
    driver.press_keycode(0x42)
    sleep(5)
    wait_for_element(
        driver, MobileBy.ID, "com.duckduckgo.mobile.android.debug:id/primaryCta"
    ).click()
