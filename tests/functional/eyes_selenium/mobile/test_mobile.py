import os
from copy import copy

import pytest
from appium import webdriver as appium_webdriver
from selenium.common.exceptions import WebDriverException

from applitools.common import StitchMode, logger
from applitools.selenium import ScreenOrientation, Target
from tests.functional.eyes_selenium.selenium_utils import open_webdriver

IOS_DEVICES = [
    ["iPad Pro (9.7 inch) Simulator", "12.0", ScreenOrientation.LANDSCAPE, False],
    ["iPad Pro (9.7 inch) Simulator", "12.0", ScreenOrientation.PORTRAIT, False],
    ["iPad Pro (9.7 inch) Simulator", "12.0", ScreenOrientation.PORTRAIT, True],
    ["iPhone XR Simulator", "13.0", ScreenOrientation.PORTRAIT, False],
    ["iPhone XR Simulator", "13.0", ScreenOrientation.PORTRAIT, True],
    ["iPhone XR Simulator", "13.0", ScreenOrientation.LANDSCAPE, False],
    # ["iPad Air 2 Simulator", "12.0", ScreenOrientation.LANDSCAPE, False],
    # ["iPad Air 2 Simulator", "11.3", ScreenOrientation.LANDSCAPE, False],
    # ["iPad Air 2 Simulator", "11.0", ScreenOrientation.LANDSCAPE, False],
    # ["iPad Air 2 Simulator", "10.3", ScreenOrientation.LANDSCAPE, False],
    # ["iPad Air 2 Simulator", "12.0", ScreenOrientation.PORTRAIT, False],
    # ["iPad Air 2 Simulator", "11.3", ScreenOrientation.PORTRAIT, False],
    # ["iPad Air 2 Simulator", "11.0", ScreenOrientation.PORTRAIT, False],
    # ["iPad Air 2 Simulator", "10.3", ScreenOrientation.PORTRAIT, False],
    # ["iPad Air Simulator", "12.0", ScreenOrientation.LANDSCAPE, False],
    # ["iPad Air Simulator", "11.0", ScreenOrientation.PORTRAIT, True],
    # ["iPad Simulator", "11.0", ScreenOrientation.LANDSCAPE, True],
    # ["iPad Simulator", "11.0", ScreenOrientation.PORTRAIT, False],
    # ["iPad (5th generation) Simulator", "11.0", ScreenOrientation.PORTRAIT, False],
    # ["iPad Pro (9.7 inch) Simulator", "11.0", ScreenOrientation.LANDSCAPE, False],
    # ["iPad Pro (9.7 inch) Simulator", "11.0", ScreenOrientation.LANDSCAPE, True],
    # [
    #     "iPad Pro (12.9 inch) (2nd generation) Simulator",
    #     "11.0",
    #     ScreenOrientation.LANDSCAPE,
    #     False,
    # ],
    # [
    #     "iPad Pro (12.9 inch) (2nd generation) Simulator",
    #     "11.0",
    #     ScreenOrientation.PORTRAIT,
    #     True,
    # ],
    # [
    #     "iPad Pro (12.9 inch) (2nd generation) Simulator",
    #     "12.0",
    #     ScreenOrientation.PORTRAIT,
    #     True,
    # ],
    # ["iPad Pro (10.5 inch) Simulator", "11.0", ScreenOrientation.PORTRAIT, False],
    # ["iPad Pro (10.5 inch) Simulator", "11.0", ScreenOrientation.LANDSCAPE, True],
    # ["iPhone XS Max Simulator", "12.2", ScreenOrientation.LANDSCAPE, False],
    # ["iPhone XS Max Simulator", "12.2", ScreenOrientation.LANDSCAPE, True],
    # ["iPhone XS Max Simulator", "12.2", ScreenOrientation.PORTRAIT, False],
    # ["iPhone XS Max Simulator", "12.2", ScreenOrientation.PORTRAIT, True],
    # ["iPhone XS Simulator", "12.2", ScreenOrientation.PORTRAIT, False],
    # ["iPhone XS Simulator", "12.2", ScreenOrientation.LANDSCAPE, False],
    # ["iPhone XS Simulator", "12.2", ScreenOrientation.PORTRAIT, True],
    # ["iPhone XS Simulator", "12.2", ScreenOrientation.LANDSCAPE, True],
    # ["iPhone XR Simulator", "12.2", ScreenOrientation.PORTRAIT, False],
    # ["iPhone XR Simulator", "12.2", ScreenOrientation.LANDSCAPE, False],
    # ["iPhone XR Simulator", "12.2", ScreenOrientation.LANDSCAPE, True],
    # ["iPhone X Simulator", "11.2", ScreenOrientation.PORTRAIT, False],
    # ["iPhone X Simulator", "11.2", ScreenOrientation.PORTRAIT, True],
    # ["iPhone 7 Simulator", "10.3", ScreenOrientation.PORTRAIT, True],
    # ["iPhone 6 Plus Simulator", "11.0", ScreenOrientation.PORTRAIT, False],
    # ["iPhone 6 Plus Simulator", "11.0", ScreenOrientation.LANDSCAPE, True],
    # ["iPhone 5s Simulator", "10.3", ScreenOrientation.LANDSCAPE, False],
    # ["iPhone 5s Simulator", "10.3", ScreenOrientation.LANDSCAPE, True],
]

ANDROID_DEVICES = [
    ["Android Emulator", "8.0", ScreenOrientation.PORTRAIT, False],
    ["Android Emulator", "8.0", ScreenOrientation.LANDSCAPE, True],
]


@pytest.yield_fixture(scope="function")
def mobile_eyes(request, page, eyes, capsys):
    # configure eyes through @pytest.mark.parametrize('mobile_eyes', [], indirect=True)
    browser_config = copy(getattr(request, "param", {}))
    fully = browser_config.pop("fully", None)

    test_name = "{name} {plat_ver} {dev_or} {page}".format(
        name=browser_config["deviceName"],
        plat_ver=browser_config["platformVersion"],
        dev_or=browser_config["deviceOrientation"],
        page=page,
    )
    test_suite_name = request.node.get_closest_marker("test_suite_name")
    test_suite_name = (
        test_suite_name.args[-1]
        if test_suite_name
        else "Eyes Selenium SDK - iOS Safari Cropping"
    )

    if fully:
        test_name += " fully"

    selenium_url = "https://{username}:{password}@ondemand.saucelabs.com:443/wd/hub".format(
        username=os.getenv("SAUCE_USERNAME", None),
        password=os.getenv("SAUCE_ACCESS_KEY", None),
    )
    desired_caps = browser_config.copy()
    desired_caps["build"] = os.getenv("BUILD_TAG", None)
    desired_caps["tunnelIdentifier"] = os.getenv("TUNNEL_IDENTIFIER", None)
    desired_caps["name"] = "{} ({})".format(test_name, eyes.full_agent_id)

    driver = open_webdriver(
        lambda: appium_webdriver.Remote(
            command_executor=selenium_url, desired_capabilities=desired_caps
        ),
        capsys,
    )

    eyes.stitch_mode = StitchMode.CSS
    eyes.add_property("Orientation", browser_config["deviceOrientation"])
    eyes.add_property("Stitched", "True" if fully else "False")

    if driver is None:
        raise WebDriverException("Never created!")

    driver.get(
        "https://applitools.github.io/demo/TestPages/DynamicResolution/{}.html".format(
            page
        )
    )
    driver = eyes.open(driver, test_suite_name, test_name)
    yield eyes, fully

    # report results
    try:
        driver.execute_script(
            "sauce:job-result=%s" % str(not request.node.rep_call.failed).lower()
        )
    except WebDriverException:
        # we can ignore the exceptions of WebDriverException type -> We're done with tests.
        logger.info(
            "Warning: The driver failed to quit properly. Check test and server side logs."
        )
    finally:
        driver.quit()
        eyes.close()


def create_browser_config(device, platform_name, browser_name):
    device_name, platform_version, dev_orientation, fully = device
    browser_config = {
        "deviceName": device_name,
        "deviceOrientation": dev_orientation.name.upper(),
        "platformVersion": platform_version,
        "platformName": platform_name,
        "browserName": browser_name,
        "fully": fully,
    }
    return browser_config


@pytest.mark.platform("Android")
@pytest.mark.parametrize(
    "mobile_eyes",
    [create_browser_config(device, "Android", "Chrome") for device in ANDROID_DEVICES],
    indirect=True,
    ids=lambda o: "{}-{}-{}".format(
        o["deviceName"], o["platformVersion"], o["deviceOrientation"]
    ),
)
def test_android__sauce_labs(mobile_eyes):
    eyes, fully = mobile_eyes
    eyes.check("", Target.window().fully(fully))


@pytest.mark.platform("iOS")
@pytest.mark.parametrize(
    "mobile_eyes",
    [create_browser_config(device, "iOS", "Safari") for device in IOS_DEVICES],
    indirect=True,
    ids=lambda o: "{}-{}-{}".format(
        o["deviceName"], o["platformVersion"], o["deviceOrientation"]
    ),
)
def test_IOS_safari_crop__sauce_labs(mobile_eyes):
    eyes, fully = mobile_eyes
    eyes.check("", Target.window().fully(fully))
