import json
import os
from collections import deque
from concurrent.futures.thread import ThreadPoolExecutor
from copy import copy, deepcopy
from typing import Any

import pytest
import requests
from mock import ANY, MagicMock, call, patch

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
from applitools.common.errors import EyesServiceUnavailableError
from applitools.common.server import SessionType
from applitools.common.ultrafastgrid import RenderingInfo
from applitools.common.utils import datetime_utils, image_utils
from applitools.common.utils.compat import urljoin
from applitools.common.utils.datetime_utils import sleep, to_sec
from applitools.common.utils.json_utils import attr_from_json
from applitools.core import ServerConnector
from applitools.core.server_connector import (
    ClientSession,
    _RequestCommunicator,
    _SessionRetryLimiter,
)

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
    def __init__(self, url, json_data, status_code, headers=None):
        self.url = url
        self.json_data = json_data
        self.status_code = status_code
        if headers is None:
            headers = {}
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


def mocked_client_session_request(self, *args, **kwargs):
    http_method = args[0]
    args = args[1:]
    if not isinstance(http_method, str):
        raise DeprecationWarning("Use text instead!")

    if http_method == "get":
        return mocked_requests_get(*args, **kwargs)
    if http_method == "post":
        return mocked_requests_post(*args, **kwargs)
    if http_method == "delete":
        return mocked_requests_delete(*args, **kwargs)

    raise NotImplementedError(
        "MockClientSession does not have implementation for {} method".format(
            http_method.upper()
        )
    )


def mocked_requests_delete(*args, **kwargs):
    _request_check(*args, **kwargs)
    url = args[0]
    if url == urljoin(RUNNING_SESSION_URL, RUNNING_SESSION_DATA_RESPONSE_ID):
        return MockResponse(url, STOP_SESSION_DATA, 200)
    elif url == LONG_REQUEST_RESPONSE_URL:
        return MockResponse(url, {}, 200)
    return MockResponse(url, None, 404)


def mocked_requests_get(*args, **kwargs):
    _request_check(*args, **kwargs)
    url = args[0]
    if url == RENDER_INFO_PATH_URL:
        return MockResponse(url, RENDERING_INFO_DATA, 200)
    if url == LONG_REQUEST_URL:
        return MockResponse(url, None, 202, {"Location": LONG_REQUEST_RESPONSE_URL})
    if url == LONG_REQUEST_RESPONSE_URL:
        return MockResponse(url, None, 201, {"Location": LONG_REQUEST_RESPONSE_URL})
    return MockResponse(url, None, 404)


def mocked_requests_post(*args, **kwargs):
    _request_check(*args, **kwargs)
    url = args[0]
    if url == RUNNING_SESSION_URL:
        return MockResponse(url, RUNNING_SESSION_DATA_RESPONSE, 201)
    elif url == urljoin(RUNNING_SESSION_URL, RUNNING_SESSION_DATA_RESPONSE_ID):
        return MockResponse(url, '{"asExpected": true}', 200)
    elif url == RUNNING_SESSION_DATA_URL:
        return MockResponse(
            url, {}, 200, headers={"Location": RUNNING_SESSION_DATA_RESPONSE_URL}
        )
    return MockResponse(url, None, 404)


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
    agent_session_id="1",
    agent_run_id="Some-Agent-Run-ID",
)
RUNNING_SESSION_DATA_RESPONSE_ID = "some id"
RUNNING_SESSION_DATA_RESPONSE_URL = "http://some-session-url.com"
RUNNING_SESSION_DATA_RESPONSE_SESSION_ID = "some session id"
RUNNING_SESSION_DATA_RESPONSE_BATCH_ID = "other url"
RUNNING_SESSION_DATA_RESPONSE_BASELINE_ID = "other url"
RUNNING_SESSION_DATA_RESPONSE_IS_NEW = True
RAW_RUNNING_SESSION_DATA_RESPONSE = {
    "id": RUNNING_SESSION_DATA_RESPONSE_ID,
    "sessionId": RUNNING_SESSION_DATA_RESPONSE_SESSION_ID,
    "url": RUNNING_SESSION_DATA_RESPONSE_URL,
    "batchId": RUNNING_SESSION_DATA_RESPONSE_BATCH_ID,
    "baselineId": RUNNING_SESSION_DATA_RESPONSE_BASELINE_ID,
    "isNew": RUNNING_SESSION_DATA_RESPONSE_IS_NEW,
}
RUNNING_SESSION_DATA_RESPONSE = json.dumps(RAW_RUNNING_SESSION_DATA_RESPONSE)
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
    app_output=AppOutput(
        title="Title", screenshot_bytes=b"some", screenshot_url="http"
    ),
    tag="Tag",
    options=Options(
        name="Opt name",
        user_inputs=[],
        replace_last=False,
        ignore_mismatch=False,
        ignore_match=False,
        force_match=False,
        force_mismatch=False,
        image_match_settings=SESSION_START_INFO_OBJ.default_match_settings,
        source=None,
        render_id=None,
        variant_id="Varian",
    ),
    agent_setup="Agent setup",
    render_id=None,
)
IMAGE_BASE_64 = "iVBORw0KGgoAAAANSUhEUgAAAlgAAAJYCAYAAAC+ZpjcAAAFi0lEQVR4nO3BAQ0AAADCoPdPbQ43oAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIBXA/yTAAFLZiwOAAAAAElFTkSuQmCC"

ALLOWED_HTTP_METHODS = ["head", "options", "get", "post", "put", "patch", "delete"]
ALLOWED_HTTP_METHODS += [m.upper() for m in ALLOWED_HTTP_METHODS]
FAKE_HTTP_METHODS = [
    "4hdy6sh",
]
