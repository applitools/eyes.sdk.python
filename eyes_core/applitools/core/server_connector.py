from __future__ import absolute_import

import json
import math
import time
import typing
from struct import pack

import attr
import requests
from requests import Response
from requests.packages import urllib3  # noqa

from applitools.common import RunningSession, logger
from applitools.common.errors import EyesError
from applitools.common.match import MatchResult
from applitools.common.match_window_data import MatchWindowData
from applitools.common.metadata import SessionStartInfo
from applitools.common.test_results import TestResults
from applitools.common.utils import (
    argument_guard,
    datetime_utils,
    gzip_compress,
    image_utils,
    json_utils,
    urljoin,
)
from applitools.common.visual_grid import (
    RenderingInfo,
    RenderRequest,
    RenderStatusResults,
    RunningRender,
    VGResource,
)

if typing.TYPE_CHECKING:
    from typing import Text, List, Any, Optional, Dict, Tuple
    from applitools.common.utils.custom_types import Num

# Prints out all data sent/received through 'requests'
# import httplib
# httplib.HTTPConnection.debuglevel = 1

# Remove Unverified SSL warnings propagated by requests' internal urllib3 module
if hasattr(urllib3, "disable_warnings") and callable(urllib3.disable_warnings):
    urllib3.disable_warnings()

__all__ = ("ServerConnector",)


@attr.s
class _RequestCommunicator(object):
    LONG_REQUEST_DELAY_MS = 2000  # type: int
    MAX_LONG_REQUEST_DELAY_MS = 10000  # type: int
    LONG_REQUEST_DELAY_MULTIPLICATIVE_INCREASE_FACTOR = 1.5  # type: float

    headers = attr.ib()  # type: Dict
    timeout_ms = attr.ib(default=None)  # type: int
    api_key = attr.ib(default=None)  # type: Text
    server_url = attr.ib(default=None)  # type: Text

    def request(self, method, url_resource, use_api_key=True, **kwargs):
        if url_resource is not None:
            # makes URL relative
            url_resource = url_resource.lstrip("/")
        url_resource = urljoin(self.server_url, url_resource)
        params = {}
        if use_api_key:
            params["apiKey"] = self.api_key
        params.update(kwargs.get("params", {}))
        headers = kwargs.get("headers", self.headers).copy()
        timeout_sec = kwargs.get("timeout", None)
        if timeout_sec is None:
            timeout_sec = datetime_utils.to_sec(self.timeout_ms)
        response = method(
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
        headers = kwargs.get("headers", self.headers).copy()
        headers["Eyes-Expect"] = "202+location"
        headers["Eyes-Date"] = datetime_utils.current_time_in_rfc1123()
        kwargs["headers"] = headers
        response = self.request(method, url_resource, **kwargs)
        return self._long_request_check_status(response)

    def _long_request_check_status(self, response):
        if response.status_code == requests.codes.ok:
            # request ends successful
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
                requests.delete,
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
        logger.debug("Still running... Retrying in {} ms".format(delay))

        datetime_utils.sleep(delay)
        response = self.request(
            requests.get,
            url,
            headers={"Eyes-Date": datetime_utils.current_time_in_rfc1123()},
        )
        if response.status_code != requests.codes.ok:
            return response
        return self._long_request_loop(url, delay)


def prepare_match_data(match_data):
    # type: (MatchWindowData) -> bytes
    screenshot64 = match_data.app_output.screenshot64
    if screenshot64:
        match_data.app_output.screenshot64 = None
        image = image_utils.image_from_base64(screenshot64)
        screenshot_bytes = image_utils.get_bytes(image)  # type: bytes
    else:
        screenshot_bytes = b""
    match_data_json = json_utils.to_json(match_data)
    logger.debug("MatchWindowData {}".format(match_data_json))
    match_data_json_bytes = match_data_json.encode("utf-8")  # type: bytes
    match_data_size_bytes = pack(">L", len(match_data_json_bytes))  # type: bytes
    body = match_data_size_bytes + match_data_json_bytes + screenshot_bytes
    return body


class ServerConnector(object):
    """
    Provides an API for communication with the Applitools server.
    """

    DEFAULT_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

    API_SESSIONS = "api/sessions"
    API_SESSIONS_RUNNING = API_SESSIONS + "/running/"
    RUNNING_DATA_PATH = API_SESSIONS + "/running/data"

    # Rendering Grid
    RENDER_INFO_PATH = API_SESSIONS + "/renderinfo"
    RESOURCES_SHA_256 = "/resources/sha256/"
    RENDER_STATUS = "/render-status"
    RENDER = "/render"

    _is_session_started = False

    def __init__(self):
        # type: () -> None
        """
        Ctor.

        :param server_url: The url of the Applitools server.
        """
        self._render_info = None  # type: Optional[RenderingInfo]
        self._com = _RequestCommunicator(headers=ServerConnector.DEFAULT_HEADERS)

    def update_config(self, conf):
        if conf.api_key is None:
            raise EyesError(
                "API key not set! Log in to https://applitools.com to obtain your"
                " API Key and use 'api_key' to set it."
            )
        self._com.server_url = conf.server_url
        self._com.api_key = conf.api_key
        self._com.timeout_ms = conf._timeout

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
        response = self._com.request(
            requests.post, url_resource=self.API_SESSIONS_RUNNING, data=data
        )
        running_session = json_utils.attr_from_response(response, RunningSession)
        running_session.is_new_session = response.status_code == requests.codes.created
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
            requests.delete,
            url_resource=urljoin(self.API_SESSIONS_RUNNING, running_session.id),
            params=params,
            headers=ServerConnector.DEFAULT_HEADERS,
        )

        test_results = json_utils.attr_from_response(response, TestResults)
        logger.debug("stop_session(): parsed response: {}".format(test_results))

        # mark that session isn't started
        self._is_session_started = False
        return test_results

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

        data = prepare_match_data(match_data)
        # Using the default headers, but modifying the "content type" to binary
        headers = ServerConnector.DEFAULT_HEADERS.copy()
        headers["Content-Type"] = "application/octet-stream"
        # TODO: allow to send images as base64
        response = self._com.long_request(
            requests.post,
            url_resource=urljoin(self.API_SESSIONS_RUNNING, running_session.id),
            data=data,
            headers=headers,
        )
        match_result = json_utils.attr_from_response(response, MatchResult)
        return match_result

    def post_dom_snapshot(self, dom_json):
        # type: (Text) -> Optional[Text]
        """
        Upload the DOM of the tested page.
        Return an URL of uploaded resource which should be posted to :py:   `AppOutput`.
        """
        logger.debug("post_dom_snapshot called.")

        if not self.is_session_started:
            raise EyesError("Session not started")

        headers = ServerConnector.DEFAULT_HEADERS.copy()
        headers["Content-Type"] = "application/octet-stream"
        dom_bytes = gzip_compress(dom_json.encode("utf-8"))

        response = self._com.request(
            requests.post,
            url_resource=urljoin(self.API_SESSIONS_RUNNING, "data"),
            data=dom_bytes,
            headers=headers,
        )
        dom_url = None
        if response.ok:
            dom_url = response.headers["Location"]
        return dom_url

    def render_info(self):
        # type: () -> Optional[RenderingInfo]
        logger.debug("render_info() called.")
        headers = ServerConnector.DEFAULT_HEADERS.copy()
        headers["Content-Type"] = "application/json"
        response = self._com.request(
            requests.get, self.RENDER_INFO_PATH, headers=headers
        )
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
            requests.post, url, use_api_key=False, headers=headers, data=data
        )
        if response.ok or response.status_code == requests.codes.not_found:
            return json_utils.attr_from_response(response, RunningRender)
        raise EyesError(
            "ServerConnector.render - unexpected status ({})\n\tcontent{}".format(
                response.status_code, response.content
            )
        )

    def render_put_resource(self, running_render, resource):
        # type: (RunningRender, VGResource) -> Text
        argument_guard.not_none(running_render)
        argument_guard.not_none(resource)
        if self._render_info is None:
            raise EyesError("render_info must be fetched first")

        content = resource.content
        argument_guard.not_none(content)
        logger.debug(
            "resource hash: {} url: {} render id: {}"
            "".format(resource.hash, resource.url, running_render.render_id)
        )
        headers = ServerConnector.DEFAULT_HEADERS.copy()
        headers["Content-Type"] = resource.content_type
        headers["X-Auth-Token"] = self._render_info.access_token

        url = urljoin(
            self._render_info.service_url, self.RESOURCES_SHA_256 + resource.hash
        )
        response = self._com.request(
            requests.put,
            url,
            use_api_key=False,
            headers=headers,
            data=content,
            params={"render-id": running_render.render_id},
        )
        logger.debug("ServerConnector.put_resource - request succeeded")
        if not response.ok:
            raise EyesError(
                "Error putting resource: {}, {}".format(
                    response.status_code, response.content
                )
            )
        return resource.hash

    @datetime_utils.retry()
    def download_resource(self, url):
        # type: (Text) -> Response
        logger.debug("Fetching {}...".format(url))
        headers = ServerConnector.DEFAULT_HEADERS.copy()
        headers["Accept-Encoding"] = "identity"

        timeout_sec = datetime_utils.to_sec(self._com.timeout_ms)
        response = requests.get(url, headers=headers, timeout=timeout_sec, verify=False)
        if response.status_code == requests.codes.not_acceptable:
            response = requests.get(url, timeout=timeout_sec, verify=False)
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
            requests.post,
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
