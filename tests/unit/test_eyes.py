import os

import mock
import pytest

from applitools.core import ServerConnector, __version__
from applitools.core.debug import (
    FileDebugScreenshotsProvider,
    NullDebugScreenshotsProvider,
)
from tests.utils import parametrize_ids


@pytest.fixture
def clean_environ():
    # Python2/Windows ThreadPoolExecutor requires this
    cpus = os.getenv("NUMBER_OF_PROCESSORS")
    save = {"NUMBER_OF_PROCESSORS": cpus} if cpus else {}

    with mock.patch.dict(os.environ, save, clear=True):
        yield


def pytest_generate_tests(metafunc):
    if "eyes" in metafunc.fixturenames:
        metafunc.parametrize(
            "eyes",
            ["selenium", "visual_grid", "images"],
            ids=parametrize_ids("eyes"),
            indirect=True,
        )


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


def test_set_get_server_connector(eyes):
    updated = []

    class CustomServerCon(ServerConnector):
        def update_config(self, conf, full_agent_id, render_info=None, ua_string=None):
            updated.append(True)
            return super(CustomServerCon, self).update_config(conf, full_agent_id)

    conn = CustomServerCon()
    eyes.server_connector = conn
    assert eyes.server_connector is conn

    eyes.server_connector.update_config(eyes.configure, eyes.full_agent_id)
    assert updated


def test_set_incorrect_server_connector(eyes):
    class CustomServerCon:
        pass

    with pytest.raises(ValueError):
        eyes.server_connector = CustomServerCon()


def test_set_get_debug_screenshot_provider(clean_environ, eyes):
    assert isinstance(eyes.debug_screenshots_provider, NullDebugScreenshotsProvider)

    eyes.save_debug_screenshots = True
    assert isinstance(eyes.debug_screenshots_provider, FileDebugScreenshotsProvider)
    assert eyes.debug_screenshots_prefix == "screenshot_"
    assert eyes.debug_screenshots_path == ""

    eyes.debug_screenshots_path = "./screenshot"
    assert eyes.debug_screenshots_path == "./screenshot"
    assert eyes.debug_screenshots_provider.path == "./screenshot"

    eyes.debug_screenshots_prefix = "new_prefix"
    assert eyes.debug_screenshots_prefix == "new_prefix"
    assert eyes.debug_screenshots_provider.prefix == "new_prefix"
