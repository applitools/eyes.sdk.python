import os

import pytest

from applitools.selenium import BatchInfo, VisualGridRunner
from tests.utils import prepare_result_data_for_makereport, send_result_report


def pytest_generate_tests(metafunc):
    os.environ["TEST_BROWSERS"] = "chrome"
    os.environ["TEST_PLATFORM"] = "Linux"
    os.environ["APPLITOOLS_BATCH_NAME"] = "Python SDK VisualGridTests"


@pytest.fixture(scope="function")
def vg_runner():
    vg = VisualGridRunner(10)
    return vg


@pytest.fixture
def batch_info():
    return BatchInfo("Python SDK VisualGridTests")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()

    if result.when in ["call", "teardown"]:
        passed = result.outcome == "passed"
        if call.excinfo:
            passed = False
        res = prepare_result_data_for_makereport(
            test_name=item.originalname, passed=passed
        )
        res["parameters"] = dict(mode="VisualGrid")
        send_result_report([res], group="selenium")
