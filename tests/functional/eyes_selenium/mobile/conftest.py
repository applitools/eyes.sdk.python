import pytest

from applitools.common import BatchInfo
from tests.utils import parametrize_ids


def pytest_generate_tests(metafunc):
    if "page" in metafunc.fixturenames:
        metafunc.parametrize(
            "page",
            ["mobile", "desktop", "scrolled_mobile"],
            ids=parametrize_ids("page"),
        )


@pytest.fixture
def batch_info():
    return BatchInfo("Python SDK Mobile")
