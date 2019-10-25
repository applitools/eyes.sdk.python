import os

import pytest

from applitools.selenium import Eyes, VisualGridRunner, logger


def pytest_generate_tests(metafunc):
    os.environ["TEST_BROWSERS"] = "chrome"
    os.environ["TEST_PLATFORM"] = "Linux"


@pytest.fixture
def vg_runner():
    vg = VisualGridRunner(10)
    return vg


@pytest.fixture
def eyes_vg(vg_runner, sel_config, driver, request, test_page_url):
    app_name = request.node.get_closest_marker("app_name")
    if app_name:
        app_name = app_name.args[0]
    test_name = request.node.get_closest_marker("test_name")
    if test_name:
        test_name = test_name.args[0]
    viewport_size = request.node.get_closest_marker("viewport_size")
    if viewport_size:
        viewport_size = viewport_size.args[0]
    else:
        viewport_size = None

    eyes = Eyes(vg_runner)
    eyes.server_url = "https://eyes.applitools.com/"
    eyes.configuration = sel_config

    app_name = app_name or eyes.configuration.app_name
    test_name = test_name or eyes.configuration.test_name
    viewport_size = viewport_size or eyes.configuration.viewport_size

    driver.get(test_page_url)
    eyes.open(driver, app_name, test_name, viewport_size)
    yield eyes
    logger.debug("closing WebDriver for url {}".format(test_page_url))
    eyes.close()
    # TODO: print VG test results
