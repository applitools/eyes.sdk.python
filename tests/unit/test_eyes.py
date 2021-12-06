import os

import mock
import pytest

from applitools.selenium import __version__


@pytest.fixture
def clean_environ():
    # Python2/Windows ThreadPoolExecutor requires this
    cpus = os.getenv("NUMBER_OF_PROCESSORS")
    save = {"NUMBER_OF_PROCESSORS": cpus} if cpus else {}

    with mock.patch.dict(os.environ, save, clear=True):
        yield


def pytest_generate_tests(metafunc):
    if "eyes" in metafunc.fixturenames:
        metafunc.parametrize("eyes", ["selenium", "visual_grid"], indirect=True)


def test_base_agent_id(eyes):
    _, version = eyes.base_agent_id.split("/")
    assert version == __version__.__version__


def test_is_disabled_True(eyes):
    eyes.is_disabled = True
    eyes.check("Test", None)


def test_is_disabled_False(eyes):
    with pytest.raises(Exception):
        eyes.is_disabled = False
        eyes.check(None, None)


def test_set_get_debug_screenshot_provider(clean_environ, eyes):
    eyes.save_debug_screenshots = True
    assert eyes.debug_screenshots_prefix == "screenshot_"
    assert eyes.debug_screenshots_path == ""

    eyes.debug_screenshots_path = "./screenshot"
    assert eyes.debug_screenshots_path == "./screenshot"

    eyes.debug_screenshots_prefix = "new_prefix"
    assert eyes.debug_screenshots_prefix == "new_prefix"
