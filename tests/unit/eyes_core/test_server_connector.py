import os

import pytest
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
from applitools.common.server import SessionType
from applitools.common.utils.compat import urljoin
from applitools.common.utils.general_utils import json_response_to_attrs_class
from applitools.common.visual_grid import RenderingInfo
from applitools.core import ServerConnector

API_KEY = "TEST API KEY"
CUSTOM_EYES_SERVER = "http://custom-eyes-server.com"

API_SESSIONS = "api/sessions"
API_SESSIONS_RUNNING = API_SESSIONS + "/running/"
RUNNING_DATA_PATH = API_SESSIONS + "/running/data"
RENDER_INFO_PATH = API_SESSIONS + "/renderinfo"

RUNNING_SESSION_URL = urljoin(CUSTOM_EYES_SERVER, API_SESSIONS_RUNNING)
RUNNING_SESSION_DATA_URL = urljoin(RUNNING_SESSION_URL, "data")
RENDER_INFO_PATH_URL = urljoin(CUSTOM_EYES_SERVER, RENDER_INFO_PATH)

RENDER_INFO_URL = "https://render-wus.applitools.com"
RENDER_INFO_AT = "Some Token"
RENDERING_INFO_DATA = {
    "ServiceUrl": RENDER_INFO_URL,
    "AccessToken": RENDER_INFO_AT,
    "ResultsUrl": RUNNING_SESSION_DATA_URL + "?accessKey=" + API_KEY,
}
RENDERING_OBJ = json_response_to_attrs_class(RENDERING_INFO_DATA, RenderingInfo)


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
        return self.json_data

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
    if url == urljoin(RUNNING_SESSION_URL, RUNNING_SESSION_DATA["id"]):
        return MockResponse(STOP_SESSION_DATA, 200)
    return MockResponse(None, 404)


def mocked_requests_get(*args, **kwargs):
    _request_check(*args, **kwargs)
    url = args[0]
    if url == RENDER_INFO_PATH_URL:
        return MockResponse(RENDERING_INFO_DATA, 200)
    return MockResponse(None, 404)


def mocked_requests_post(*args, **kwargs):
    _request_check(*args, **kwargs)
    url = args[0]
    if url == RUNNING_SESSION_URL:
        return MockResponse(RUNNING_SESSION_DATA, 201)
    elif url == urljoin(RUNNING_SESSION_URL, RUNNING_SESSION_DATA["id"]):
        return MockResponse({"asExpected": True}, 200)
    elif url == RUNNING_SESSION_DATA_URL:
        return MockResponse({}, 200, headers={"Location": RUNNING_SESSION_DATA["url"]})
    return MockResponse(None, 404)


SESSION_START_INFO_DATA = {
    "scenarioIdOrName": "TestName",
    "batchInfo": {
        "name": None,
        "startedAt": "YYYY-MM-DD HH:MM:SS.mmmmmm",
        "id": "UUID ID",
    },
    "envName": None,
    "environment": None,
    "defaultMatchSettings": {"matchLevel": "STRICT", "exact": None},
    "verId": None,
    "branchName": None,
    "parentBranchName": None,
    "properties": [],
}
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
    compare_with_parent_branch=False,
    ignore_baseline=False,
    save_diffs=True,
    render=False,
    properties=[],
)
RUNNING_SESSION_DATA = {
    "id": "some id",
    "sessionId": "some session id",
    "url": "http://some-session-url.com",
    "batchId": "other url",
    "baselineId": "other url",
}
RUNNING_SESSION_OBJ = json_response_to_attrs_class(RUNNING_SESSION_DATA, RunningSession)

STOP_SESSION_DATA = {
    "steps": 1,
    "matches": 1,
    "mismatches": 0,
    "missing": 0,
    "exactMatches": None,
    "strictMatches": None,
    "contentMatches": None,
    "layoutMatches": None,
    "noneMatches": None,
    "status": "Passed",
}
STOP_SESSION_OBJ = json_response_to_attrs_class(STOP_SESSION_DATA, TestResults)

MATCH_WINDOW_DATA_OBJ = MatchWindowData(
    ignore_mismatch=False,
    user_inputs=[],
    app_output=AppOutput(title="Title", screenshot64="some image"),
    tag="Tag",
    options=Options(
        name="Opt name",
        user_inputs=[],
        ignore_mismatch=False,
        ignore_match=False,
        force_match=False,
        force_mismatch=False,
        image_match_settings=SESSION_START_INFO_OBJ.default_match_settings,
    ),
)


def test_set_get_server_url():
    # type: () -> None
    connector = ServerConnector(CUSTOM_EYES_SERVER)
    assert connector.server_url == CUSTOM_EYES_SERVER


def test_set_default_server_url_if_none_passed_as_url():
    connector = ServerConnector(None)
    assert connector.server_url == ServerConnector.DEFAULT_SERVER_URL


def test_set_get_api_key(connector):
    # type: (ServerConnector) -> None
    connector.api_key = API_KEY
    assert connector.api_key == API_KEY


def test_get_api_key_if_not_settled(connector):
    # type: (ServerConnector) -> None
    os.environ["APPLITOOLS_API_KEY"] = API_KEY
    assert connector.api_key == API_KEY


def test_set_get_timeout(connector):
    # type: (ServerConnector) -> None
    connector.timeout = 100
    assert connector.timeout == 100


def test_is_session_started_True(started_connector):
    assert started_connector.is_session_started


def test_is_session_started_False(configured_connector):
    assert not configured_connector.is_session_started


def test_start_session(configured_connector):
    # type: (ServerConnector) -> None
    with patch("requests.post", side_effect=mocked_requests_post):
        running_session = configured_connector.start_session(SESSION_START_INFO_OBJ)
    assert running_session.id == RUNNING_SESSION_DATA["id"]
    assert running_session.session_id == RUNNING_SESSION_DATA["sessionId"]
    assert running_session.batch_id == RUNNING_SESSION_DATA["batchId"]
    assert running_session.baseline_id == RUNNING_SESSION_DATA["baselineId"]
    assert running_session.url == RUNNING_SESSION_DATA["url"]


def test_match_window(started_connector):
    #  type: (ServerConnector) -> None
    with patch("requests.post", side_effect=mocked_requests_post):
        with patch(
            "applitools.core.server_connector.ServerConnector._prepare_data",
            return_value=b"Some value",
        ):
            match = started_connector.match_window(
                RUNNING_SESSION_OBJ, MATCH_WINDOW_DATA_OBJ
            )
    assert match.as_expected


def test_post_dom_snapshot(started_connector):
    #  type: (ServerConnector) -> None
    with patch("requests.post", side_effect=mocked_requests_post):
        dom_url = started_connector.post_dom_snapshot("{HTML: []")
    assert dom_url == RUNNING_SESSION_DATA["url"]


def test_stop_session(started_connector):
    #  type: (ServerConnector) -> None
    with patch("requests.delete", side_effect=mocked_requests_delete):
        respo = started_connector.stop_session(
            RUNNING_SESSION_OBJ, is_aborted=False, save=False
        )
    assert respo == json_response_to_attrs_class(STOP_SESSION_DATA, TestResults)
    # should be False after stop_session
    assert not started_connector.is_session_started


def test_raise_error_when_session_was_not_run(configured_connector):
    with pytest.raises(EyesError):
        configured_connector.match_window(RUNNING_SESSION_OBJ, b"data")
    with pytest.raises(EyesError):
        configured_connector.post_dom_snapshot("{HTML: []")
    with pytest.raises(EyesError):
        configured_connector.stop_session(
            RUNNING_SESSION_OBJ, is_aborted=False, save=False
        )


def test_request_with_changed_values(configured_connector):
    new_timeout = 99999
    new_api_key = "NEW API KEY"
    new_server_url = "http://new-server.com/"
    configured_connector.timeout = new_timeout
    configured_connector.api_key = new_api_key
    configured_connector.server_url = new_server_url

    with patch("requests.post") as mocked_post:
        with patch(
            "applitools.core.server_connector.json_response_to_attrs_class",
            return_value=RUNNING_SESSION_OBJ,
        ):
            configured_connector.start_session(SESSION_START_INFO_OBJ)

    assert mocked_post.call_args[1]["timeout"] == new_timeout
    assert mocked_post.call_args[1]["params"]["apiKey"] == new_api_key
    assert new_server_url in mocked_post.call_args[0][0]


def test_get_rendering_info(started_connector):
    with patch("requests.get", side_effect=mocked_requests_get):
        render_info = started_connector.get_render_info()
    assert render_info == RENDERING_OBJ
