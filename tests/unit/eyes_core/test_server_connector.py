import json
import os
from copy import copy
from typing import Any

import pytest
import requests
from mock import patch

from applitools.common import (
    AppEnvironment,
    AppOutput,
    BatchInfo,
    EyesError,
    ImageMatchSettings,
    MatchLevel,
    MatchWindowData,
    Options,
    RunningSession,
    SessionStartInfo,
    TestResults,
)
from applitools.common.config import DEFAULT_SERVER_URL, Configuration
from applitools.common.server import SessionType
from applitools.common.utils import image_utils
from applitools.common.utils.compat import urljoin
from applitools.common.utils.json_utils import attr_from_json
from applitools.common.visual_grid import RenderingInfo
from applitools.core import ServerConnector

API_KEY = "TEST-API-KEY"
CUSTOM_EYES_SERVER = "http://custom-eyes-server.com"

API_SESSIONS = "api/sessions"
API_SESSIONS_RUNNING = API_SESSIONS + "/running/"
RUNNING_DATA_PATH = API_SESSIONS + "/running/data"
RENDER_INFO_PATH = API_SESSIONS + "/renderinfo"

RUNNING_SESSION_URL = urljoin(CUSTOM_EYES_SERVER, API_SESSIONS_RUNNING)
RUNNING_SESSION_DATA_URL = urljoin(RUNNING_SESSION_URL, "data")
RENDER_INFO_PATH_URL = urljoin(CUSTOM_EYES_SERVER, RENDER_INFO_PATH)
LONG_REQUEST_URL = urljoin(CUSTOM_EYES_SERVER, "/one")
LONG_REQUEST_RESPONSE_URL = urljoin(CUSTOM_EYES_SERVER, "/second")

RENDER_INFO_URL = "https://render-wus.applitools.com"
RENDER_INFO_AT = "Some Token"
RENDERING_INFO_DATA = """
{
    "ServiceUrl": "%s",
    "AccessToken": "%s",
    "ResultsUrl": "%s?accessKey=%s"
}""" % (
    RENDER_INFO_URL,
    RENDER_INFO_AT,
    RUNNING_SESSION_DATA_URL,
    API_KEY,
)
RENDERING_OBJ = attr_from_json(RENDERING_INFO_DATA, RenderingInfo)


@pytest.fixture
def custom_eyes_server():
    return CUSTOM_EYES_SERVER


class MockResponse(object):
    def __init__(self, json_data, status_code, headers=None):
        self.json_data = json_data
        self.status_code = status_code
        self.headers = headers

    def raise_for_status(self):
        pass

    def json(self):
        return json.loads(self.json_data)

    @property
    def text(self):
        return self.json_data

    @property
    def content(self):
        return bytes(self.json_data)

    @property
    def ok(self):
        return self.status_code in (200, 201)


def _request_check(*args, **kwargs):
    if not kwargs["params"]["apiKey"]:
        raise ValueError("API KEY Must be installed")
    if args[0] is None:
        raise ValueError("URL must be present")


def mocked_requests_delete(*args, **kwargs):
    _request_check(*args, **kwargs)
    url = args[0]
    if url == urljoin(RUNNING_SESSION_URL, RUNNING_SESSION_DATA_RESPONSE_ID):
        return MockResponse(STOP_SESSION_DATA, 200)
    elif url == LONG_REQUEST_RESPONSE_URL:
        return MockResponse({}, 200)
    return MockResponse(None, 404)


def mocked_requests_get(*args, **kwargs):
    _request_check(*args, **kwargs)
    url = args[0]
    if url == RENDER_INFO_PATH_URL:
        return MockResponse(RENDERING_INFO_DATA, 200)
    if url == LONG_REQUEST_URL:
        return MockResponse(None, 202, {"Location": LONG_REQUEST_RESPONSE_URL})
    if url == LONG_REQUEST_RESPONSE_URL:
        return MockResponse(None, 201, {"Location": LONG_REQUEST_RESPONSE_URL})
    return MockResponse(None, 404)


def mocked_requests_post(*args, **kwargs):
    _request_check(*args, **kwargs)
    url = args[0]
    if url == RUNNING_SESSION_URL:
        return MockResponse(RUNNING_SESSION_DATA_RESPONSE, 201)
    elif url == urljoin(RUNNING_SESSION_URL, RUNNING_SESSION_DATA_RESPONSE_ID):
        return MockResponse('{"asExpected": true}', 200)
    elif url == RUNNING_SESSION_DATA_URL:
        return MockResponse(
            {}, 200, headers={"Location": RUNNING_SESSION_DATA_RESPONSE_URL}
        )
    return MockResponse(None, 404)


SESSION_START_INFO_DATA = """
{
    "scenarioIdOrName": "TestName",
    "batchInfo": {
        "name": None,
        "startedAt": "YYYY-MM-DD HH:MM:SS.mmmmmm",
        "id": "UUID ID",
    },
    "envName": null,
    "environment": null,
    "defaultMatchSettings": {"matchLevel": "STRICT", "exact": null},
    "verId": null,
    "branchName": null,
    "parentBranchName": null,
    "properties": []
}"""
SESSION_START_INFO_OBJ = SessionStartInfo(
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
    save_diffs=True,
    render=False,
    properties=[],
)
RUNNING_SESSION_DATA_RESPONSE_ID = "some id"
RUNNING_SESSION_DATA_RESPONSE_URL = "http://some-session-url.com"
RUNNING_SESSION_DATA_RESPONSE_SESSION_ID = "some session id"
RUNNING_SESSION_DATA_RESPONSE_BATCH_ID = "other url"
RUNNING_SESSION_DATA_RESPONSE_BASELINE_ID = "other url"
RUNNING_SESSION_DATA_RESPONSE = """
{
    "id": "%s",
    "sessionId": "%s",
    "url": "%s",
    "batchId": "%s",
    "baselineId": "%s"
}""" % (
    RUNNING_SESSION_DATA_RESPONSE_ID,
    RUNNING_SESSION_DATA_RESPONSE_SESSION_ID,
    RUNNING_SESSION_DATA_RESPONSE_URL,
    RUNNING_SESSION_DATA_RESPONSE_BATCH_ID,
    RUNNING_SESSION_DATA_RESPONSE_BASELINE_ID,
)
RUNNING_SESSION_OBJ = attr_from_json(RUNNING_SESSION_DATA_RESPONSE, RunningSession)

STOP_SESSION_DATA = """
{
    "steps": 1,
    "matches": 1,
    "mismatches": 0,
    "missing": 0,
    "exactMatches": null,
    "strictMatches": null,
    "contentMatches": null,
    "layoutMatches": null,
    "noneMatches": null,
    "status": "Passed"
}"""
STOP_SESSION_OBJ = attr_from_json(STOP_SESSION_DATA, TestResults)

MATCH_WINDOW_DATA_OBJ = MatchWindowData(
    ignore_mismatch=False,
    user_inputs=[],
    app_output=AppOutput(title="Title", screenshot_bytes=None, screenshot_url="http"),
    tag="Tag",
    options=Options(
        name="Opt name",
        user_inputs=[],
        ignore_mismatch=False,
        ignore_match=False,
        force_match=False,
        force_mismatch=False,
        image_match_settings=SESSION_START_INFO_OBJ.default_match_settings,
        render_id=None,
    ),
    agent_setup="Agent setup",
    render_id=None,
)
IMAGE_BASE_64 = "iVBORw0KGgoAAAANSUhEUgAAAlgAAAJYCAYAAAC+ZpjcAAAFi0lEQVR4nO3BAQ0AAADCoPdPbQ43oAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIBXA/yTAAFLZiwOAAAAAElFTkSuQmCC"


def test_set_get_server_url():
    # type: () -> None
    connector = ServerConnector()
    connector.server_url = CUSTOM_EYES_SERVER
    assert connector.server_url == CUSTOM_EYES_SERVER


def test_check_default_server_url_from_settings():
    connector = ServerConnector()
    conf = Configuration()
    connector.update_config(conf)
    assert connector.server_url == DEFAULT_SERVER_URL


def test_set_get_api_key(connector):
    # type: (ServerConnector) -> None
    connector.api_key = API_KEY
    assert connector.api_key == API_KEY


def test_get_api_key_if_not_settled(connector, monkeypatch):
    # type: (ServerConnector, Any) -> None
    monkeypatch.setattr(os, "environ", {"APPLITOOLS_API_KEY": API_KEY})
    conf = Configuration()
    connector.update_config(conf)
    assert connector.api_key == API_KEY


def test_set_get_timeout(connector):
    # type: (ServerConnector) -> None
    connector.timeout_sec = 100
    assert connector.timeout_sec == 100


def test_is_session_started_True(started_connector):
    assert started_connector.is_session_started


def test_is_session_started_False(configured_connector):
    assert not configured_connector.is_session_started


def test_start_session(configured_connector):
    # type: (ServerConnector) -> None
    with patch("requests.post", side_effect=mocked_requests_post):
        running_session = configured_connector.start_session(SESSION_START_INFO_OBJ)
    assert running_session.id == RUNNING_SESSION_DATA_RESPONSE_ID
    assert running_session.session_id == RUNNING_SESSION_DATA_RESPONSE_SESSION_ID
    assert running_session.batch_id == RUNNING_SESSION_DATA_RESPONSE_BATCH_ID
    assert running_session.baseline_id == RUNNING_SESSION_DATA_RESPONSE_BASELINE_ID
    assert running_session.url == RUNNING_SESSION_DATA_RESPONSE_URL


def test_match_window(started_connector):
    #  type: (ServerConnector) -> None
    with patch("requests.post", side_effect=mocked_requests_post):
        match = started_connector.match_window(
            RUNNING_SESSION_OBJ, MATCH_WINDOW_DATA_OBJ
        )
    assert match.as_expected


@pytest.mark.parametrize("server_status", [500, 200, 201, 400, 404])
def test_match_window_with_image_uploading(started_connector, server_status):
    #  type: (ServerConnector, int) -> None
    data = copy(MATCH_WINDOW_DATA_OBJ)
    data.app_output.screenshot_url = None
    data.app_output.screenshot_bytes = image_utils.get_bytes(
        image_utils.image_from_base64(IMAGE_BASE_64)
    )
    rendering_info = RenderingInfo(
        access_token="some access",
        service_url="https://render-wus.applitools.com",
        results_url="https://eyespublicwustemp.blob.core.windows.net/temp/__random__?sv=2017-04-17&sr=c&sig=aAArw3au%",
    )
    with patch(
        "applitools.core.server_connector.ServerConnector.render_info",
        return_value=rendering_info,
    ):
        with patch("requests.put", return_value=MockResponse(None, server_status)):
            with patch("requests.post", side_effect=mocked_requests_post):

                if server_status in [200, 201]:
                    started_connector.match_window(RUNNING_SESSION_OBJ, data)
                else:
                    with pytest.raises(EyesError):
                        started_connector.match_window(RUNNING_SESSION_OBJ, data)

    if server_status in [200, 201]:
        target_url = data.app_output.screenshot_url
        assert target_url.startswith(
            "https://eyespublicwustemp.blob.core.windows.net/temp/"
        )
        assert target_url.endswith("?sv=2017-04-17&sr=c&sig=aAArw3au%")
        assert "__random__" not in target_url


def test_post_dom_snapshot(started_connector):
    #  type: (ServerConnector) -> None
    with patch("requests.post", side_effect=mocked_requests_post):
        dom_url = started_connector.post_dom_snapshot("{HTML: []")
    assert dom_url == RUNNING_SESSION_DATA_RESPONSE_URL


def test_stop_session(started_connector):
    #  type: (ServerConnector) -> None
    with patch("requests.delete", side_effect=mocked_requests_delete):
        respo = started_connector.stop_session(
            RUNNING_SESSION_OBJ, is_aborted=False, save=False
        )
    assert respo == attr_from_json(STOP_SESSION_DATA, TestResults)
    # should be False after stop_session
    assert not started_connector.is_session_started


def test_request_with_changed_values(configured_connector):
    new_timeout = 99999
    new_timeout_sec = int(new_timeout / 1000.0)
    new_api_key = "NEW API KEY"
    new_server_url = "http://new-server.com/"
    conf = Configuration(
        timeout=new_timeout, api_key=new_api_key, server_url=new_server_url
    )
    configured_connector.update_config(conf)

    with patch("requests.post") as mocked_post:
        with patch(
            "applitools.core.server_connector.json_utils.attr_from_response",
            return_value=RUNNING_SESSION_OBJ,
        ):
            configured_connector.start_session(SESSION_START_INFO_OBJ)

    assert mocked_post.call_args[1]["timeout"] == new_timeout_sec
    assert mocked_post.call_args[1]["params"]["apiKey"] == new_api_key
    assert new_server_url in mocked_post.call_args[0][0]


def test_long_request(configured_connector):
    with patch("requests.get", side_effect=mocked_requests_get):
        with patch("requests.delete", side_effect=mocked_requests_delete):
            r = configured_connector._com.long_request(requests.get, LONG_REQUEST_URL)
            assert r.status_code == 200


def test_get_rendering_info(started_connector):
    with patch("requests.get", side_effect=mocked_requests_get):
        render_info = started_connector.render_info()
    assert render_info == RENDERING_OBJ
