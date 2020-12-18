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
    Point,
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
        title="Title",
        location=Point(0, 0),
        screenshot_bytes=b"some",
        screenshot_url="http",
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


def test_set_get_server_url():
    # type: () -> None
    connector = ServerConnector()
    connector.server_url = CUSTOM_EYES_SERVER
    assert connector.server_url == CUSTOM_EYES_SERVER


def test_check_default_server_url_from_settings():
    connector = ServerConnector()
    conf = Configuration()
    connector.update_config(conf, "eyes.test")
    assert connector.server_url == DEFAULT_SERVER_URL


def test_set_get_api_key(connector):
    # type: (ServerConnector) -> None
    connector.api_key = API_KEY
    assert connector.api_key == API_KEY


def test_get_api_key_if_not_settled(connector, monkeypatch):
    # type: (ServerConnector, Any) -> None
    monkeypatch.setattr(os, "environ", {"APPLITOOLS_API_KEY": API_KEY})
    conf = Configuration()
    connector.update_config(conf, "eyes.test")
    assert connector.api_key == API_KEY


def test_set_get_timeout(connector):
    # type: (ServerConnector) -> None
    connector.timeout_sec = 100
    assert connector.timeout_sec == 100


def test_is_session_started_True(started_connector):
    assert started_connector.is_session_started


def test_is_session_started_False(configured_connector):
    assert not configured_connector.is_session_started


@patch(
    "applitools.core.server_connector.ClientSession.request",
    new=mocked_client_session_request,
)
def test_start_session(configured_connector):
    # type: (ServerConnector) -> None
    running_session = configured_connector.start_session(SESSION_START_INFO_OBJ)
    assert running_session.id == RUNNING_SESSION_DATA_RESPONSE_ID
    assert running_session.session_id == RUNNING_SESSION_DATA_RESPONSE_SESSION_ID
    assert running_session.batch_id == RUNNING_SESSION_DATA_RESPONSE_BATCH_ID
    assert running_session.baseline_id == RUNNING_SESSION_DATA_RESPONSE_BASELINE_ID
    assert running_session.url == RUNNING_SESSION_DATA_RESPONSE_URL
    assert running_session.is_new_session == RUNNING_SESSION_DATA_RESPONSE_IS_NEW


@patch(
    "applitools.core.server_connector.ClientSession.request",
    new=mocked_client_session_request,
)
def test_match_window(started_connector):
    #  type: (ServerConnector) -> None
    match = started_connector.match_window(RUNNING_SESSION_OBJ, MATCH_WINDOW_DATA_OBJ)
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
        stitching_service_url="https://some.stitchingserviceuri.com",
    )
    with patch(
        "applitools.core.server_connector.ServerConnector.render_info",
        return_value=rendering_info,
    ):
        with patch(
            "applitools.core.server_connector.ClientSession.put",
            return_value=MockResponse(None, None, server_status),
        ):
            with patch(
                "applitools.core.server_connector.ClientSession.post",
                side_effect=mocked_requests_post,
            ):
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


def test_post_dom_capture(started_connector):
    #  type: (ServerConnector) -> None
    with patch(
        "applitools.core.server_connector.ServerConnector.render_info",
        return_value=RENDERING_OBJ,
    ):
        with patch(
            "applitools.core.server_connector.ServerConnector._upload_data",
            return_value=True,
        ):
            dom_url = started_connector.post_dom_capture("{HTML: []")
            assert dom_url == RENDERING_OBJ.results_url


@patch(
    "applitools.core.server_connector.ClientSession.request",
    new=mocked_client_session_request,
)
def test_stop_session(started_connector):
    #  type: (ServerConnector) -> None
    respo = started_connector.stop_session(
        RUNNING_SESSION_OBJ, is_aborted=False, save=False
    )
    assert respo == attr_from_json(STOP_SESSION_DATA, TestResults)
    # should be False after stop_session
    assert not started_connector.is_session_started


def test_request_with_changed_values(configured_connector):
    new_timeout = 99999
    new_timeout_sec = to_sec(new_timeout)
    new_api_key = "NEW API KEY"
    new_server_url = "http://new-server.com/"
    conf = Configuration(
        timeout=new_timeout, api_key=new_api_key, server_url=new_server_url
    )
    configured_connector.update_config(conf, "eyes.test")

    with patch(
        "applitools.core.server_connector.ClientSession.request"
    ) as mocked_request:
        with patch(
            "applitools.core.server_connector.json_utils.attr_from_response",
            return_value=RUNNING_SESSION_OBJ,
        ):
            configured_connector.start_session(SESSION_START_INFO_OBJ)

    assert mocked_request.call_args[1]["timeout"] == new_timeout_sec
    assert mocked_request.call_args[1]["params"]["apiKey"] == new_api_key
    assert new_server_url in mocked_request.call_args[0][1]


@patch(
    "applitools.core.server_connector.ClientSession.request",
    new=mocked_client_session_request,
)
def test_long_request(configured_connector):
    r = configured_connector._com.long_request("get", LONG_REQUEST_URL)
    assert r.status_code == 200


@patch(
    "applitools.core.server_connector.ClientSession.request",
    new=mocked_client_session_request,
)
def test_long_request_on_start_session(configured_connector):
    r = configured_connector._com.long_request("post", RUNNING_SESSION_URL)
    assert r.status_code == 201


@patch(
    "applitools.core.server_connector.ClientSession.request",
    new=mocked_client_session_request,
)
def test_get_rendering_info(started_connector):
    render_info = started_connector.render_info()
    assert render_info == RENDERING_OBJ


@patch("requests.Session.request", return_value=MockResponse(None, None, 200))
@pytest.mark.parametrize("http_method", ALLOWED_HTTP_METHODS + FAKE_HTTP_METHODS)
def test_http_methods(configured_connector, http_method):
    client_session = ClientSession()
    if http_method in ALLOWED_HTTP_METHODS:
        r = client_session.request(http_method, "http://httpbin.org/anything")
        assert r.status_code == 200
    else:
        with pytest.raises(ValueError):
            client_session.request(http_method, "http://httpbin.org/anything")


@pytest.mark.parametrize(
    "render_json",
    [
        '{"ServiceUrl": "url","AccessToken": "token","ResultsUrl": "result"}',
        '{"ServiceUrl": "url","StitchingServiceUrl": "stitching"}',
        '{"ServiceUrl": "url","ResultsUrl": "result"}',
    ],
)
def test_parse_render_info_no_error(render_json):
    ri = attr_from_json(render_json, RenderingInfo)
    if ri.service_url:
        assert ri.service_url == "url"
    if ri.access_token:
        assert ri.access_token == "token"
    if ri.results_url:
        assert ri.results_url == "result"
    if ri.stitching_service_url:
        assert ri.stitching_service_url == "stitching"


def test_server_communicator_request_sets_random_request_id_header():
    session_mock = MagicMock()
    communicator = _RequestCommunicator({}, 1, "a", "b", client_session=session_mock)

    communicator.request("get", "https://c.com/")

    assert (
        "x-applitools-eyes-client-request-id"
        in session_mock.request.call_args.kwargs["headers"]
    )


def test_server_communicator_request_sets_provided_request_id_header():
    session_mock = MagicMock()
    communicator = _RequestCommunicator({}, 1, "a", "b", client_session=session_mock)

    communicator.request("get", "https://c.com/", request_id="d")

    headers = session_mock.request.call_args.kwargs["headers"]
    assert headers["x-applitools-eyes-client-request-id"] == "d"


def test_server_communicator_long_request_calls_all_have_same_request_id():
    response1 = MagicMock()
    response1.status_code = requests.codes.accepted
    response1.headers = {"Location": "e"}
    response2 = MagicMock()
    response2.status_code = requests.codes.created
    response2.headers = {"Location": "f"}
    session_mock = MagicMock()
    session_mock.request = MagicMock(side_effect=[response1, response2, MagicMock()])
    communicator = _RequestCommunicator({}, 1, "a", "b", client_session=session_mock)

    communicator.long_request("get", "https://c.com/")

    calls = session_mock.request.call_args_list
    assert (
        calls[0].kwargs["headers"]["x-applitools-eyes-client-request-id"]
        == calls[1].kwargs["headers"]["x-applitools-eyes-client-request-id"]
        == calls[2].kwargs["headers"]["x-applitools-eyes-client-request-id"]
    )


def test_retry_limiter_serializes_open_session_calls(monkeypatch):
    monkeypatch.setattr(ServerConnector, "_retry_limiter", _SessionRetryLimiter(9, 0.1))
    response = MagicMock()
    response.text = (
        '{"id": 1, "session_id": 2, "batch_id": 3, "baseline_id": 4, "url": 5}'
    )
    long_request_calls = []
    # Simulate sequential errors from eyes server that should make server connector
    # allow only one parallel start_session call at a time
    returns = deque(
        (
            EyesServiceUnavailableError(),
            EyesServiceUnavailableError(),
            EyesServiceUnavailableError(),
            EyesServiceUnavailableError(),
            EyesServiceUnavailableError(),
            response,
            EyesServiceUnavailableError(),
            EyesServiceUnavailableError(),
            EyesServiceUnavailableError(),
            EyesServiceUnavailableError(),
            response,
            EyesServiceUnavailableError(),
            EyesServiceUnavailableError(),
            response,
        )
    )

    def long_request_mock(*args, **kwargs):
        long_request_calls.append((args, kwargs))
        sleep(0.01)
        res = returns.popleft()
        if isinstance(res, Exception):
            raise res
        else:
            return res

    connector1 = ServerConnector()
    connector1._com = MagicMock()
    connector1._com.long_request = long_request_mock
    connector2 = deepcopy(connector1)
    connector3 = deepcopy(connector1)

    with ThreadPoolExecutor(3) as executor:
        future1 = executor.submit(connector1.start_session, 1)
        future2 = executor.submit(connector2.start_session, 2)
        future3 = executor.submit(connector3.start_session, 3)
    future1.result(), future2.result(), future3.result()
    request_ids = "".join(c[1]["data"] for c in long_request_calls)
    assert len(request_ids) == 14
    assert "111" in request_ids
    assert "333" in request_ids


def test_communicator_long_request_immediate_response_200():
    expected_response = MockResponse("url1", None, 200)
    mocked_session = MagicMock()
    mocked_session.request = MagicMock(side_effect=[expected_response])
    communicator = _RequestCommunicator({"a": "b"}, 1000, "key", "d", mocked_session)

    communicator.long_request("post", "url2")

    assert mocked_session.request.call_args_list == [
        call(
            "post",
            "url2",
            data=None,
            verify=False,
            params={"apiKey": "key"},
            headers={
                "a": "b",
                "Eyes-Expect": "202+location",
                "Eyes-Expect-Version": "2",
                "Eyes-Date": ANY,
                "x-applitools-eyes-client-request-id": ANY,
            },
            timeout=1.0,
        )
    ]


def test_communicator_long_request_no_wait():
    mocked_session = MagicMock()
    mocked_session.request = MagicMock(
        side_effect=[
            MockResponse("url1", None, 202, {"Location": "url2"}),
            MockResponse("url2", None, 201, {"Location": "url3"}),
            MockResponse("url3", None, 200),
        ]
    )
    communicator = _RequestCommunicator({"a": "b"}, 1000, "key", "d", mocked_session)

    communicator.long_request("post", "url1")

    assert mocked_session.request.call_args_list == [
        call(
            "post",
            "url1",
            data=None,
            verify=False,
            params={"apiKey": "key"},
            headers={
                "a": "b",
                "Eyes-Expect": "202+location",
                "Eyes-Expect-Version": "2",
                "Eyes-Date": ANY,
                "x-applitools-eyes-client-request-id": ANY,
            },
            timeout=1.0,
        ),
        call(
            "get",
            "url2",
            data=None,
            verify=False,
            params={"apiKey": "key"},
            headers={
                "a": "b",
                "Eyes-Date": ANY,
                "x-applitools-eyes-client-request-id": ANY,
            },
            timeout=1.0,
        ),
        call(
            "delete",
            "url3",
            data=None,
            verify=False,
            params={"apiKey": "key"},
            headers={
                "a": "b",
                "Eyes-Date": ANY,
                "x-applitools-eyes-client-request-id": ANY,
            },
            timeout=1.0,
        ),
    ]


def test_communicator_long_request_redirects_and_waiting(monkeypatch):
    sleep_mock = MagicMock()
    monkeypatch.setattr(datetime_utils, "sleep", sleep_mock)
    mocked_session = MagicMock()
    mocked_session.request = MagicMock(
        side_effect=[
            MockResponse("url1", None, 202, {"Location": "url2"}),
            MockResponse("url2", None, 200, {"Retry-After": "3"}),
            MockResponse("url2", None, 200, {"Location": "url3"}),
            MockResponse("url3", None, 201, {"Location": "url4"}),
            MockResponse("url4", None, 200),
        ]
    )
    communicator = _RequestCommunicator({"a": "b"}, 1000, "key", "d", mocked_session)

    communicator.long_request("post", "url1")

    # Filter out call(10, msg='Waiting for task', verbose=False) calls generated by
    # leaked VisualGridRunner thread
    sleep_calls = [c for c in sleep_mock.call_args_list if "msg" not in c.kwargs]
    assert sleep_calls == [
        call(500, ANY),
        call(3000, ANY),
        call(500, ANY),
    ]
    assert mocked_session.request.call_args_list == [
        call(
            "post",
            "url1",
            data=None,
            verify=False,
            params={"apiKey": "key"},
            headers={
                "a": "b",
                "Eyes-Expect": "202+location",
                "Eyes-Expect-Version": "2",
                "Eyes-Date": ANY,
                "x-applitools-eyes-client-request-id": ANY,
            },
            timeout=1.0,
        ),
        call(
            "get",
            "url2",
            data=None,
            verify=False,
            params={"apiKey": "key"},
            headers={
                "a": "b",
                "Eyes-Date": ANY,
                "x-applitools-eyes-client-request-id": ANY,
            },
            timeout=1.0,
        ),
        call(
            "get",
            "url2",
            data=None,
            verify=False,
            params={"apiKey": "key"},
            headers={
                "a": "b",
                "Eyes-Date": ANY,
                "x-applitools-eyes-client-request-id": ANY,
            },
            timeout=1.0,
        ),
        call(
            "get",
            "url3",
            data=None,
            verify=False,
            params={"apiKey": "key"},
            headers={
                "a": "b",
                "Eyes-Date": ANY,
                "x-applitools-eyes-client-request-id": ANY,
            },
            timeout=1.0,
        ),
        call(
            "delete",
            "url4",
            data=None,
            verify=False,
            params={"apiKey": "key"},
            headers={
                "a": "b",
                "Eyes-Date": ANY,
                "x-applitools-eyes-client-request-id": ANY,
            },
            timeout=1.0,
        ),
    ]
