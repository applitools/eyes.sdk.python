import os

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from applitools.core import logger
from applitools.selenium import Eyes, EyesWebDriver, eyes_selenium_utils
from applitools.selenium.__version__ import __version__


def _setup_env_vars_for_session():
    python_version = os.environ.get("TRAVIS_PYTHON_VERSION", None)
    if not python_version:
        import platform

        python_version = platform.python_version()
    os.environ["APPLITOOLS_BATCH_NAME"] = "Python {} | Selenium SDK {}".format(
        python_version, __version__
    )


def pytest_generate_tests(metafunc):
    _setup_env_vars_for_session()


@pytest.fixture
def eyes_class():
    return Eyes


@pytest.fixture
def webdriver_module():
    return webdriver


@pytest.fixture(scope="function")
def eyes_open(request, eyes, driver):
    test_page_url = request.node.get_closest_marker("test_page_url").args[-1]

    viewport_size = request.node.get_closest_marker("viewport_size")
    viewport_size = viewport_size.args[-1] if viewport_size else None

    test_suite_name = request.node.get_closest_marker("test_suite_name")
    test_suite_name = (
        test_suite_name.args[-1] if test_suite_name else "Python Selenium SDK"
    )

    # use camel case in method name for fit java sdk tests name
    test_name = request.function.__name__.title().replace("_", "")

    if eyes.force_full_page_screenshot:
        test_suite_name += " - ForceFPS"
        test_name += "_FPS"
    driver = eyes.open(driver, test_suite_name, test_name, viewport_size=viewport_size)
    driver.get(test_page_url)

    yield eyes, driver
    results = eyes.close()
    print(results)


@pytest.fixture(scope="function")
def eyes_for_class(request, eyes_open):
    # TODO: implement eyes.setDebugScreenshotsPrefix("Java_" + testName + "_");

    eyes, driver = eyes_open
    request.cls.eyes = eyes
    request.cls.driver = driver
    yield


@pytest.fixture(scope="function")
def driver_for_class(request, driver):
    test_page_url = request.node.get_closest_marker("test_page_url").args[0]
    viewport_size = request.node.get_closest_marker("viewport_size").args[0]

    driver = EyesWebDriver(driver, None)
    if viewport_size:
        eyes_selenium_utils.set_browser_size(driver, viewport_size)
    request.cls.driver = driver

    driver.get(test_page_url)
    yield


@pytest.yield_fixture(scope="function")
def driver(request, browser_config, webdriver_module):
    test_name = request.node.name
    build_tag = os.environ.get("BUILD_TAG", None)
    tunnel_id = os.environ.get("TUNNEL_IDENTIFIER", None)
    username = os.environ.get("SAUCE_USERNAME", None)
    access_key = os.environ.get("SAUCE_ACCESS_KEY", None)

    force_remote = request.config.getoption("remote", default=False)
    selenium_url = os.environ.get("SELENIUM_SERVER_URL", "http://127.0.0.1:4444/wd/hub")
    if "ondemand.saucelabs.com" in selenium_url or force_remote:
        selenium_url = "https://%s:%s@ondemand.saucelabs.com:443/wd/hub" % (
            username,
            access_key,
        )
    logger.debug("SELENIUM_URL={}".format(selenium_url))

    desired_caps = browser_config.copy()
    desired_caps["build"] = build_tag
    desired_caps["tunnelIdentifier"] = tunnel_id
    desired_caps["name"] = test_name

    browser = webdriver_module.Remote(
        command_executor=selenium_url, desired_capabilities=desired_caps
    )
    if browser is None:
        raise WebDriverException("Never created!")

    yield browser

    # report results
    try:
        browser.execute_script(
            "sauce:job-result=%s" % str(not request.node.rep_call.failed).lower()
        )
    except WebDriverException:
        # we can ignore the exceptions of WebDriverException type -> We're done with tests.
        logger.info(
            "Warning: The driver failed to quit properly. Check test and server side logs."
        )
    finally:
        browser.quit()
