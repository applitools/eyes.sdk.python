import os

import pytest

from applitools.images import BatchInfo, Eyes


@pytest.fixture
def eyes_class():
    return Eyes


@pytest.fixture
def batch_info():
    return BatchInfo("Python SDK Images")
