import os

import pytest
from applitools.images import Eyes
from applitools.images.__version__ import __version__


@pytest.fixture
def eyes_class():
    return Eyes


def _setup_env_vars_for_session():
    os.environ["APPLITOOLS_BATCH_NAME"] = "Python | Images SDK {}".format(__version__)


def pytest_generate_tests(metafunc):
    _setup_env_vars_for_session()
