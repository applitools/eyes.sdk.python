from __future__ import absolute_import

import itertools
import json
import math
import typing
import uuid

import attr
import requests
from requests import Response
from requests.packages import urllib3  # noqa

from applitools.common import Region, RunningSession, logger
from applitools.common.errors import EyesError
from applitools.common.match import MatchResult
from applitools.common.match_window_data import MatchWindowData
from applitools.common.metadata import SessionStartInfo
from applitools.common.test_results import TestResults
from applitools.common.ultrafastgrid import (
    JobInfo,
    RenderingInfo,
    RenderRequest,
    RenderStatusResults,
    RunningRender,
    VGResource,
)
from applitools.common.utils import (
    argument_guard,
    datetime_utils,
    gzip_compress,
    iteritems,
    json_utils,
    urljoin,
)
from applitools.common.utils.compat import raise_from
from applitools.core.locators import LOCATORS_TYPE, VisualLocatorsData

if typing.TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Text, Union

# Prints out all data sent/received through 'requests'
# import httplib
# httplib.HTTPConnection.debuglevel = 1

# Remove Unverified SSL warnings propagated by requests' internal urllib3 module
if hasattr(urllib3, "disable_warnings") and callable(urllib3.disable_warnings):
    urllib3.disable_warnings()

__all__ = ("ServerConnector",)


def retry(
    delays=tuple(itertools.chain((1000,), (5000,) * 4, (10000,) * 4)),
    exception=(EyesError, requests.ConnectionError, requests.HTTPError),
    report=lambda *args: logger.debug,
):
    return datetime_utils.retry(delays, exception, report)


@attr.s
class ClientSession(object):
    """ A proxy to requests.Session """

    _session = attr.ib(
        factory=requests.Session
    )  # type: Union[requests, requests.Session]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        if isinstance(self._session, requests.Session):
            self._session.close()

    def request(self, method, url, **kwargs):
        # type: (Text, Text, **Any) -> Response
        method = method.lower()

        # refactored to "if" tree for easier monkey-patching during testing
        if method == "get":
            return self.get(url, **kwargs)
        if method == "options":
            return self.options(url, **kwargs)
        if method == "head":
            return self.head(url, **kwargs)
        if method == "post":
            return self.post(url, **kwargs)
        if method == "put":
            return self.put(url, **kwargs)
        if method == "patch":
            return self.patch(url, **kwargs)
        if method == "delete":
            return self.delete(url, **kwargs)

        raise ValueError("Unknown HTTP method: {}".format(method))

    def get(self, url, **kwargs):
        return self._session.get(url, **kwargs)

    def options(self, url, **kwargs):
        return self._session.options(url, **kwargs)

    def head(self, url, **kwargs):
        return self._session.head(url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        return self._session.post(url, data=data, json=json, **kwargs)

    def put(self, url, data=None, **kwargs):
        return self._session.put(url, data=data, **kwargs)

    def patch(self, url, data=None, **kwargs):
        return self._session.patch(url, data=data, **kwargs)

    def delete(self, url, **kwargs):
        return self._session.delete(url, **kwargs)


@attr.s
class _RequestCommunicator(object):
    LONG_REQUEST_DELAY_MS = 2000  # type: int
    MAX_LONG_REQUEST_DELAY_MS = 10000  # type: int
    LONG_REQUEST_DELAY_MULTIPLICATIVE_INCREASE_FACTOR = 1.5  # type: float

    headers = attr.ib()  # type: Dict
    timeout_ms = attr.ib(default=None)  # type: int
    api_key = attr.ib(default=None)  # type: Text
    server_url = attr.ib(default=None)  # type: Text
    client_session = attr.ib(factory=ClientSession)

    def close_session(self):
        """
        Closes all adapters and as such the client session.
        """
        self.client_session.close()

    def request(self, method, url_resource, use_api_key=True, **kwargs):
        # type: (Text, Text, bool, **Any) -> Response
        if url_resource is not None:
            # makes URL relative
            url_resource = url_resource.lstrip("/")
        url_resource = urljoin(self.server_url.rstrip("/"), url_resource)
        params = {}
        if use_api_key:
            params["apiKey"] = self.api_key
        params.update(kwargs.get("params", {}))
        headers = self.headers.copy()
        headers.update(kwargs.get("headers", {}))
        timeout_sec = kwargs.get("timeout", None)
        if timeout_sec is None:
            timeout_sec = datetime_utils.to_sec(self.timeout_ms)
        response = self.client_session.request(
            method,
            url_resource,
            data=kwargs.get("data", None),
            verify=False,
            params=params,
            headers=headers,
            timeout=timeout_sec,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            logger.exception(e)
        return response

    def long_request(self, method, url_resource, **kwargs):
        # type: (Text, Text, **Any) -> Response
        headers = kwargs.get("headers", self.headers).copy()
        headers["Eyes-Expect"] = "202+location"
        headers["Eyes-Date"] = datetime_utils.current_time_in_rfc1123()
        kwargs["headers"] = headers
        response = self.request(method, url_resource, **kwargs)
        logger.debug("Long request `{}` for {}".format(method, response.url))
        return self._long_request_check_status(response)

    def _long_request_check_status(self, response):
        if (
            response.status_code == requests.codes.ok
            or "Location" not in response.headers
        ):
            # request ends successful or it doesn't support Long request
            return response
        elif response.status_code == requests.codes.accepted:
            # long request here; calling received url to know that request was processed
            url = response.headers["Location"]
            response = self._long_request_loop(url)
            return self._long_request_check_status(response)
        elif response.status_code == requests.codes.created:
            # delete url that was used before
            url = response.headers["Location"]
            return self.request(
                "delete",
                url,
                headers={"Eyes-Date": datetime_utils.current_time_in_rfc1123()},
            )
        elif response.status_code == requests.codes.gone:
            raise EyesError("The server task has gone.")
        else:
            raise EyesError("Unknown error during long request: {}".format(response))

    def _long_request_loop(self, url, delay=LONG_REQUEST_DELAY_MS):
        delay = min(
            self.MAX_LONG_REQUEST_DELAY_MS,
            math.floor(delay * self.LONG_REQUEST_DELAY_MULTIPLICATIVE_INCREASE_FACTOR),
        )
        logger.debug("Long request. Still running... Retrying in {} ms".format(delay))

        datetime_utils.sleep(delay)
        response = self.request(
            "get", url, headers={"Eyes-Date": datetime_utils.current_time_in_rfc1123()}
        )
        if response.status_code != requests.codes.ok:
            return response
        return self._long_request_loop(url, delay)


class ServerConnector(object):
    """
    Provides an API for communication with the Applitools server.
    """

    DEFAULT_HEADERS = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-applitools-eyes-client": None,
    }

    API_SESSIONS = "api/sessions"
    API_SESSIONS_RUNNING = API_SESSIONS + "/running/"
    RUNNING_DATA_PATH = API_SESSIONS + "/running/data"

    # Rendering Grid
    RENDER_INFO_PATH = API_SESSIONS + "/renderinfo"
    RESOURCES_SHA_256 = "/resources/sha256/"
    RENDER_STATUS = "/render-status"
    RENDER = "/render"
    RENDERER_INFO = "/job-info"

    _is_session_started = False

    def __init__(self, client_session=None):
        # type: (Optional[ClientSession]) -> None
        """
        Ctor.

        :param client_session: session for communication with server.
        """
        self._render_info = None  # type: Optional[RenderingInfo]
        self._ua_string = None  # type: Optional[RenderingInfo]

        if client_session:
            self._com = _RequestCommunicator(
                headers=ServerConnector.DEFAULT_HEADERS, client_session=client_session
            )
        else:
            self._com = _RequestCommunicator(headers=ServerConnector.DEFAULT_HEADERS)

    def update_config(self, conf, full_agent_id, render_info=None, ua_string=None):
        if conf.api_key is None:
            raise EyesError(
                "API key not set! Log in to https://applitools.com to obtain your"
                " API Key and use 'api_key' to set it."
            )
        self._com.server_url = conf.server_url
        self._com.api_key = conf.api_key
        self._com.timeout_ms = conf._timeout
        if render_info:
            self._render_info = render_info
        if ua_string:
            self._ua_string = ua_string
        self.DEFAULT_HEADERS["x-applitools-eyes-client"] = full_agent_id

    @property
    def server_url(self):
        return self._com.server_url

    @server_url.setter
    def server_url(self, value):
        self._com.server_url = value

    @property
    def api_key(self):
        return self._com.api_key

    @api_key.setter
    def api_key(self, value):
        self._com.api_key = value

    @property
    def timeout(self):
        return self._com.timeout_ms

    @timeout.setter
    def timeout(self, value):
        self._com.timeout_ms = value

    @property
    def is_session_started(self):
        return self._is_session_started

    @property
    def client_session(self):
        # type: () -> ClientSession
        return self._com.client_session

    # TODO: Add Proxy
    def start_session(self, session_start_info):
        # type: (SessionStartInfo) -> RunningSession
        """
        Starts a new running session in the agent. Based on the given parameters,
        this running session will either be linked to an existing session, or to
        a completely new session.

        :param session_start_info: The start params for the session.
        :return: Represents the current running session.
        """
        logger.debug("start_session called.")
        data = json_utils.to_json(session_start_info)
        response = self._com.long_request(
            "post",
            url_resource=self.API_SESSIONS_RUNNING,
            data=data,
            headers=self.DEFAULT_HEADERS,
        )
        running_session = json_utils.attr_from_response(response, RunningSession)
        self._is_session_started = True
        return running_session

    def stop_session(self, running_session, is_aborted, save):
        # type: (RunningSession, bool, bool) -> TestResults
        """
        Stops a running session in the Eyes server.

        :param running_session: The session to stop.
        :param is_aborted: Whether the server should mark this session as aborted.
        :param save: Whether the session should be automatically saved if it is not aborted.
        :return: Test results of the stopped session.
        """
        logger.debug("stop_session called.")

        if not self.is_session_started:
            raise EyesError("Session not started")

        params = {"aborted": is_aborted, "updateBaseline": save}
        response = self._com.long_request(
            "delete",
            url_resource=urljoin(self.API_SESSIONS_RUNNING, running_session.id),
            params=params,
            headers=ServerConnector.DEFAULT_HEADERS,
        )

        test_results = json_utils.attr_from_response(response, TestResults)
        logger.debug("stop_session(): parsed response: {}".format(test_results))

        self._com.close_session()

        # mark that session isn't started
        self._is_session_started = False
        return test_results

    def _try_upload_data(self, bytes_data, content_type, media_type):
        # type: (bytes, Text, Text) -> Optional[Text]
        argument_guard.not_none(bytes_data)

        rendering_info = self.render_info()
        if rendering_info and rendering_info.results_url:
            try:
                target_url = rendering_info.results_url
                guid = uuid.uuid4()
                target_url = target_url.replace("__random__", str(guid))
                logger.debug("Uploading {} to {}".format(media_type, target_url))
                if self._upload_data(
                    bytes_data, rendering_info, target_url, content_type, media_type
                ):
                    return target_url
            except Exception as e:
                logger.error("Error uploading {}".format(media_type))
                logger.exception(e)

    @retry()
    def _upload_data(
        self, data_bytes, rendering_info, target_url, content_type, media_type
    ):
        # type: (bytes, RenderingInfo, Text, Text, Text) -> bool
        headers = ServerConnector.DEFAULT_HEADERS.copy()
        headers["Content-Type"] = content_type
        headers["Content-Length"] = str(len(data_bytes))
        headers["Media-Type"] = media_type
        headers["X-Auth-Token"] = rendering_info.access_token
        headers["x-ms-blob-type"] = "BlockBlob"

        timeout_sec = datetime_utils.to_sec(self._com.timeout_ms)
        response = self.client_session.request(
            "put",
            target_url,
            data=data_bytes,
            headers=headers,
            timeout=timeout_sec,
            verify=False,
        )
        if response.status_code in [requests.codes.ok, requests.codes.created]:
            logger.debug("Upload Status Code: {}".format(response.status_code))
            return True
        raise EyesError(
            "Failed to Upload. Status Code: {}".format(response.status_code)
        )

    def try_upload_image(self, data):
        # type: (bytes) -> Optional[Text]
        try:
            return self._try_upload_data(data, "image/png", "image/png")
        except EyesError as e:
            raise_from(EyesError("Failed to Upload Image"), e)

    def match_window(self, running_session, match_data):
        # type: (RunningSession, MatchWindowData) -> MatchResult
        """
        Matches the current window to the immediate expected window in the Eyes server.
        Notice that a window might be matched later at the end of the test, even if it
        was not immediately matched in this call.

        :param running_session: The current session that is running.
        :param match_data: The data for the requests.post.
        :return: The parsed response.
        """
        logger.debug("match_window called. {}".format(running_session))

        # logger.debug("Data length: %d, data: %s" % (len(data), repr(data)))
        if not self.is_session_started:
            raise EyesError("Session not started")
        app_output = match_data.app_output
        # when screenshot_url is present we don't need to upload again
        if app_output.screenshot_url is None and app_output.screenshot_bytes:
            app_output.screenshot_url = self.try_upload_image(
                match_data.app_output.screenshot_bytes
            )

        if app_output.screenshot_url is None:
            raise EyesError(
                "MatchWindow failed: could not upload image to storage service."
            )
        logger.info("Screenshot image URL: {}".format(app_output.screenshot_url))
        data = json_utils.to_json(match_data)
        headers = ServerConnector.DEFAULT_HEADERS.copy()
        response = self._com.long_request(
            "post",
            url_resource=urljoin(self.API_SESSIONS_RUNNING, running_session.id),
            data=data,
            headers=headers,
        )
        return json_utils.attr_from_response(response, MatchResult)

    def post_dom_capture(self, dom_json):
        # type: (Text) -> Optional[Text]
        """
        Upload the DOM of the tested page.
        Return an URL of uploaded resource which should be posted to :py:   `AppOutput`.
        """
        logger.debug("post_dom_snapshot called.")

        if not self.is_session_started:
            raise EyesError("Session not started")

        dom_bytes = gzip_compress(dom_json.encode("utf-8"))
        return self._try_upload_data(
            dom_bytes, "application/octet-stream", "application/json"
        )

    def _ufg_request(self, method, url_resource, **kwargs):
        headers = ServerConnector.DEFAULT_HEADERS.copy()
        headers["Content-Type"] = "application/json"
        headers["X-Auth-Token"] = self._render_info.access_token
        full_url = urljoin(self._render_info.service_url, url_resource)
        return self._com.request(method, full_url, headers=headers, **kwargs)

    def render_info(self):
        # type: () -> Optional[RenderingInfo]
        logger.debug("render_info() called.")
        if self._render_info:
            return self._render_info
        headers = ServerConnector.DEFAULT_HEADERS.copy()
        headers["Content-Type"] = "application/json"
        response = self._com.long_request("get", self.RENDER_INFO_PATH, headers=headers)
        if not response.ok:
            raise EyesError(
                "Cannot get render info: \n Status: {}, Content: {}".format(
                    response.status_code, response.content
                )
            )
        self._render_info = json_utils.attr_from_response(response, RenderingInfo)
        return self._render_info

    def render(self, *render_requests):
        # type: (*RenderRequest) -> List[RunningRender]
        logger.debug("render called with {}".format(render_requests))
        if self._render_info is None:
            raise EyesError("render_info must be fetched first")

        url = urljoin(self._render_info.service_url, self.RENDER)

        headers = ServerConnector.DEFAULT_HEADERS.copy()
        headers["Content-Type"] = "application/json"
        headers["X-Auth-Token"] = self._render_info.access_token

        data = json_utils.to_json(render_requests)
        response = self._com.request(
            "post", url_resource=url, use_api_key=False, headers=headers, data=data
        )
        if response.ok or response.status_code == requests.codes.not_found:
            return json_utils.attr_from_response(response, RunningRender)
        raise EyesError(
            "ServerConnector.render - unexpected status ({})\n\tcontent{}".format(
                response.status_code, response.content
            )
        )

    def render_put_resource(self, render_id, resource):
        # type: (Text, VGResource) -> Text
        argument_guard.not_none(resource)
        render_id = render_id or "NONE"
        if self._render_info is None:
            raise EyesError("render_info must be fetched first")

        content = resource.content
        argument_guard.not_none(content)
        logger.debug(
            "resource hash: {} url: {} render id: {}"
            "".format(resource.hash, resource.url, render_id)
        )
        headers = ServerConnector.DEFAULT_HEADERS.copy()
        headers["Content-Type"] = resource.content_type
        headers["X-Auth-Token"] = self._render_info.access_token

        url = urljoin(
            self._render_info.service_url, self.RESOURCES_SHA_256 + resource.hash
        )
        response = self._com.request(
            "put",
            url,
            use_api_key=False,
            headers=headers,
            data=content,
            params={"render-id": render_id},
        )
        logger.debug("ServerConnector.put_resource - request succeeded")
        if not response.ok:
            raise EyesError(
                "Error putting resource: {}, {}".format(
                    response.status_code, response.content
                )
            )
        return resource.hash

    @retry()
    def download_resource(self, url):
        # type: (Text) -> Response
        headers = {
            "Accept-Encoding": "identity",
            "Accept-Language": "*",
        }
        if self._ua_string:
            headers["User-Agent"] = self._ua_string
        logger.debug("Fetching URL {}\nwith headers {}".format(url, headers))
        timeout_sec = datetime_utils.to_sec(self._com.timeout_ms)
        try:
            response = requests.get(
                url, headers=headers, timeout=timeout_sec, verify=False
            )
            if response.status_code == requests.codes.not_acceptable:
                response = requests.get(url, timeout=timeout_sec, verify=False)
            return response
        except (requests.HTTPError, requests.ConnectionError):
            response = Response()
            response._content = b""
            response.status_code = requests.codes.no_response
            return response

    def render_status_by_id(self, *render_ids):
        # type: (*Text) -> List[RenderStatusResults]
        argument_guard.not_none(render_ids)
        if self._render_info is None:
            raise EyesError("render_info must be fetched first")

        headers = ServerConnector.DEFAULT_HEADERS.copy()
        headers["Content-Type"] = "application/json"
        headers["X-Auth-Token"] = self._render_info.access_token
        url = urljoin(self._render_info.service_url, self.RENDER_STATUS)
        response = self._com.request(
            "post",
            url,
            use_api_key=False,
            headers=headers,
            data=json.dumps(render_ids),
        )
        if not response.ok:
            raise EyesError(
                "Error getting server status, {} {}".format(
                    response.status_code, response.content
                )
            )
        # TODO: improve parser to handle similar names
        return json_utils.attr_from_response(response, RenderStatusResults)

    @retry()
    def post_locators(self, visual_locators_data):
        # type: (VisualLocatorsData) -> LOCATORS_TYPE
        data = json_utils.to_json(visual_locators_data)
        response = self._com.long_request("post", "api/locators/locate", data=data)
        response.raise_for_status()
        return {
            locator_id: json_utils.attr_from_dict(regions, Region)
            for locator_id, regions in iteritems(response.json())
        }

    @retry()
    def job_info(self, render_request):
        # type: (List[RenderRequest]) -> List[JobInfo]
        resp = self._ufg_request(
            "post", self.RENDERER_INFO, data=json_utils.to_json(render_request)
        )
        resp.raise_for_status()
        # TODO: improve parser to skip parsing of inner structures if required
        return [
            JobInfo(
                renderer=d.get("renderer"), eyes_environment=d.get("eyesEnvironment")
            )
            for d in resp.json()
        ]
