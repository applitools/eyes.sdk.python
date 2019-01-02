from __future__ import absolute_import

import abc
import os
import typing as tp

from . import logger
from .utils import ABC
from .match import ImageMatchSettings
from .metadata import BatchInfo
from .agent_connector import AgentConnector
from .errors import EyesError, NewTestError, DiffsFoundError, TestFailedError
from .match_window_task import MatchWindowTask
from .test_results import TestResults, TestResultsStatus

if tp.TYPE_CHECKING:
    from .utils.custom_types import (ViewPort, UserInputs, AppEnvironment, MatchResult,
                                     RunningSession, SessionStartInfo, RegionOrElement)
    from .capture import EyesScreenshot

__all__ = ('FailureReports', 'EyesBase')


class FailureReports(object):
    """
    Failures are either reported immediately when they are detected, or when the test is closed.
    """
    IMMEDIATE = "Immediate"
    ON_CLOSE = "OnClose"


class EyesBase(ABC):
    _DEFAULT_MATCH_TIMEOUT = 2000  # Milliseconds
    _DEFAULT_WAIT_BEFORE_SCREENSHOTS = 100  # ms
    DEFAULT_EYES_SERVER = 'https://eyessdk.applitools.com'

    def __init__(self, server_url=DEFAULT_EYES_SERVER):
        # type: (tp.Text) -> None
        """
        Creates a new (possibly disabled) Eyes instance that interacts with the Eyes server.

        :param server_url: The URL of the Eyes server
        """
        self._agent_connector = AgentConnector(server_url)  # type: AgentConnector
        self._should_get_title = False  # type: bool
        self._is_open = False  # type: bool
        self._app_name = None  # type: tp.Optional[tp.Text]
        self._running_session = None  # type: tp.Optional[RunningSession]
        self._match_timeout = EyesBase._DEFAULT_MATCH_TIMEOUT  # type: int
        self._last_screenshot = None  # type: tp.Optional[EyesScreenshot]
        self._should_match_once_on_timeout = False  # type: bool
        self._start_info = None  # type: tp.Optional[SessionStartInfo]
        self._test_name = None  # type: tp.Optional[tp.Text]
        self._user_inputs = []  # type: UserInputs
        self._region_to_check = None  # type: tp.Optional[RegionOrElement]
        self._viewport_size = None  # type: ViewPort

        # key-value pairs to be associated with the test. Can be used for filtering later.
        self._properties = []  # type: tp.List

        # Disables Applitools Eyes and uses the webdriver directly.
        self.is_disabled = False  # type: bool

        # An optional string identifying the current library using the SDK.
        self.agent_id = None  # type: tp.Optional[tp.Text]

        # Should the test report mismatches immediately or when it is finished. See FailureReports.
        self.failure_reports = FailureReports.ON_CLOSE  # type: tp.Text

        # The default match settings for the session. See ImageMatchSettings.
        self.default_match_settings = ImageMatchSettings()  # type: ImageMatchSettings

        # The batch to which the tests belong to. See BatchInfo. None means no batch.
        self.batch = None  # type: tp.Optional[BatchInfo]

        # A string identifying the OS running the AUT. Use this to override Eyes automatic inference.
        self.host_os = None  # type: tp.Optional[tp.Text]

        # A string identifying the app running the AUT. Use this to override Eyes automatic inference.
        self.host_app = None  # type: tp.Optional[tp.Text]

        # A string that, if specified, determines the baseline to compare with and disables automatic baseline
        # inference.
        self.baseline_branch_name = None  # type: tp.Optional[tp.Text]

        # A boolean denoting whether new tests should be automatically accepted.
        self.save_new_tests = True  # type: bool

        # Whether failed tests should be automatically saved with all new output accepted.
        self.save_failed_tests = False  # type: bool

        # A string identifying the branch in which tests are run.
        self.branch_name = None  # type: tp.Optional[tp.Text]

        # A string identifying the parent branch of the branch set by "branch_name".
        self.parent_branch_name = None  # type: tp.Optional[tp.Text]

        # If true, Eyes will treat new tests the same as failed tests.
        self.fail_on_new_test = False  # type: bool

        # The number of milliseconds to wait before each time a screenshot is taken.
        self.wait_before_screenshots = EyesBase._DEFAULT_WAIT_BEFORE_SCREENSHOTS  # type: int

        # If true, we will send full DOM to the server for analyzing
        self.send_dom = False

    @property
    @abc.abstractmethod
    def _title(self):
        # type: () -> tp.Text
        """
        Returns the title of the window of the AUT, or empty string if the title is not available.
        """

    @abc.abstractmethod
    def get_screenshot(self, **kwargs):
        pass

    @abc.abstractmethod
    def _get_viewport_size(self):
        # type: () -> ViewPort
        """
        :return: The viewport size of the AUT.
        """

    @abc.abstractmethod
    def _set_viewport_size(self, size):
        # type: (ViewPort) -> None
        """
        :param size: The required viewport size.
        """

    @abc.abstractmethod
    def _assign_viewport_size(self):
        # type: () -> None
        """
        Assign the viewport size we need to be in the default content frame.
        """

    @abc.abstractmethod
    def _get_environment(self):
        # type: () -> AppEnvironment
        """
        Application environment is the environment (e.g., the host OS) which runs the application under test.

        :return: The current application environment.
        """

    @abc.abstractmethod
    def _inferred_environment(self):
        pass

    @property
    def _seconds_to_wait_screenshot(self):
        return self.wait_before_screenshots / 1000.0

    @property
    def match_level(self):
        # type: () -> tp.Text
        """
        Gets the default match level for the entire session. See ImageMatchSettings.
        """
        return self.default_match_settings.match_level

    @match_level.setter
    def match_level(self, match_level):
        # type: (tp.Text) -> None
        """
        Sets the default match level for the entire session. See ImageMatchSettings.

        :param match_level: The match level to set. Should be one of the values defined by MatchLevel
        """
        self.default_match_settings.match_level = match_level

    @property
    def match_timeout(self):
        # type: () -> int
        """
        Gets the default timeout for check_XXXX operations. (milliseconds)

        :return: The match timeout (milliseconds)
        """
        return self._match_timeout

    @match_timeout.setter
    def match_timeout(self, match_timeout):
        # type: (int) -> None
        """
        Sets the default timeout for check_XXXX operations. (milliseconds)
        """
        if 0 < match_timeout < MatchWindowTask.MINIMUM_MATCH_TIMEOUT:
            raise ValueError("Match timeout must be at least 60ms.")
        self._match_timeout = match_timeout

    @property
    def api_key(self):
        # type: () -> tp.Text
        """
        Gets the Api key used for authenticating the user with Eyes.

        :return: The Api key used for authenticating the user with Eyes.
        """
        return self._agent_connector.api_key

    @api_key.setter
    def api_key(self, api_key):
        # type: (tp.Text) -> None
        """
        Sets the api key used for authenticating the user with Eyes.

        :param api_key: The api key used for authenticating the user with Eyes.
        """
        self._agent_connector.api_key = api_key  # type: ignore

    @property
    def server_url(self):
        # type: () -> tp.Text
        """
        Gets the URL of the Eyes server.

        :return: The URL of the Eyes server, or None to use the default server.
        """
        return self._agent_connector.server_url

    @server_url.setter
    def server_url(self, server_url):
        # type: (tp.Text) -> None
        """
        Sets the URL of the Eyes server.

        :param server_url: The URL of the Eyes server, or None to use the default server.
        :return: None
        """
        if server_url is None:
            self._agent_connector.server_url = EyesBase.DEFAULT_EYES_SERVER
        else:
            self._agent_connector.server_url = server_url

    @property
    @abc.abstractmethod
    def base_agent_id(self):
        # type: () -> tp.Text
        """
        Must return version of SDK. (e.g. Selenium, Images) in next format:
            "eyes.{package}.python/{lib_version}"
        """

    @property
    def full_agent_id(self):
        """
        Gets the agent id, which identifies the current library using the SDK.

        :return: The agent id.
        """
        if self.agent_id is None:
            return self.base_agent_id
        return "{0} [{1}]".format(self.agent_id, self.base_agent_id)

    def add_property(self, name, value):
        # type: (tp.Text, tp.Text) -> None
        """
        Associates a key/value pair with the test. This can be used later for filtering.
        :param name: (string) The property name.
        :param value: (string) The property value
        """
        self._properties.append({'name': name, 'value': value})

    def is_open(self):
        # type: () -> bool
        """
        Returns whether the session is currently running.
        """
        return self._is_open

    def close(self, raise_ex=True):
        # type: (bool) -> tp.Optional[TestResults]
        """
        Ends the test.

        :param raise_ex: If true, an exception will be raised for failed/new tests.
        :return: The test results.
        """
        if self.is_disabled:
            logger.debug('close(): ignored (disabled)')
            return None
        try:
            logger.debug('close({})'.format(raise_ex))
            if not self._is_open:
                raise ValueError("Eyes not open")

            self._is_open = False

            self._reset_last_screenshot()

            # If there's no running session, we simply return the default test results.
            if not self._running_session:
                logger.debug('close(): Server session was not started')
                logger.info('close(): --- Empty test ended.')
                return TestResults()

            is_new_session = self._running_session['is_new_session']
            results_url = self._running_session['session_url']

            logger.info("close(): Ending server session...")
            should_save = (is_new_session and self.save_new_tests) or \
                          ((not is_new_session) and self.save_failed_tests)
            logger.debug("close(): automatically save session? %s" % should_save)
            results = self._agent_connector.stop_session(self._running_session, False, should_save)
            results.is_new = is_new_session
            results.url = results_url
            logger.info("close(): %s" % results)

            if results.status == TestResultsStatus.Unresolved:
                if results.is_new:
                    instructions = "Please approve the new baseline at " + results_url
                    logger.info("--- New test ended. " + instructions)
                    if raise_ex:
                        message = "'%s' of '%s'. %s" % (self._start_info['scenarioIdOrName'],
                                                        self._start_info['appIdOrName'],
                                                        instructions)
                        raise NewTestError(message, results)
                else:
                    logger.info("--- Failed test ended. See details at {}".format(results_url))
                    if raise_ex:
                        raise DiffsFoundError("Test '{}' of '{}' detected differences! See details at: {}".format(
                            self._start_info['scenarioIdOrName'],
                            self._start_info['appIdOrName'],
                            results_url), results)
            elif results.status == TestResultsStatus.Failed:
                logger.info("--- Failed test ended. See details at {}".format(results_url))
                if raise_ex:
                    raise TestFailedError("Test '{}' of '{}'. See details at: {}".format(
                        self._start_info['scenarioIdOrName'],
                        self._start_info['appIdOrName'],
                        results_url), results)
            # Test passed
            logger.info("--- Test passed. See details at {}".format(results_url))

            return results
        finally:
            self._running_session = None
            logger.close()

    def abort_if_not_closed(self):
        # type: () -> None
        """
        If a test is running, aborts it. Otherwise, does nothing.
        """
        if self.is_disabled:
            logger.debug('abort_if_not_closed(): ignored (disabled)')
            return
        try:
            self._reset_last_screenshot()

            if self._running_session:
                logger.debug('abort_if_not_closed(): Aborting session...')
                try:
                    self._agent_connector.stop_session(self._running_session, True, False)
                    logger.info('--- Test aborted.')
                except EyesError as e:
                    logger.info("Failed to abort server session: %s " % e)
                    pass
                finally:
                    self._running_session = None
        finally:
            logger.close()

    def _before_open(self):
        pass

    def _after_open(self):
        pass

    def open_base(self, app_name, test_name, viewport_size=None):
        # type: (tp.Text, tp.Text, tp.Optional[ViewPort]) -> None
        """
        Starts a test.

        :param app_name: The name of the application under test.
        :param test_name: The test name.
        :param viewport_size: The client's viewport size (i.e., the visible part of the document's body) or None to
                                allow any viewport size.
        :return: An updated web driver
        :raise EyesError: If the session was already open.
        """
        logger.open_()
        if self.is_disabled:
            logger.debug('open_base(): ignored (disabled)')
            return

        if self.api_key is None:
            try:
                self.api_key = os.environ['APPLITOOLS_API_KEY']
            except KeyError:
                raise EyesError("API key not set! Log in to https://applitools.com to obtain your"
                                " API Key and use 'api_key' to set it.")

        logger.info("open(%s, %s, %s, %s)" % (app_name, test_name, viewport_size, self.failure_reports))

        if self.is_open():
            self.abort_if_not_closed()
            raise EyesError('a test is already running')

        self._before_open()

        self._app_name = app_name
        self._test_name = test_name
        self._viewport_size = viewport_size

        if viewport_size is not None:
            self._ensure_running_session()

        self._is_open = True

        self._after_open()

    def _create_start_info(self):
        # type: () -> None
        app_env = self._get_environment()
        self._start_info = {'agentId':              self.full_agent_id, 'appIdOrName': self._app_name,
                            'scenarioIdOrName':     self._test_name, 'batchInfo': self.batch,
                            'envName':              self.baseline_branch_name, 'environment': app_env,
                            'defaultMatchSettings': self.default_match_settings, 'verId': None,
                            'branchName':           self.branch_name, 'parentBranchName': self.parent_branch_name,
                            'properties':           self._properties}

    def _start_session(self):
        # type: () -> None
        logger.debug("_start_session()")
        self._assign_viewport_size()

        # initialization of Eyes parameters if empty from ENV variables
        if not self.branch_name:
            self.branch_name = os.environ.get('APPLITOOLS_BRANCH', None)
        if not self.baseline_branch_name:
            self.baseline_branch_name = os.environ.get('APPLITOOLS_BASELINE_BRANCH', None)
        if not self.parent_branch_name:
            self.parent_branch_name = os.environ.get('APPLITOOLS_PARENT_BRANCH', None)
        if not self.batch:
            self.batch = BatchInfo()

        self._create_start_info()
        # Actually start the session.
        self._running_session = self._agent_connector.start_session(self._start_info)
        self._should_match_once_on_timeout = self._running_session['is_new_session']

    def _reset_last_screenshot(self):
        # type: () -> None
        self._last_screenshot = None
        self._user_inputs = []  # type: UserInputs

    def _ensure_running_session(self):
        if self._running_session:
            logger.debug('Session already running.')
            return
        self._start_session()
        self._match_window_task = MatchWindowTask(self, self._agent_connector,
                                                  self._running_session,
                                                  self.match_timeout)

    def _before_match_window(self):
        """
        Allow to add custom behavior after receiving response from the server
        """

    def _after_match_window(self):
        """
        Allow to add custom behavior before sending data to the server
        """

    def _check_window_base(self, tag=None, match_timeout=-1, target=None):
        if self.is_disabled:
            logger.info("check_window(%s): ignored (disabled)" % tag)
            # TODO: create propper MatchResult class
            result = {"as_expected": True, "screenshot": None}
            return result

        self._ensure_running_session()

        self._before_match_window()

        # TODO: implement MatchWIndow_ analog
        result = self._match_window_task.match_window(retry_timeout=match_timeout,
                                                      tag=tag,
                                                      user_inputs=self._user_inputs,
                                                      default_match_settings=self.default_match_settings,
                                                      target=target,
                                                      run_once_after_wait=self._should_match_once_on_timeout)
        self._after_match_window()
        self._handle_match_result(result, tag)
        return result

    def _handle_match_result(self, result, tag):
        # type: (MatchResult, tp.Text) -> None
        self._last_screenshot = result['screenshot']
        as_expected = result['as_expected']
        self._user_inputs = []
        if not as_expected:
            self._should_match_once_on_timeout = True
            if self._running_session and not self._running_session['is_new_session']:
                logger.info("Window mismatch %s" % tag)
                if self.failure_reports == FailureReports.IMMEDIATE:
                    raise TestFailedError("Mismatch found in '%s' of '%s'" %
                                          (self._start_info['scenarioIdOrName'],
                                           self._start_info['appIdOrName']))

    @abc.abstractmethod
    def _try_capture_dom(self):
        # type: () -> tp.Text
        """
        Returns the string with DOM of the current page in the prepared format or empty string
        """

    def _try_post_dom_snapshot(self, dom_json):
        # type: (tp.Text) -> tp.Optional[tp.Text]
        """
        In case DOM data is valid uploads it to the server and return URL where it stored.
        """
        if dom_json is None:
            return None
        try:
            return self._agent_connector.post_dom_snapshot(dom_json)
        except Exception as e:
            logger.warning("Couldn't send DOM Json. Passing...\n Got next error: {}".format(e))
            return None
