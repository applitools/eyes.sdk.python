import os

import mock
import pytest


def pytest_generate_tests(metafunc):
    import uuid

    # setup environment variables once per test run if not settled up
    # needed for multi thread run

    os.environ["APPLITOOLS_BATCH_ID"] = os.getenv(
        "APPLITOOLS_BATCH_ID", str(uuid.uuid4())
    )


@pytest.fixture
def driver_mock():
    from selenium.webdriver.remote.webdriver import WebDriver

    return mock.Mock(WebDriver)
