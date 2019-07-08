import os

import pytest

from applitools.images import Eyes
from applitools.images.__version__ import __version__


@pytest.fixture
def eyes_class():
    return Eyes


def _setup_env_vars_for_session():
    python_version = os.getenv("TRAVIS_PYTHON_VERSION", None)
    if not python_version:
        import platform

        python_version = platform.python_version()
    os.environ["APPLITOOLS_BATCH_NAME"] = "Python {} | Images SDK {}".format(
        python_version, __version__
    )


def pytest_generate_tests(metafunc):
    _setup_env_vars_for_session()
