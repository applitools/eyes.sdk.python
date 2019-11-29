import pytest

from applitools.common import BatchInfo


@pytest.fixture
def batch_info():
    return BatchInfo("Python SDK Selenium")
