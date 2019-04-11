import os
from typing import Optional, Text

import pytest
from mock import MagicMock

from applitools.common import (
    AppOutput,
    Configuration,
    ImageMatchSettings,
    RunningSession,
)
from applitools.common.utils.json_utils import attr_from_response
from applitools.core import EyesBase, ServerConnector
from applitools.core.capture import AppOutputProvider, AppOutputWithScreenshot
from applitools.images.capture import EyesImagesScreenshot


@pytest.fixture
def custom_eyes_server():
    return None


@pytest.fixture
def eyes_base_mock():
    return MagicMock(EyesBase)


@pytest.fixture
def configuration():
    return Configuration()


@pytest.fixture(scope="function")
def connector(custom_eyes_server):
    # type: (Optional[Text]) -> ServerConnector
    return ServerConnector(custom_eyes_server)


@pytest.fixture(scope="function")
def configured_connector(custom_eyes_server):
    # type: (Optional[Text]) -> ServerConnector
    connector = ServerConnector(custom_eyes_server)
    connector.api_key = os.environ["APPLITOOLS_API_KEY"]
    return connector


@pytest.fixture(scope="function")
def started_connector(configured_connector):
    configured_connector._request = configured_connector._request_factory.create(
        server_url=configured_connector.server_url,
        api_key=configured_connector.api_key,
        timeout=configured_connector.timeout,
    )
    return configured_connector


@pytest.fixture
def screenshot(image):
    return EyesImagesScreenshot(image)


@pytest.fixture
def app_output():
    return AppOutput("output", None)


@pytest.fixture
def app_output_with_screenshot(app_output, screenshot):
    return AppOutputWithScreenshot(app_output, screenshot)


@pytest.fixture
def image_match_settings():
    return ImageMatchSettings()


@pytest.fixture
def app_output_provider(image, app_output_with_screenshot):
    apo = AppOutputProvider(
        lambda region, last_screenshot, check_settings: app_output_with_screenshot
    )
    return apo


@pytest.fixture
def running_session():
    RUNNING_SESSION_DATA = {
        "id": "some id",
        "sessionId": "some session id",
        "url": "http://some-session-url.com",
        "batchId": "other url",
        "baselineId": "other url",
    }
    RUNNING_SESSION_OBJ = attr_from_response(RUNNING_SESSION_DATA, RunningSession)
    return RUNNING_SESSION_OBJ
