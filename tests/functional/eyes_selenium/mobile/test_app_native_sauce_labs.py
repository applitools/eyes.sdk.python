import os
from copy import copy

import pytest
from appium import webdriver as appium_webdriver
from mock import patch
from selenium.common.exceptions import WebDriverException

from applitools.common import logger
from applitools.selenium import Target, Region
from tests.functional.eyes_selenium.selenium_utils import open_webdriver


@pytest.yield_fixture(scope="function")
def mobile_eyes(request, eyes, ios_desired_capabilities, android_desired_capabilities):
    selenium_url = (
        "https://{username}:{password}@ondemand.saucelabs.com:443/wd/hub".format(
            username=os.getenv("SAUCE_USERNAME", None),
            password=os.getenv("SAUCE_ACCESS_KEY", None),
        )
    )
    platform_name = os.getenv("TEST_PLATFORM", None)
    if platform_name == "Android":
        desired_caps = android_desired_capabilities
    else:
        desired_caps = ios_desired_capabilities

    mobile_driver = open_webdriver(
        lambda: appium_webdriver.Remote(
            command_executor=selenium_url, desired_capabilities=desired_caps
        ),
    )
    if mobile_driver is None:
        raise WebDriverException("Never created!")

    yield eyes, mobile_driver

    # report results
    try:
        mobile_driver.execute_script(
            "sauce:job-result=%s" % str(not request.node.rep_call.failed).lower()
        )
    except WebDriverException:
        logger.info(
            "Warning: The driver failed to quit properly. Check test and server side logs."
        )
    finally:
        mobile_driver.quit()
        eyes.close()


@pytest.yield_fixture(scope="function")
def android_desired_capabilities(request):
    desired_caps = copy(getattr(request, "param", {}))  # browser_config.copy()
    desired_caps["app"] = "http://saucelabs.com/example_files/ContactManager.apk"
    desired_caps["NATIVE_APP"] = True
    desired_caps["browserName"] = ""
    desired_caps["deviceName"] = "Samsung Galaxy S8 WQHD GoogleAPI Emulator"
    desired_caps["platformVersion"] = "8.1"
    desired_caps["platformName"] = "Android"
    desired_caps["clearSystemFiles"] = True
    desired_caps["noReset"] = True
    desired_caps["name"] = "AndroidNativeApp checkWindow"
    return desired_caps


@pytest.yield_fixture(scope="function")
def ios_desired_capabilities(request):
    desired_caps = copy(getattr(request, "param", {}))
    desired_caps[
        "app"
    ] = "https://applitools.bintray.com/Examples/HelloWorldiOS_1_0.zip"
    desired_caps["NATIVE_APP"] = True
    desired_caps["browserName"] = ""
    desired_caps["deviceName"] = "iPhone XS Simulator"
    desired_caps["platformVersion"] = "12.2"
    desired_caps["platformName"] = "iOS"
    desired_caps["clearSystemFiles"] = True
    desired_caps["noReset"] = True
    desired_caps["name"] = "iOSNativeApp checkWindow"
    return desired_caps


@pytest.mark.platform("Android")
def test_android_native_sauce_labs(mobile_eyes):
    eyes, mobile_driver = mobile_eyes
    eyes.open(mobile_driver, "AndroidNativeApp", "AndroidNativeApp checkWindow")
    eyes.check(
        "Contact list",
        Target.window().ignore(Region(left=0, top=0, width=1440, height=100)),
    )


@pytest.mark.platform("Android")
def test_android_native_region__sauce_labs(mobile_eyes):
    eyes, mobile_driver = mobile_eyes
    eyes.open(mobile_driver, "AndroidNativeApp", "AndroidNativeApp checkRegionFloating")
    settings = Target.region(Region(0, 100, 1400, 2000)).floating(
        Region(10, 10, 20, 20), 3, 3, 20, 30
    )
    eyes.check("Contact list", settings)


@pytest.mark.platform("iOS")
def test_iOS_native__sauce_labs(mobile_eyes):
    eyes, mobile_driver = mobile_eyes
    eyes.open(mobile_driver, "iOSNativeApp", "iOSNativeApp checkWindow")
    eyes.check(
        "Contact list",
        Target.window().ignore(Region(left=0, top=0, width=300, height=100)),
    )


@pytest.mark.platform("iOS")
def test_iOS_native_region__sauce_labs(mobile_eyes):
    eyes, mobile_driver = mobile_eyes
    eyes.open(mobile_driver, "iOSNativeApp", "iOSNativeApp checkRegionFloating")
    settings = Target.region(Region(0, 100, 375, 712)).floating(
        Region(10, 10, 20, 20), 3, 3, 20, 30
    )
    eyes.check("Contact list", settings)


@pytest.mark.platform("Android")
def test_android_native_sauce_labs_tracking_id_sent(mobile_eyes):
    eyes, mobile_driver = mobile_eyes
    eyes.open(mobile_driver, "AndroidNativeApp", "AndroidNativeApp trackingIdSent")
    with patch("applitools.core.server_connector.ServerConnector.match_window") as smw:
        eyes.check("Contact list", Target.window())
        match_window_data = smw.call_args[0][1]  # type: MatchWindowData

    assert match_window_data.options.source == "com.example.android.contactmanager"


@pytest.mark.platform("iOS")
def test_iOS_native_region_sauce_labs_tracking_id_sent(mobile_eyes):
    eyes, mobile_driver = mobile_eyes
    eyes.open(mobile_driver, "iOSNativeApp", "iOSNativeApp trackingIdSent")
    with patch("applitools.core.server_connector.ServerConnector.match_window") as smw:
        eyes.check("Contact list", Target.window())
        match_window_data = smw.call_args[0][1]  # type: MatchWindowData

    assert match_window_data.options.source == "HelloWorldiOS.app"
