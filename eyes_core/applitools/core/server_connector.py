from __future__ import absolute_import

import os
import time
import typing as tp

import requests
from requests.packages import urllib3

from . import logger
from .test_results import TestResults
from .utils import general_utils
from .utils.compat import gzip_compress, urljoin  # type: ignore

if tp.TYPE_CHECKING:
    from .utils.custom_types import RunningSession, SessionStartInfo, Num

# Prints out all data sent/received through 'requests'
# import httplib
# httplib.HTTPConnection.debuglevel = 1

# Remove Unverified SSL warnings propagated by requests' internal urllib3 module
if hasattr(urllib3, "disable_warnings") and callable(urllib3.disable_warnings):
    urllib3.disable_warnings()

__all__ = ("ServerConnector",)


class _RequestsCommunicator(object):
    LONG_REQUEST_DELAY = 2  # seconds
    MAX_LONG_REQUEST_DELAY = 10  # seconds
    LONG_REQUEST_DELAY_MULTIPLICATIVE_INCREASE_FACTOR = 1.5

    endpoint_uri = None  # type: tp.Optional[tp.Text]
    api_key = None
    timeout = None

    def __init__(self, timeout, headers):
        # type: (int, dict) -> None
        self.timeout = timeout
        self.headers = headers.copy()

    def _request(self, method, url_resource, **kwargs):
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

    def _long_request(self, method, url_resource, **kwargs):
        headers = kwargs["headers"].copy()
        headers["Eyes-Expect"] = "202-accepted"
        for delay in self.request_delay():
            # Sending the current time of the request (in RFC 1123 format)
            headers["Eyes-Date"] = time.strftime(
                "%a, %d %b %Y %H:%M:%S GMT", time.gmtime()
            )
            kwargs["headers"] = headers
            response = self._request(method, url_resource, **kwargs)
            if response.status_code != 202:
                return response
            logger.debug("Still running... Retrying in {}s".format(delay))
        else:
            raise requests.Timeout("Couldn't process request")

    def post(self, url_resource=None, **kwargs):
        return self._request(requests.post, url_resource, **kwargs)

    def long_delete(self, url_resource=None, **kwargs):
        return self._long_request(requests.delete, url_resource, **kwargs)

    @staticmethod
    def request_delay(
        first_delay=LONG_REQUEST_DELAY,
        step_factor=LONG_REQUEST_DELAY_MULTIPLICATIVE_INCREASE_FACTOR,
        max_delay=MAX_LONG_REQUEST_DELAY,
    ):
        delay = _RequestsCommunicator.LONG_REQUEST_DELAY  # type: Num
        while True:
            yield delay
            time.sleep(first_delay)
            delay = delay * step_factor
            if delay > max_delay:
                raise StopIteration


class ServerConnector(object):
    """
    Provides an API for communication with the Applitools server.
    """

    DEFAULT_TIMEOUT = 60 * 5  # Seconds
    DEFAULT_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}
    DEFAULT_SERVER_URL = "https://eyesapi.applitools.com"
    API_SESSIONS_RUNNING = "/api/sessions/running/"

    def __init__(self, server_url):
        # type: (tp.Optional[tp.Text]) -> None
        """
        Ctor.

        :param server_url: The url of the Applitools server.
        """
        self._request = _RequestsCommunicator(
            timeout=ServerConnector.DEFAULT_TIMEOUT,
            headers=ServerConnector.DEFAULT_HEADERS,
        )
        self.server_url = server_url

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
        self._request.endpoint_uri = urljoin(
            self._server_url, ServerConnector.API_SESSIONS_RUNNING
        )

    @property
    def api_key(self):
        if self._request.api_key is None:
            # if api_key is None the error will be raised in EyesBase._open_base
            self._request.api_key = os.environ.get("APPLITOOLS_API_KEY", None)
        return self._request.api_key

    @api_key.setter
    def api_key(self, api_key):
        self._request.api_key = api_key

    @property
    def timeout(self):
        if self._request.timeout is None:
            self._request.timeout = self.DEFAULT_TIMEOUT
        return self._request.timeout

    @timeout.setter
    def timeout(self, timeout):
        self._request.timeout = timeout

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
        data = '{"startInfo": %s}' % (general_utils.to_json(session_start_info))
        response = self._request.post(data=data)
        parsed_response = response.json()
        return dict(
            session_id=parsed_response["id"],
            session_url=parsed_response["url"],
            is_new_session=(response.status_code == requests.codes.created),
        )

    def stop_session(self, running_session, is_aborted, save):
        # type: (RunningSession, bool, bool) -> TestResults
        """
        Stops a running session in the Eyes server.

        :param running_session: The session to stop.
        :param is_aborted: Whether the server should mark this session as aborted.
        :param save: Whether the session should be automatically saved if it is not aborted.
        :return: Test results of the stopped session.
        """
        logger.debug("Stop session called..")
        params = {"aborted": is_aborted, "updateBaseline": save, "apiKey": self.api_key}
        headers = ServerConnector.DEFAULT_HEADERS.copy()
        response = self._request.long_delete(
            url_resource=running_session["session_id"], params=params, headers=headers
        )
        pr = response.json()
        logger.debug("stop_session(): parsed response: {}".format(pr))
        return TestResults(
            pr["steps"],
            pr["matches"],
            pr["mismatches"],
            pr["missing"],
            pr["exactMatches"],
            pr["strictMatches"],
            pr["contentMatches"],
            pr["layoutMatches"],
            pr["noneMatches"],
            pr["status"],
        )

    def match_window(self, running_session, data):
        # type: (RunningSession, tp.Text) -> bool
        """
        Matches the current window to the immediate expected window in the Eyes server.
        Notice that a window might be matched later at the end of the test, even if it
        was not immediately matched in this call.

        :param running_session: The current session that is running.
        :param data: The data for the requests.post.
        :return: The parsed response.
        """
        # logger.debug("Data length: %d, data: %s" % (len(data), repr(data)))
        # Using the default headers, but modifying the "content type" to binary
        headers = ServerConnector.DEFAULT_HEADERS.copy()
        headers["Content-Type"] = "application/octet-stream"
        response = self._request.post(
            url_resource=running_session["session_id"], data=data, headers=headers
        )
        return response.json()["asExpected"]

    def post_dom_snapshot(self, dom_json):
        # type: (tp.Text) -> tp.Optional[tp.Text]
        """
        Upload the DOM of the tested page.
        Return an URL of uploaded resource which should be posted to :py:   `AppOutput`.
        """
        headers = ServerConnector.DEFAULT_HEADERS.copy()
        headers["Content-Type"] = "application/octet-stream"
        dom_bytes = gzip_compress(dom_json.encode("utf-8"))
        response = self._request.post(
            url_resource="running/data", data=dom_bytes, headers=headers
        )
        dom_url = None
        if response.ok:
            dom_url = response.headers["Location"]
        return dom_url
