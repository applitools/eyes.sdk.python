from __future__ import absolute_import

import os
import time
import typing as tp
from struct import pack
from typing import Any, Optional

import requests
from requests.packages import urllib3  # noqa

from applitools.common import RunningSession, logger
from applitools.common.errors import EyesError
from applitools.common.match import MatchResult
from applitools.common.match_window_data import MatchWindowData
from applitools.common.metadata import SessionStartInfo
from applitools.common.test_results import TestResults
from applitools.common.utils import general_utils, gzip_compress, image_utils, urljoin
from applitools.common.utils.general_utils import json_response_to_attrs_class
from applitools.common.visualgridclient.model import (
    RenderingInfo,
    RenderRequest,
    RunningRender,
)

if tp.TYPE_CHECKING:
    from applitools.common.utils.custom_types import Num

# Prints out all data sent/received through 'requests'
# import httplib
# httplib.HTTPConnection.debuglevel = 1

# Remove Unverified SSL warnings propagated by requests' internal urllib3 module
if hasattr(urllib3, "disable_warnings") and callable(urllib3.disable_warnings):
    urllib3.disable_warnings()

__all__ = ("ServerConnector",)


class _RequestCommunicator(object):
    LONG_REQUEST_DELAY = 2  # seconds
    MAX_LONG_REQUEST_DELAY = 10  # seconds
    LONG_REQUEST_DELAY_MULTIPLICATIVE_INCREASE_FACTOR = 1.5

    def __init__(self, timeout, headers, api_key, endpoint_uri):
        # type: (int, tp.Dict, tp.Text, tp.Text) -> None
        self.timeout = timeout
        self.headers = headers.copy()
        self.api_key = api_key
        self.endpoint_uri = endpoint_uri

    def request(self, method, url_resource, **kwargs):
        if url_resource is not None:
            # makes URL relative
            url_resource = url_resource.lstrip("/")
        url_resource = urljoin(self.endpoint_uri, url_resource)

        params = dict(apiKey=self.api_key)
        params.update(kwargs.get("params", {}))
        headers = kwargs.get("headers", self.headers)
        timeout = kwargs.get("timeout", self.timeout)

        response = method(
            url_resource,
            data=kwargs.get("data", None),
            verify=False,
            params=params,
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()
        return response

    def long_request(self, method, url_resource, **kwargs):
        headers = kwargs["headers"].copy()
        headers["Eyes-Expect"] = "202-accepted"
        for delay in self.request_delay():
            # Sending the current time of the request (in RFC 1123 format)
            headers["Eyes-Date"] = time.strftime(
                "%a, %d %b %Y %H:%M:%S GMT", time.gmtime()
            )
            kwargs["headers"] = headers
            response = self.request(method, url_resource, **kwargs)
            if response.status_code != 202:
                return response
            logger.debug("Still running... Retrying in {}s".format(delay))
        else:
            raise requests.Timeout("Couldn't process request")

    @staticmethod
    def request_delay(
        first_delay=LONG_REQUEST_DELAY,
        step_factor=LONG_REQUEST_DELAY_MULTIPLICATIVE_INCREASE_FACTOR,
        max_delay=MAX_LONG_REQUEST_DELAY,
    ):
        delay = _RequestCommunicator.LONG_REQUEST_DELAY  # type: Num
        while True:
            yield delay
            time.sleep(first_delay)
            delay = delay * step_factor
            if delay > max_delay:
                raise StopIteration


class _Request(object):
    """
    Class for fetching data from
    """

    def __init__(self, com):
        self._com = com

    def post(self, url_resource=None, long_query=False, **kwargs):
        # type: (str, bool, **Any) -> requests.Response
        func = self._com.long_request if long_query else self._com.request
        return func(requests.post, url_resource, **kwargs)

    def get(self, url_resource=None, long_query=False, **kwargs):
        # type: (str, bool, **Any) -> requests.Response
        func = self._com.long_request if long_query else self._com.request
        return func(requests.get, url_resource, **kwargs)

    def delete(self, url_resource=None, long_query=False, **kwargs):
        # type: (str, bool, **Any) -> requests.Response
        func = self._com.long_request if long_query else self._com.request
        return func(requests.delete, url_resource, **kwargs)


def create_request_factory(headers, server_url):
    class RequestFactory(object):
        def __init__(self):
            self._com = None

        def create(self, api_key, server_url, timeout):
            # server_url could be updated
            if self._com:
                return self._com

            self._com = _RequestCommunicator(
                timeout, headers, api_key, endpoint_uri=server_url
            )
            return _Request(self._com)

    return RequestFactory()


class ServerConnector(object):
    """
    Provides an API for communication with the Applitools server.
    """

    DEFAULT_TIMEOUT = 60 * 5  # Seconds
    DEFAULT_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}
    DEFAULT_SERVER_URL = "https://eyesapi.applitools.com"

    API_SESSIONS = "api/sessions"
    API_SESSIONS_RUNNING = API_SESSIONS + "/running/"
    RUNNING_DATA_PATH = API_SESSIONS + "/running/data"

    # Rendering Grid
    RENDER_INFO_PATH = API_SESSIONS + "/renderinfo"
    RESOURCES_SHA_256 = "/resources/sha256/"
    RENDER_STATUS = "/render-status"
    RENDER = "/render"

    _api_key = None
    _timeout = None
    _server_url = None  # type: tp.Optional[tp.Text]
    _request = None  # type: tp.Optional[_Request]

    def __init__(self, server_url):
        # type: (tp.Optional[tp.Text]) -> None
        """
        Ctor.

        :param server_url: The url of the Applitools server.
        """
        self.server_url = server_url
        self._render_info = None  # type: Optional[RenderingInfo]
        self._request_factory = create_request_factory(
            headers=ServerConnector.DEFAULT_HEADERS, server_url=server_url
        )

    @property
    def server_url(self):
        # type: () -> tp.Text
        return self._server_url

    @server_url.setter
    def server_url(self, server_url):
        # type: (tp.Text) -> None
        if server_url is None:
            self._server_url = self.DEFAULT_SERVER_URL
        else:
            self._server_url = server_url

    @property
    def api_key(self):
        if self._api_key is None:
            # if api_key is None the error will be raised in EyesBase.open_base
            self._api_key = os.environ.get("APPLITOOLS_API_KEY", None)
        return self._api_key

    @api_key.setter
    def api_key(self, api_key):
        self._api_key = api_key

    @property
    def timeout(self):
        if self._timeout is None:
            self._timeout = self.DEFAULT_TIMEOUT
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        self._timeout = timeout

    @property
    def is_session_started(self):
        return self._request is not None

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
        data = session_start_info.to_json()

        self._request = self._request_factory.create(
            server_url=self.server_url, api_key=self.api_key, timeout=self.timeout
        )
        response = self._request.post(url_resource=self.API_SESSIONS_RUNNING, data=data)
        running_session = json_response_to_attrs_class(response.json(), RunningSession)
        running_session.is_new_session = response.status_code == requests.codes.created
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
        response = self._request.delete(
            url_resource=urljoin(self.API_SESSIONS_RUNNING, running_session.id),
            long_query=True,
            params=params,
            headers=ServerConnector.DEFAULT_HEADERS,
        )

        test_results = json_response_to_attrs_class(response.json(), TestResults)
        logger.debug("stop_session(): parsed response: {}".format(test_results))

        # mark that session isn't started
        self._request = None
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
        logger.debug("_match_window called.")

        # logger.debug("Data length: %d, data: %s" % (len(data), repr(data)))
        if not self.is_session_started:
            raise EyesError("Session not started")

        data = self._prepare_data(match_data)
        # Using the default headers, but modifying the "content type" to binary
        headers = ServerConnector.DEFAULT_HEADERS.copy()
        headers["Content-Type"] = "application/octet-stream"
        # TODO: allow to send images as base64
        response = self._request.post(
            url_resource=urljoin(self.API_SESSIONS_RUNNING, running_session.id),
            data=data,
            headers=headers,
        )
        match_result = json_response_to_attrs_class(response.json(), MatchResult)
        return match_result

    def post_dom_snapshot(self, dom_json):
        # type: (tp.Text) -> tp.Optional[tp.Text]
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

        response = self._request.post(
            url_resource=urljoin(self.API_SESSIONS_RUNNING, "data"),
            data=dom_bytes,
            headers=headers,
        )
        dom_url = None
        if response.ok:
            dom_url = response.headers["Location"]
        return dom_url

    def get_render_info(self):
        # type: () -> tp.Optional[RenderingInfo]
        logger.debug("get_render_info called.")

        if not self.is_session_started:
            raise EyesError("Session not started")

        headers = ServerConnector.DEFAULT_HEADERS.copy()
        headers["Content-Type"] = "application/json"
        response = self._request.get(self.RENDER_INFO_PATH, headers=headers)

        if not response.ok:
            return None

        self._render_info = json_response_to_attrs_class(response.json(), RenderingInfo)
        return self._render_info

    def render(self, *render_requests):
        # type: (*RenderRequest) -> tp.List[RunningRender]
        logger.debug("render called with {}".format(render_requests))
        if self._render_info is None:
            raise RuntimeError("get_render_info must be called first")

        url = urljoin(self._render_info.service_url, self.RENDER)
        # if len(render_requests) > 1:
        headers = ServerConnector.DEFAULT_HEADERS.copy()
        headers["Content-Type"] = "application/json"
        headers["X-Auth-Token"] = self._render_info.access_token

        response = self._request.post(
            url, headers=headers, params={"render-id": render_requests}
        )
        if response.ok or response.status_code == 404:
            d = response.json()
            return d
        raise EyesError(
            "ServerConnector.render - unexpected status ({})".format(
                response.status_code
            )
        )

    def render_check_resource(self, running_render, check_resource):
        pass

    def render_put_resource(self, running_render, resource, listener):
        pass

    def render_status(self, running_render):
        pass

    @staticmethod
    def _prepare_data(match_data):
        # type: (MatchWindowData) -> bytes
        screenshot64 = match_data.app_output.screenshot64
        match_data.app_output.screenshot64 = None
        image = image_utils.image_from_base64(screenshot64)
        screenshot_bytes = image_utils.get_bytes(image)  # type: bytes

        match_data_json_bytes = general_utils.to_json(match_data).encode(
            "utf-8"
        )  # type: bytes
        match_data_size_bytes = pack(">L", len(match_data_json_bytes))  # type: bytes
        body = match_data_size_bytes + match_data_json_bytes + screenshot_bytes
        return body
