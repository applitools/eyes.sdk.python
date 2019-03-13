from __future__ import absolute_import

import abc
import typing as tp
from typing import Optional, Text

from applitools.common import (
    BatchInfo,
    Configuration,
    RectangleSize,
    Region,
    RunningSession,
    logger,
)
from applitools.common.app_output import AppOutput
from applitools.common.errors import (
    DiffsFoundError,
    EyesError,
    NewTestError,
    TestFailedError,
)
from applitools.common.match import ImageMatchSettings, MatchLevel, MatchResult
from applitools.common.metadata import AppEnvironment, SessionStartInfo
from applitools.common.server import FailureReports, SessionType
from applitools.common.test_results import TestResults
from applitools.common.utils import ABC, argument_guard
from applitools.core.capture import AppOutputProvider, AppOutputWithScreenshot
from applitools.core.cut import NullCutProvider
from applitools.core.debug import (
    FileDebugScreenshotProvider,
    NullDebugScreenshotProvider,
)

from .fluent import CheckSettings
from .match_window_task import MatchWindowTask
from .positioning import InvalidPositionProvider, PositionProvider, RegionProvider
from .scaling import FixedScaleProvider, NullScaleProvider, ScaleProvider
from .server_connector import ServerConnector

if tp.TYPE_CHECKING:
    from applitools.common.utils.custom_types import (
        ViewPort,
        UserInputs,
        RegionOrElement,
    )
    from applitools.common.capture import EyesScreenshot

__all__ = ("EyesBase",)


class EyesBaseAbstract(ABC):
    @abc.abstractmethod
    def _try_capture_dom(self):
        # type: () -> tp.Text
        """
        Returns the string with DOM of the current page in the prepared format or empty string
        """

    @property
    @abc.abstractmethod
    def base_agent_id(self):
        # type: () -> tp.Text
        """
        Must return version of SDK. (e.g. Selenium, Images) in next format:
            "eyes.{package}.python/{lib_version}"
        """

    @abc.abstractmethod
    def get_screenshot(self, **kwargs):
        # type: (...) -> EyesScreenshot
        pass

    @abc.abstractmethod
    def get_viewport_size_static(self):
        # type: () -> ViewPort
        """
        :return: The viewport size of the AUT.
        """

    @abc.abstractmethod
    def set_viewport_size_static(self, size):
        # type: (ViewPort) -> None
        """
        :param size: The required viewport size.
        """

    @property
    @abc.abstractmethod
    def _title(self):
        # type: () -> tp.Text
        """
        Returns the title of the window of the AUT, or empty string
         if the title is not available.
        """

    @property
    @abc.abstractmethod
    def _environment(self):
        # type: () -> AppEnvironment
        """
        Application environment is the environment (e.g., the host OS)
        which runs the application under test.

        :return: The current application environment.
        """

    @abc.abstractmethod
    def _get_viewport_size(self):
        # type: () -> RectangleSize
        """

        :return:
        """

    @abc.abstractmethod
    def _set_viewport_size(self, size):
        """

        """

    @property
    @abc.abstractmethod
    def _inferred_environment(self):
        pass


class EyesBase(EyesBaseAbstract):
    _config = None  # type: tp.Optional[Configuration]
    _host_os = None  # type: tp.Optional[tp.Text]
    _host_app = None  # type: tp.Optional[tp.Text]
    _running_session = None  # type: tp.Optional[RunningSession]
    _session_start_info = None  # type: tp.Optional[SessionStartInfo]
    _region_to_check = None  # type: tp.Optional[RegionOrElement]
    _last_screenshot = None  # type: tp.Optional[EyesScreenshot]
    _viewport_size = None  # type: ViewPort
    _scale_provider = None  # type: tp.Optional[ScaleProvider]
    _dom_url = None  # type: Optional[Text]
    _position_provider = None  # type: Optional[PositionProvider]
    _is_viewport_size_set = False

    # TODO: make it run with no effect to other pices of code
    # def set_explicit_viewport_size(self, size):
    #     """
    #     Define the viewport size as {@code size} without doing any actual action on the
    #
    #     :param size: The size of the viewport.
    #     """
    #     if not size:
    #         self.viewport_size = None
    #         self._is_viewport_size_set = False
    #         return None
    #     logger.info("Viewport size explicitly set to {}".format(size))
    #     self.viewport_size = RectangleSize(size["width"], size["height"])
    #     self._is_viewport_size_set = True

    def __init__(self, server_url=None):
        # type: (tp.Text) -> None
        """
        Creates a new (possibly disabled) Eyes instance that
        interacts with the Eyes server.

        :param server_url: The URL of the Eyes server
        """
        self._render = False
        self._server_connector = ServerConnector(server_url)  # type: ServerConnector
        self._should_get_title = False  # type: bool
        self._is_open = False  # type: bool
        self._should_match_once_on_timeout = False  # type: bool
        self._user_inputs = []  # type: UserInputs
        self._stitch_content = False  # type: bool
        self._debug_screenshot_provider = NullDebugScreenshotProvider()
        self._cut_provider = NullCutProvider()
        # self._is_viewport_size_set = False  # type: bool

        self._ensure_configuration()

        # Should the test report mismatches immediately or when it is finished.
        self.failure_reports = FailureReports.ON_CLOSE  # type: tp.Text
        # The default match settings for the session. See ImageMatchSettings.
        self.default_match_settings = ImageMatchSettings()  # type: ImageMatchSettings

    @property
    def is_debug_screenshot_provided(self):
        # type: () -> bool
        """True if screenshots saving enabled."""
        return isinstance(self._debug_screenshot_provider, FileDebugScreenshotProvider)

    def set_debug_screenshot_provider_for_saving(self, save=True):
        prev = self._debug_screenshot_provider
        if save:
            self._debug_screenshot_provider = FileDebugScreenshotProvider(
                prev.prefix, prev.path
            )
        else:
            self._debug_screenshot_provider = NullDebugScreenshotProvider()

    @property
    def viewport_size(self):
        return self._config.viewport_size

    @viewport_size.setter
    def viewport_size(self, size):
        self._config.viewport_size = size

    @property
    def stitching_overlap(self):
        return self._config.stitching_overlap

    @stitching_overlap.setter
    def stitching_overlap(self, value):
        self._config.stitching_overlap = value

    @property
    def agent_id(self):
        # type: () -> tp.Optional[tp.Text]
        return self._config.agent_id

    @agent_id.setter
    def agent_id(self, value):
        # type: (tp.Optional[tp.Text]) -> None
        """
        Sets the user given agent id of the SDK. {@code null} is referred to
          as no id.

        :param value: The agent ID to set
        """
        logger.debug("Agent ID: {}".format(value))
        if value.strip():
            self._config.agent_id = value.strip()

    @property
    def host_os(self):
        # type: () -> tp.Optional[tp.Text]
        return self._config.host_os

    @host_os.setter
    def host_os(self, value):
        # type: (tp.Optional[tp.Text]) -> None
        """
        :param value: The host OS running the AUT.
        """
        logger.debug("Host OS: {}".format(value))
        if value.strip():
            self._config.host_os = value.strip()

    @property
    def host_app(self):
        # type: () -> tp.Optional[tp.Text]
        return self._config.host_os

    @host_app.setter
    def host_app(self, value):
        # type: (tp.Optional[tp.Text]) -> None
        """
        :param value: The application running the AUT (e.g., Chrome).
        """
        logger.debug("Host OS: {}".format(value))
        if value.strip():
            self._config.host_app = value.strip()

    @property
    def baseline_name(self):
        logger.deprecation("use `baseline_env_name` instead")
        return self._config.baseline_env_name

    @baseline_name.setter
    def baseline_name(self, value):
        logger.deprecation("use `baseline_env_name` instead")
        self._config.baseline_env_name = value

    @property
    def baseline_env_name(self):
        return self._config.baseline_env_name

    @baseline_env_name.setter
    def baseline_env_name(self, value):
        logger.debug("Baseline environment name: {}".format(value))
        if value.strip():
            self._config.baseline_env_name = value

    @property
    def env_name(self):
        return self._config.environment_name

    @env_name.setter
    def env_name(self, value):
        logger.debug("Environment name: {}".format(value))
        if value.strip():
            self._config.environment_name = value

    @property
    def send_dom(self):
        return self._config.send_dom

    @send_dom.setter
    def send_dom(self, send):
        # type: (bool) -> None
        self._config.send_dom = send

    @property
    def use_dom(self):
        return self._config.use_dom

    @use_dom.setter
    def use_dom(self, send):
        # type: (bool) -> None
        self._config.use_dom = send

    @property
    def enable_patterns(self):
        return self._config.enable_patterns

    @enable_patterns.setter
    def enable_patterns(self, enable):
        # type: (bool) -> None
        self._config.enable_patterns = enable

    @property
    def match_level(self):
        # type: () -> tp.Text
        """
        Gets the default match level for the entire session. See ImageMatchSettings.
        """
        return self.default_match_settings.match_level

    @match_level.setter
    def match_level(self, match_level):
        # type: (MatchLevel) -> None
        """
        Sets the default match level for the entire session. See ImageMatchSettings.

        :param match_level: The match level to set. Should be one of
                            the values defined by MatchLevel
        """
        self.default_match_settings.match_level = match_level

    @property
    def match_timeout(self):
        # type: () -> int
        """
        Gets the default timeout for check_XXXX operations. (milliseconds)

        :return: The match timeout (milliseconds)
        """
        return self._config.match_timeout

    @match_timeout.setter
    def match_timeout(self, match_timeout):
        # type: (int) -> None
        """
        Sets the default timeout for check_XXXX operations. (milliseconds)
        """
        if 0 < match_timeout < MatchWindowTask.MINIMUM_MATCH_TIMEOUT:
            raise ValueError("Match timeout must be at least 60ms.")
        self._config.match_timeout = match_timeout

    @property
    def is_disabled(self):
        return self._config.is_disabled

    @property
    def save_new_tests(self):
        """A boolean denoting whether new tests should be automatically accepted."""
        return self._config.save_new_tests

    @save_new_tests.setter
    def save_new_tests(self, save):
        self._config.save_new_tests = save

    @property
    def save_failed_tests(self):
        """Whether failed tests should be automatically saved with all new output
        accepted."""
        return self._config.save_failed_tests

    @save_failed_tests.setter
    def save_failed_tests(self, save):
        self._config.save_failed_tests = save

    @property
    def fail_on_new_test(self):
        """ If true, Eyes will treat new tests the same as failed tests."""
        return self._config.fail_on_new_test

    @fail_on_new_test.setter
    def fail_on_new_test(self, save):
        self._config.fail_on_new_test = save

    @property
    def api_key(self):
        # type: () -> tp.Text
        """
        Gets the Api key used for authenticating the user with Eyes.

        :return: The Api key used for authenticating the user with Eyes.
        """
        return self._server_connector.api_key

    @api_key.setter
    def api_key(self, api_key):
        # type: (tp.Text) -> None
        """
        Sets the api key used for authenticating the user with Eyes.

        :param api_key: The api key used for authenticating the user with Eyes.
        """
        self._server_connector.api_key = api_key  # type: ignore

    @property
    def server_url(self):
        # type: () -> tp.Text
        """
        Gets the URL of the Eyes server.

        :return: The URL of the Eyes server, or None to use the default server.
        """
        return self._server_connector.server_url

    @server_url.setter
    def server_url(self, server_url):
        # type: (tp.Text) -> None
        """
        Sets the URL of the Eyes server.

        :param server_url: The URL of the Eyes server, or None to use the default server.
        :return: None
        """
        self._server_connector.server_url = server_url

    @property
    def scale_ratio(self):
        return self._scale_provider.scale_ratio

    @scale_ratio.setter
    def scale_ratio(self, value):
        if value:
            self._scale_provider = FixedScaleProvider(value)
        else:
            self._scale_provider = NullScaleProvider()

    @property
    def position_provider(self):
        return self._position_provider

    @position_provider.setter
    def position_provider(self, provider):
        if isinstance(provider, PositionProvider):
            self._position_provider = provider
        else:
            self._position_provider = InvalidPositionProvider()

    @property
    def full_agent_id(self):
        # type: () -> tp.Text
        """
        Gets the agent id, which identifies the current library using the SDK.

        :return: The agent id.
        """
        if self._config.agent_id is None:
            return self.base_agent_id
        return "{0} [{1}]".format(self._config.agent_id, self.base_agent_id)

    def add_property(self, name, value):
        # type: (tp.Text, tp.Text) -> None
        """
        Associates a key/value pair with the test. This can be used later for filtering.
        :param name: (string) The property name.
        :param value: (string) The property value
        """
        self._config.properties.append({"name": name, "value": value})

    @property
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
            logger.debug("close(): ignored (disabled)")
            return None
        try:
            logger.debug("close({})".format(raise_ex))
            if not self._is_open:
                raise ValueError("Eyes not open")

            self._is_open = False

            self._reset_last_screenshot()
            self._init_providers(hard_reset=True)

            # If there's no running session, we simply return the default test results.
            if not self._running_session:
                logger.debug("close(): Server session was not started")
                logger.info("close(): --- Empty test ended.")
                return TestResults()

            is_new_session = self._running_session.is_new_session
            results_url = self._running_session.url

            logger.info("close(): Ending server session...")
            should_save = (is_new_session and self.save_new_tests) or (
                (not is_new_session) and self.save_failed_tests
            )
            logger.debug("close(): automatically save session? %s" % should_save)
            results = self._server_connector.stop_session(
                self._running_session, False, should_save
            )
            results.is_new = is_new_session
            results.url = results_url
            logger.info("close(): %s" % results)

            if results.is_unresolved:
                if results.is_new:
                    instructions = "Please approve the new baseline at " + results_url
                    logger.info("--- New test ended. " + instructions)
                    if raise_ex:
                        message = "'%s' of '%s'. %s" % (
                            self._session_start_info.scenario_id_or_name,
                            self._session_start_info.app_id_or_name,
                            instructions,
                        )
                        raise NewTestError(message, results)
                else:
                    logger.info(
                        "--- Failed test ended. See details at {}".format(results_url)
                    )
                    if raise_ex:
                        raise DiffsFoundError(
                            "Test '{}' of '{}' detected differences! See details at: {}".format(
                                self._session_start_info.scenario_id_or_name,
                                self._session_start_info.app_id_or_name,
                                results_url,
                            ),
                            results,
                        )
            elif results.is_failed:
                logger.info(
                    "--- Failed test ended. See details at {}".format(results_url)
                )
                if raise_ex:
                    raise TestFailedError(
                        "Test '{}' of '{}'. See details at: {}".format(
                            self._session_start_info.scenario_id_or_name,
                            self._session_start_info.app_id_or_name,
                            results_url,
                        ),
                        results,
                    )
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
            logger.debug("abort_if_not_closed(): ignored (disabled)")
            return
        try:
            self._reset_last_screenshot()

            if self._running_session:
                logger.debug("abort_if_not_closed(): Aborting session...")
                try:
                    self._server_connector.stop_session(
                        self._running_session, True, False
                    )
                    logger.info("--- Test aborted.")
                except EyesError as e:
                    logger.info("Failed to abort server session: %s " % e)
                    pass
                finally:
                    self._running_session = None
        finally:
            logger.close()

    def get_screenshot_url(self):
        return None

    def get_image_location(self):
        pass

    def open_base(
        self,
        app_name,  # type: Text
        test_name,  # type: Text
        viewport_size=None,  # type: Optional[ViewPort]
        session_type=SessionType.SEQUENTIAL,  # type: SessionType
    ):
        # type: (...) -> None
        """
        Starts a test.

        :param app_name: The name of the application under test.
        :param test_name: The test name.
        :param viewport_size: The client's viewport size (i.e.,
                              the visible part of the document's body) or None to
                              allow any viewport size.
        :param session_type: The type of test (e.g., Progression for timing tests)
                              or Sequential by default.
        :return: An updated web driver
        :raise EyesError: If the session was already open.
        """
        logger.open_()
        if self.is_disabled:
            logger.debug("open_base(): ignored (disabled)")
            return

        if self._server_connector is None:
            raise EyesError("Server connector not set.")

        # If there's no default application name, one must be provided for the current test.
        if self._config.app_name is None:
            argument_guard.not_none(app_name)
            self._config.app_name = app_name

        argument_guard.not_none(test_name)
        self._config.test_name = test_name

        logger.info("\nAgent: {}\n".format(self.full_agent_id))
        logger.info(
            "open_base(%s, %s, %s, %s)"
            % (app_name, test_name, viewport_size, self.failure_reports)
        )
        self._config.session_type = session_type

        self.viewport_size = viewport_size
        self._open_base()

    def _before_open(self):
        pass

    def _after_open(self):
        pass

    def _ensure_configuration(self):
        if not self._config:
            self._config = Configuration()

    def _init_providers(self, hard_reset=False):
        if hard_reset:
            self._scale_provider = NullScaleProvider()
            self._position_provider = InvalidPositionProvider()
            self._cut_provider = NullCutProvider()

        if self._scale_provider is None:
            self._scale_provider = NullScaleProvider()

        if self._position_provider is None:
            self._position_provider = InvalidPositionProvider()

        if self._cut_provider is None:
            self._cut_provider = NullCutProvider()

    def _open_base(self):
        logger.open_()

        # TODO: Add repeatable check here
        self._validate_api_key()
        self._log_open_base()
        self._validate_session_open()
        self._init_providers()

        if self.viewport_size is not None:
            self._ensure_running_session()
        self._before_open()

        self._is_open = True

        self._after_open()

    def _validate_session_open(self):
        if self.is_open:
            self.abort_if_not_closed()
            raise EyesError("A test is already running")

    def _log_open_base(self):
        logger.debug(
            "Eyes server URL is '{}'".format(self._server_connector.server_url)
        )
        logger.info("Timeout = '{}'".format(self._server_connector.timeout))
        logger.debug("match_timeout = '{}'".format(self.match_timeout))
        logger.debug(
            "Default match settings = '{}' ".format(self.default_match_settings)
        )
        logger.debug("FailureReports = '{}' ".format(self.failure_reports))

    def _validate_api_key(self):
        if self.api_key is None:
            raise EyesError(
                "API key not set! Log in to https://applitools.com to obtain your"
                " API Key and use 'api_key' to set it."
            )

    def _create_session_start_info(self):
        # type: () -> None
        app_env = self._environment
        self._session_start_info = SessionStartInfo(
            agent_id=self.full_agent_id,
            session_type=self._config.session_type,
            app_id_or_name=self._config.app_name,
            ver_id=None,
            scenario_id_or_name=self._config.test_name,
            batch_info=self._config.batch,
            baseline_env_name=self._config.baseline_env_name,
            environment_name=self._config.environment_name,
            environment=app_env,
            default_match_settings=self.default_match_settings,
            branch_name=self._config.branch_name,
            parent_branch_name=self._config.parent_branch_name,
            baseline_branch_name=self._config.baseline_branch_name,
            compare_with_parent_branch=self._config.compare_with_parent_branch,
            ignore_baseline=self._config.ignore_baseline,
            save_diffs=self._config.save_diffs,
            render=self._render,
            properties=self._config.properties,
        )

    def _start_session(self):
        # type: () -> None
        logger.debug("_start_session()")
        self._ensure_viewport_size()

        # initialization of Eyes parameters if empty from ENV variables
        if self._config.batch is None:
            logger.info("No Batch set")
            self._config.batch = BatchInfo()
        else:
            logger.info("Batch is {}".format(self._config.batch))

        self._create_session_start_info()
        # Actually start the session.
        self._running_session = self._server_connector.start_session(
            self._session_start_info
        )
        self._should_match_once_on_timeout = self._running_session.is_new_session

    def _reset_last_screenshot(self):
        # type: () -> None
        self._last_screenshot = None
        self._user_inputs = []  # type: UserInputs

    def _ensure_running_session(self):
        if self._running_session:
            logger.debug("Session already running.")
            return

        logger.debug("No running session, calling start session...")
        self._start_session()

        output_provider = AppOutputProvider(self._get_app_output_with_screenshot)
        self._match_window_task = MatchWindowTask(
            self._server_connector,
            self._running_session,
            self.match_timeout,
            eyes=self,
            app_output_provider=output_provider,
        )

    def _get_app_output_with_screenshot(self, region, last_screenshot, check_settings):
        # type: (Region, EyesScreenshot, CheckSettings) -> AppOutputWithScreenshot
        logger.info("getting screenshot...")
        screenshot = self.get_screenshot()
        logger.info("Done getting screenshot!")
        if not region.is_size_empty:
            screenshot = screenshot.sub_screenshot(region)
            self._debug_screenshot_provider.save(screenshot.image, "SUB_SCREENSHOT")

        # logger.info("getting screenshot url...")
        # screenshot_url = self.get_screenshot_url()
        # logger.info("Done getting screenshot_url!")

        logger.info("Getting title, dom_url, image_location...")
        title = self._title
        logger.info("Done getting title, dom_url, image_location!")
        if not self._dom_url and (
            check_settings.values.send_dom or self.default_match_settings.send_dom
        ):
            dom_json = self._try_capture_dom()
            self._dom_url = self._try_post_dom_snapshot(dom_json)
            logger.info("dom_url: {}".format(self._dom_url))

        app_output = AppOutput(title=title, screenshot64=None, dom_url=self._dom_url)
        result = AppOutputWithScreenshot(app_output, screenshot)
        logger.info("Done")
        return result

    def _before_match_window(self):
        """
        Allow to add custom behavior after receiving response from the server
        """

    def _after_match_window(self):
        """
        Allow to add custom behavior before sending data to the server
        """

    def _check_window_base(
        self, region_provider, tag=None, ignore_mismatch=False, check_settings=None
    ):
        # type: (RegionProvider, Optional[Text], bool, CheckSettings) -> MatchResult
        if self.is_disabled:
            logger.info("check_window(%s): ignored (disabled)" % tag)
            return MatchResult(as_expected=True)

        self._ensure_running_session()

        self._before_match_window()

        tag = tag if tag is not None else ""
        result = self._match_window(
            region_provider, tag, ignore_mismatch, check_settings
        )
        self._after_match_window()
        self._handle_match_result(result, tag)
        return result

    def _handle_match_result(self, result, tag):
        # type: (MatchResult, tp.Text) -> None
        self._last_screenshot = result.screenshot
        as_expected = result.as_expected
        self._user_inputs = []
        if not as_expected:
            self._should_match_once_on_timeout = True
            if self._running_session and not self._running_session.is_new_session:
                logger.info("Window mismatch %s" % tag)
                if self.failure_reports == FailureReports.IMMEDIATE:
                    raise TestFailedError(
                        "Mismatch found in '%s' of '%s'"
                        % (
                            self._session_start_info.scenario_id_or_name,
                            self._session_start_info.app_id_or_name,
                        )
                    )

    def _try_post_dom_snapshot(self, dom_json):
        # type: (tp.Text) -> tp.Optional[tp.Text]
        """
        In case DOM data is valid uploads it to the server and return URL where it stored.
        """
        if dom_json is None:
            return None
        try:
            return self._server_connector.post_dom_snapshot(dom_json)
        except Exception as e:
            logger.warning(
                "Couldn't send DOM Json. Passing...\n Got next error: {}".format(e)
            )
            return None

    def _match_window(self, region_provider, tag, ignore_mismatch, check_settings):
        # type: (RegionProvider, Text, bool, CheckSettings) -> MatchResult
        # Update retry timeout if it wasn't specified.
        retry_timeout = -1
        if check_settings:
            retry_timeout = check_settings.values.timeout

        default_match_settings = self.default_match_settings
        # Set defaults if necessary
        if check_settings:
            if check_settings.values.match_level is None:
                check_settings = check_settings.match_level(
                    default_match_settings.match_level
                )
            if check_settings.values.ignore_caret is None:
                check_settings = check_settings.ignore_caret(
                    default_match_settings.ignore_caret
                )
        region = region_provider.get_region()
        logger.info("params: ([{}], {}, {})".format(region, tag, retry_timeout))

        result = self._match_window_task.match_window(
            self._user_inputs,
            region,
            tag,
            self._should_match_once_on_timeout,
            ignore_mismatch,
            check_settings,
            retry_timeout,
        )
        return result

    def _ensure_viewport_size(self):
        # type: () -> None
        """
        Assign the viewport size we need to be in the default content frame.
        """
        if not self._is_viewport_size_set:
            try:
                if self.viewport_size is None:
                    # TODO: ignore if viewport_size settled explicitly
                    target_size = self._get_viewport_size()
                    self.viewport_size = target_size
                else:
                    target_size = self.viewport_size
                    self._set_viewport_size(target_size)
                self._is_viewport_size_set = True
            except Exception as e:
                logger.warning("Viewport has not been setup. {}".format(e))
                self._is_viewport_size_set = False
