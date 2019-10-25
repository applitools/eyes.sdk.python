import os

import pytest
from appium import webdriver as appium_webdriver
from selenium.common.exceptions import WebDriverException

from applitools.common import StitchMode, logger


def pytest_generate_tests(metafunc):
    if "page" in metafunc.fixturenames:
        metafunc.parametrize("page", ["mobile", "desktop", "scrolled_mobile"])


@pytest.yield_fixture(scope="function")
def mobile_eyes(request, page, eyes):
    # configure eyes through @pytest.mark.parametrize('mobile_eyes', [], indirect=True)
    browser_config = getattr(request, "param", {})
    fully = browser_config.pop("fully")

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

    driver = appium_webdriver.Remote(
        command_executor=selenium_url, desired_capabilities=desired_caps
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
