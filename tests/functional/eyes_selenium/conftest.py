from __future__ import absolute_import

import os
from distutils.util import strtobool

import pytest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from applitools.selenium import Configuration, Eyes, logger

try:
    from typing import TYPE_CHECKING, Generator, Iterable, Optional, Text
except ImportError:
    TYPE_CHECKING = False
    pass


@pytest.fixture
def sauce_driver_url():
    return "https://{}:{}@ondemand.saucelabs.com:443/wd/hub".format(
        os.environ["SAUCE_USERNAME"], os.environ["SAUCE_ACCESS_KEY"]
    )


@pytest.fixture
def eyes_class():
    return Eyes


@pytest.fixture
def webdriver_module():
    return webdriver


@pytest.fixture
def eyes_config_base():
    return (
        Configuration()
        .set_hide_scrollbars(True)
        .set_save_new_tests(False)
        .set_hide_caret(True)
        .set_parent_branch_name("master")
    )


@pytest.fixture(scope="function")
def chrome_driver(request, sauce_driver_url):
    test_page_url = request.node.get_closest_marker("test_page_url")
    test_page_url = test_page_url.args[-1] if test_page_url else None

    options = webdriver.ChromeOptions()
    headless = strtobool(os.getenv("TEST_BROWSER_HEADLESS", "True"))
    options.headless = bool(headless)
    force_remote = bool(os.getenv("TEST_REMOTE", False))
    if force_remote:
        selenium_url = os.getenv("SELENIUM_SERVER_URL", sauce_driver_url)
        logger.debug("SELENIUM_URL={}".format(selenium_url))
        browser = webdriver.Remote(
            command_executor=selenium_url,
            desired_capabilities=options.to_capabilities(),
        )
    else:
        browser = webdriver.Chrome(ChromeDriverManager().install())
    if test_page_url:
        browser.get(test_page_url)
        logger.info("navigation to URL: {}".format(test_page_url))
    yield browser
    browser.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # this sets the result as a test attribute for SauceLabs reporting.
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set an report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)
