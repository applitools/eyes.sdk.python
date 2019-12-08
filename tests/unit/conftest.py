from typing import Optional, Text

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

import mock
import pytest
from applitools.common import (
    AppEnvironment,
    AppOutput,
    BatchInfo,
    Configuration,
    ImageMatchSettings,
    MatchLevel,
    RunningSession,
    SessionStartInfo,
    SessionType,
)
from applitools.common.utils.json_utils import attr_from_json
from applitools.core import EyesBase, ServerConnector
from applitools.core.capture import AppOutputProvider, AppOutputWithScreenshot
from mock import MagicMock


@pytest.fixture
def driver_mock():
    from applitools.selenium import EyesWebDriver

    driver = mock.Mock(EyesWebDriver)
    driver._driver = mock.Mock(WebDriver)

    desired_capabilities = {"platformName": ""}
    driver.desired_capabilities = desired_capabilities
    driver._driver.desired_capabilities = desired_capabilities

    # need to configure below
    driver._driver.execute_script = mock.Mock(side_effect=WebDriverException())
    return driver


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
    connector = ServerConnector()
    connector.server_url = custom_eyes_server
    return connector


@pytest.fixture(scope="function")
def configured_connector(custom_eyes_server):
    # type: (Optional[Text]) -> ServerConnector
    connector = ServerConnector()
    conf = Configuration(server_url=custom_eyes_server)
    connector.update_config(conf)
    return connector


@pytest.fixture(scope="function")
def started_connector(configured_connector):
    configured_connector._is_session_started = True
    return configured_connector


@pytest.fixture
def screenshot(image):
    from applitools.images.capture import EyesImagesScreenshot

    return EyesImagesScreenshot(image)


@pytest.fixture
def app_output():
    return AppOutput("output", None)


@pytest.fixture
def app_output_with_screenshot(app_output, screenshot):
    return AppOutputWithScreenshot(app_output, screenshot)


@pytest.fixture(scope="function")
def image_match_settings():
    return ImageMatchSettings()


@pytest.fixture
def app_output_provider(image, app_output_with_screenshot):
    apo = AppOutputProvider(
        lambda region, last_screenshot, check_settings: app_output_with_screenshot
    )
    return apo


@pytest.fixture(scope="function")
def running_session():
    RUNNING_SESSION_DATA = """{
        "id": "some id",
        "sessionId": "some session id",
        "url": "http://some-session-url.com",
        "batchId": "other url",
        "baselineId": "other url"
    }"""
    RUNNING_SESSION_OBJ = attr_from_json(RUNNING_SESSION_DATA, RunningSession)
    return RUNNING_SESSION_OBJ


@pytest.fixture(scope="function")
def session_start_info():
    return SessionStartInfo(
        agent_id="eyes.core.python/3.15.4",
        session_type=SessionType.SEQUENTIAL,
        app_id_or_name="TestApp",
        ver_id=None,
        scenario_id_or_name="TestName",
        batch_info=BatchInfo(),
        baseline_env_name="Baseline env name",
        environment_name="Env name",
        environment=AppEnvironment(),
        default_match_settings=ImageMatchSettings(match_level=MatchLevel.STRICT),
        branch_name="branch Name",
        parent_branch_name="parentBranchName",
        baseline_branch_name="baselineBranchName",
        compare_with_parent_branch=False,
        ignore_baseline=False,
        save_diffs=True,
        render=False,
        properties=[],
    )
