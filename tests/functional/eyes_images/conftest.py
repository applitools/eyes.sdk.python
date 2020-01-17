import os

import pytest

from applitools.images import BatchInfo, Eyes
from tests.utils import send_result_report, prepare_result_data_for_makereport


@pytest.fixture
def eyes_class():
    return Eyes


@pytest.fixture
def batch_info():
    return BatchInfo("Python SDK Images")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()

    if result.when == "teardown":
        passed = result.outcome == "passed"
        res = prepare_result_data_for_makereport(test_name=item.name, passed=passed)
        send_result_report([res], group="images")
