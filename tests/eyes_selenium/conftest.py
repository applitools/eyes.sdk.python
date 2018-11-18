import os

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.remote_connection import RemoteConnection

from applitools.eyes_core import logger
from applitools.eyes_selenium import Eyes, EyesWebDriver, eyes_selenium_utils


@pytest.fixture
def eyes_class():
    return Eyes


@pytest.fixture(scope="function")
def driver_session(request, driver):
    test_page_url = request.node.get_closest_marker('test_page_url').args[0]
    viewport_size = request.node.get_closest_marker('viewport_size').args[0]

    driver = EyesWebDriver(driver, None)
    if viewport_size:
        eyes_selenium_utils.set_browser_size(driver, viewport_size)
    request.cls.driver = driver

    driver.get(test_page_url)
    yield


@pytest.yield_fixture(scope='function')
def driver(request, browser_config):
    test_name = request.node.name
    build_tag = os.environ.get('BUILD_TAG', None)
    tunnel_id = os.environ.get('TUNNEL_IDENTIFIER', None)
    username = os.environ.get('SAUCE_USERNAME', None)
    access_key = os.environ.get('SAUCE_ACCESS_KEY', None)

    selenium_url = os.environ.get('SELENIUM_SERVER_URL', 'http://127.0.0.1:4444/wd/hub')
    if 'ondemand.saucelabs.com' in selenium_url:
        selenium_url = "https://%s:%s@ondemand.saucelabs.com:443/wd/hub" % (username, access_key)
    logger.debug('SELENIUM_URL={}'.format(selenium_url))

    desired_caps = browser_config.copy()
    desired_caps['build'] = build_tag
    desired_caps['tunnelIdentifier'] = tunnel_id
    desired_caps['name'] = test_name

    executor = RemoteConnection(selenium_url, resolve_ip=False)
    browser = webdriver.Remote(command_executor=executor,
                               desired_capabilities=desired_caps)
    if browser is None:
        raise WebDriverException("Never created!")

    yield browser

    # report results
    try:
        browser.execute_script("sauce:job-result=%s" % str(not request.node.rep_call.failed).lower())
    except WebDriverException:
        # we can ignore the exceptions of WebDriverException type -> We're done with tests.
        logger.info('Warning: The driver failed to quit properly. Check test and server side logs.')
    finally:
        browser.quit()
