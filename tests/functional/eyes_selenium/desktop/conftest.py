import os
from distutils.util import strtobool

import pytest

from applitools.selenium import (
    BatchInfo,
    BrowserType,
    StitchMode,
    VisualGridRunner,
    ClassicRunner,
)


@pytest.fixture
def stitch_mode():
    return StitchMode.CSS


@pytest.fixture
def eyes_config(eyes_config_base, stitch_mode):
    return eyes_config_base.set_stitch_mode(stitch_mode).add_browser(
        700, 460, BrowserType.CHROME
    )


if strtobool(os.getenv("TEST_RUN_ON_VG", "False")):

    @pytest.fixture(scope="session")
    def eyes_runner_class():
        return lambda: VisualGridRunner(1)

    @pytest.fixture
    def batch_info():
        return BatchInfo("Python SDK Desktop VG")


else:

    @pytest.fixture(scope="session")
    def eyes_runner_class():
        return lambda: ClassicRunner()

    @pytest.fixture
    def batch_info():
        return BatchInfo("Python SDK Desktop Selenium")


def pytest_generate_tests(metafunc):
    os.environ["TEST_BROWSERS"] = "chrome"

    if "page" in metafunc.fixturenames:
        metafunc.parametrize("page", ["mobile", "desktop", "scrolled_mobile"])

    if not strtobool(os.getenv("TEST_RUN_ON_VG", "False")):
        if "stitch_mode" in metafunc.fixturenames:
            metafunc.parametrize("stitch_mode", [StitchMode.CSS, StitchMode.Scroll])
