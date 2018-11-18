import pytest

from applitools.eyes_images import Eyes


@pytest.fixture
def eyes_class():
    return Eyes
