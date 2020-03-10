import pytest

from applitools.common import BatchInfo


def pytest_generate_tests(metafunc):
    if "page" in metafunc.fixturenames:
        metafunc.parametrize("page", ["mobile", "desktop", "scrolled_mobile"])


@pytest.fixture
def batch_info():
    return BatchInfo("Python SDK Mobile")
