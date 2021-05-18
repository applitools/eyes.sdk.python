import os

import pytest

from applitools.selenium import BatchInfo, VisualGridRunner


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
