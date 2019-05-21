from __future__ import absolute_import

import abc
import typing

from applitools.common import (
    AppOutput,
    BatchInfo,
    Configuration,
    RectangleSize,
    Region,
    RunningSession,
    logger,
)
from applitools.common.errors import (
    DiffsFoundError,
    EyesError,
    NewTestError,
    TestFailedError,
)
from applitools.common.match import MatchResult
from applitools.common.metadata import AppEnvironment, SessionStartInfo
from applitools.common.server import FailureReports, SessionType
from applitools.common.test_results import TestResults
from applitools.common.utils import ABC, argument_guard, general_utils
from applitools.common.visual_grid import RenderingInfo
from applitools.core.capture import AppOutputProvider, AppOutputWithScreenshot
from applitools.core.cut import NullCutProvider
from applitools.core.debug import (
    FileDebugScreenshotProvider,
    NullDebugScreenshotProvider,
)

from .match_window_task import MatchWindowTask
from .positioning import InvalidPositionProvider, PositionProvider, RegionProvider
from .scaling import FixedScaleProvider, NullScaleProvider, ScaleProvider
from .server_connector import ServerConnector

if typing.TYPE_CHECKING:
    from applitools.common.utils.custom_types import ViewPort, UserInputs, Num
    from applitools.core.fluent.check_settings import CheckSettings
    from applitools.common.capture import EyesScreenshot
    from typing import Optional, Text

__all__ = ("EyesBase",)


class _EyesBaseAbstract(ABC):
    @property
    @abc.abstractmethod
    def configuration(self):
        # type: () -> Configuration
        """
        Returns Eyes configuration
        """

    @abc.abstractmethod
    def _try_capture_dom(self):
        # type: () -> Text
        """
        Returns the string with DOM of the current page in the prepared format or empty string
        """

    @property
    @abc.abstractmethod
    def base_agent_id(self):
        # type: () -> Text
        """
        Must return version of SDK. (e.g. Selenium, Images) in next format:
            "eyes.{package}.python/{lib_version}"
        """

    @abc.abstractmethod
    def _get_screenshot(self):
        # type: (...) -> EyesScreenshot
        pass

    @abc.abstractmethod
    def get_viewport_size_static(self):
        # type: () -> RectangleSize
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
        # type: () -> Text
        """
        Returns the title of the window of the AUT, or empty string
         if the title is not available.
        """

    @abc.abstractmethod
    def _get_viewport_size(self):
        # type: () -> RectangleSize
        """

        :return:
        """

    @abc.abstractmethod
    def _set_viewport_size(self, size):
        # type: (ViewPort) -> None
        """

        """

    @property
    @abc.abstractmethod
    def _inferred_environment(self):
        pass


class EyesBase(_EyesBaseAbstract):
    MAX_ITERATION = 10
    _running_session = None  # type: Optional[RunningSession]
    _session_start_info = None  # type: Optional[SessionStartInfo]
    _last_screenshot = None  # type: Optional[EyesScreenshot]
    _scale_provider = None  # type: Optional[ScaleProvider]
    _dom_url = None  # type: Optional[Text]
    _position_provider = None  # type: Optional[PositionProvider]
    _is_viewport_size_set = False  # type: bool
    _should_match_once_on_timeout = False  # type: bool
    _is_opened = False  # type: bool
    _render_info = None  # type: Optional[RenderingInfo]
    _render = False
    _cut_provider = None
    _should_get_title = False  # type: bool

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

    def __init__(self):
        """
        Creates a new (possibly disabled) Eyes instance that
        interacts with the Eyes server.
        """
        self._config_provider = Configuration()
        self._server_connector = ServerConnector()  # type: ServerConnector
        self._user_inputs = []  # type: UserInputs
        self._debug_screenshot_provider = NullDebugScreenshotProvider()

    @property
    def is_debug_screenshot_provided(self):
        # type: () -> bool
        """True if screenshots saving enabled."""
        return isinstance(self._debug_screenshot_provider, FileDebugScreenshotProvider)

    @is_debug_screenshot_provided.setter
    def is_debug_screenshot_provided(self, save):
        prev = self._debug_screenshot_provider
        if save:
            self._debug_screenshot_provider = FileDebugScreenshotProvider(
                prev.prefix, prev.path
            )
        else:
            self._debug_screenshot_provider = NullDebugScreenshotProvider()

    @property
    def _environment(self):
        # type: () -> AppEnvironment
        """
        Application environment is the environment (e.g., the host OS)
        which runs the application under test.

        :return: The current application environment.
        """

        app_env = AppEnvironment(
            os=self.configuration.host_os,
            hosting_app=self.configuration.host_app,
            display_size=self.configuration.viewport_size,
            inferred=self._inferred_environment,
        )
        return app_env

    @property
    def configuration(self):
        return self._config_provider

    @configuration.setter
    def configuration(self, value):
        # type:(Configuration) -> None
        self._config_provider = value

    @property
    def scale_ratio(self):
        # type: () -> float
        return self._scale_provider.scale_ratio

    @scale_ratio.setter
    def scale_ratio(self, value):
        # type: (float) -> None
        if value:
            self._scale_provider = FixedScaleProvider(value)
        else:
            self._scale_provider = NullScaleProvider()

    @property
    def position_provider(self):
        # type: () -> PositionProvider
        return self._position_provider

    @position_provider.setter
    def position_provider(self, provider):
        # type: (PositionProvider) -> None
        if isinstance(provider, PositionProvider):
            self._position_provider = provider
        else:
            self._position_provider = InvalidPositionProvider()

    @property
    def full_agent_id(self):
        # type: () -> Text
        """
        Gets the agent id, which identifies the current library using the SDK.

        :return: The agent id.
        """
        if self.configuration.agent_id is None:
            return self.base_agent_id
        return "{0} [{1}]".format(self.configuration.agent_id, self.base_agent_id)

    @property
    def agent_setup(self):
        return None

    def add_property(self, name, value):
        # type: (Text, Text) -> None
        """
        Associates a key/value pair with the test. This can be used later for filtering.
        :param name: (string) The property name.
        :param value: (string) The property value
        """
        self.configuration.properties.append({"name": name, "value": value})

    def clear_properties(self):
        self.configuration.properties.clear()

    @property
    def is_opened(self):
        # type: () -> bool
        """
        Returns whether the session is currently running.
        """
        return self._is_opened

    def close(self, raise_ex=True):
        # type: (bool) -> Optional[TestResults]
        """
        Ends the test.

        :param raise_ex: If true, an exception will be raised for failed/new tests.
        :return: The test results.
        """
        if self.configuration.is_disabled:
            logger.debug("close(): ignored (disabled)")
            return None
        try:
            logger.debug("close({})".format(raise_ex))
            if not self._is_opened:
                raise ValueError("Eyes not open")

            self._is_opened = False

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
            should_save = (is_new_session and self.configuration.save_new_tests) or (
                (not is_new_session) and self.configuration.save_failed_tests
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
                        "--- Failed test ended. \n\tSee details at {}".format(
                            results_url
                        )
                    )
                    if raise_ex:
                        raise DiffsFoundError(
                            "Test '{}' of '{}' detected differences! "
                            "\n\tSee details at: {}".format(
                                self._session_start_info.scenario_id_or_name,
                                self._session_start_info.app_id_or_name,
                                results_url,
                            ),
                            results,
                        )
            elif results.is_failed:
                logger.info(
                    "--- Failed test ended. \n\tSee details at {}".format(results_url)
                )
                if raise_ex:
                    raise TestFailedError(
                        "Test '{}' of '{}'. \n\tSee details at: {}".format(
                            self._session_start_info.scenario_id_or_name,
                            self._session_start_info.app_id_or_name,
                            results_url,
                        ),
                        results,
                    )
            # Test passed
            logger.info("--- Test passed. \n\tSee details at {}".format(results_url))

            return results
        finally:
            self._running_session = None
            logger.close()

    def abort_if_not_closed(self):
        # type: () -> None
        """
        If a test is running, aborts it. Otherwise, does nothing.
        """
        if self.configuration.is_disabled:
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
        if self.configuration.is_disabled:
            logger.debug("open_base(): ignored (disabled)")
            return

        if self._server_connector is None:
            raise EyesError("Server connector not set.")

        # If there's no default application name, one must be provided for the current test.
        if self.configuration.app_name is None:
            argument_guard.not_none(app_name)
            self.configuration.app_name = app_name

        argument_guard.not_none(test_name)
        self.configuration.test_name = test_name

        logger.info("\nAgent: {}\n".format(self.full_agent_id))
        logger.info(
            "open_base(%s, %s, %s, %s)"
            % (app_name, test_name, viewport_size, self.configuration.failure_reports)
        )
        self.configuration.session_type = session_type
        self.configuration.viewport_size = viewport_size

        self._open_base()

    def _before_open(self):
        pass

    def _after_open(self):
        pass

    def _init_providers(self, hard_reset=False):
        if hard_reset:
            self._scale_provider = NullScaleProvider()
            self._position_provider = InvalidPositionProvider()
            self._cut_provider = NullCutProvider()
            self._debug_screenshot_provider = NullDebugScreenshotProvider()

        if self._scale_provider is None:
            self._scale_provider = NullScaleProvider()

        if self._position_provider is None:
            self._position_provider = InvalidPositionProvider()

        if self._cut_provider is None:
            self._cut_provider = NullCutProvider()

    def _open_base(self):
        if self.configuration.is_disabled:
            logger.debug("open_base(): ignored (disabled)")
            return
        logger.open_()
        self._log_open_base()

        retry = 0
        while retry < self.MAX_ITERATION:
            try:
                self._validate_api_key()
                self._validate_session_open()
                self._init_providers()

                self._is_viewport_size_set = False

                self._before_open()
                try:
                    if self.configuration.viewport_size:
                        self._ensure_running_session()
                except Exception as e:
                    logger.exception(e)
                    retry += 1
                    continue

                self._is_opened = True
                self._after_open()
                return None
            except EyesError as e:
                logger.exception(e)
                logger.close()
                raise e

        raise EyesError("eyes.open_base() failed")

    def _validate_session_open(self):
        if self.is_opened:
            self.abort_if_not_closed()
            raise EyesError("A test is already running")

    def _log_open_base(self):
        logger.debug(
            "Eyes server URL is '{}'".format(self._server_connector.server_url)
        )
        logger.debug("Timeout = {} ms".format(self.configuration.timeout))
        logger.debug("match_timeout = {} ms".format(self.configuration.match_timeout))
        logger.debug(
            "Default match settings = '{}' ".format(
                self.configuration.default_match_settings
            )
        )
        logger.debug(
            "FailureReports = '{}' ".format(self.configuration.failure_reports)
        )

    def _validate_api_key(self):
        if self.configuration.api_key is None:
            raise EyesError(
                "API key not set! Log in to https://applitools.com to obtain your"
                " API Key and use 'api_key' to set it."
            )

    def _create_session_start_info(self):
        # type: () -> None
        self._session_start_info = SessionStartInfo(
            agent_id=self.full_agent_id,
            session_type=self.configuration.session_type,
            app_id_or_name=self.configuration.app_name,
            ver_id=None,
            scenario_id_or_name=self.configuration.test_name,
            batch_info=self.configuration.batch,
            baseline_env_name=self.configuration.baseline_env_name,
            environment_name=self.configuration.environment_name,
            environment=self._environment,
            default_match_settings=self.configuration.default_match_settings,
            branch_name=self.configuration.branch_name,
            parent_branch_name=self.configuration.parent_branch_name,
            baseline_branch_name=self.configuration.baseline_branch_name,
            compare_with_parent_branch=self.configuration.compare_with_parent_branch,
            ignore_baseline=self.configuration.ignore_baseline,
            save_diffs=self.configuration.save_diffs,
            render=self._render,
            properties=self.configuration.properties,
        )

    def _start_session(self):
        # type: () -> None
        logger.debug("_start_session()")
        self.__ensure_viewport_size()

        # initialization of Eyes parameters if empty from ENV variables
        if self.configuration.batch is None:
            logger.info("No Batch set")
            self.configuration.batch = BatchInfo()
        else:
            logger.info("Batch is {}".format(self.configuration.batch))

        self._server_connector.update_config(self.configuration)
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
            self.configuration.match_timeout,
            eyes=self,
            app_output_provider=output_provider,
        )

    def _get_app_output_with_screenshot(self, region, last_screenshot, check_settings):
        # type: (Region, EyesScreenshot, CheckSettings) -> AppOutputWithScreenshot
        logger.info("getting screenshot...")
        screenshot = self._get_screenshot()
        logger.info("Done getting screenshot!")
        if not region.is_size_empty:
            screenshot = screenshot.sub_screenshot(region)
            self._debug_screenshot_provider.save(screenshot.image, "SUB_SCREENSHOT")

        title = self._title
        logger.info("Done getting title")

        if not self._dom_url and (
            self.configuration.send_dom or check_settings.values.send_dom
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
        if self.configuration.is_disabled:
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
        # type: (MatchResult, Text) -> None
        self._last_screenshot = result.screenshot
        as_expected = result.as_expected
        self._user_inputs = []
        if not as_expected:
            self._should_match_once_on_timeout = True
            if self._running_session and not self._running_session.is_new_session:
                logger.info("Window mismatch %s" % tag)
                if self.configuration.failure_reports == FailureReports.IMMEDIATE:
                    raise TestFailedError(
                        "Mismatch found in '%s' of '%s'"
                        % (
                            self._session_start_info.scenario_id_or_name,
                            self._session_start_info.app_id_or_name,
                        )
                    )

    def _try_post_dom_snapshot(self, dom_json):
        # type: (Text) -> Optional[Text]
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
        retry_timeout_ms = -1  # type: Num
        if check_settings:
            retry_timeout_ms = check_settings.values.timeout

        get_config_value = general_utils.use_default_if_none_factory(
            self.configuration.default_match_settings, self.configuration
        )
        # Set defaults if necessary
        if check_settings.values.match_level is None:
            check_settings = check_settings.match_level(get_config_value("match_level"))
        if check_settings.values.ignore_caret is None:
            check_settings = check_settings.ignore_caret(
                get_config_value("ignore_caret")
            )
        if check_settings.values.send_dom is None:
            check_settings = check_settings.ignore_caret(get_config_value("send_dom"))
        if check_settings.values.use_dom is None:
            check_settings = check_settings.ignore_caret(get_config_value("use_dom"))
        if check_settings.values.enable_patterns is None:
            check_settings = check_settings.ignore_caret(
                get_config_value("enable_patterns")
            )

        region = region_provider.get_region()
        logger.debug("params: ([{}], {}, {})".format(region, tag, retry_timeout_ms))

        result = self._match_window_task.match_window(
            self._user_inputs,
            region,
            tag,
            self._should_match_once_on_timeout,
            ignore_mismatch,
            check_settings,
            retry_timeout_ms,
        )
        return result

    def __ensure_viewport_size(self):
        # type: () -> None
        """
        Assign the viewport size we need to be in the default content frame.
        """
        if not self._is_viewport_size_set:
            try:
                if self.configuration.viewport_size is None:
                    # TODO: ignore if viewport_size settled explicitly
                    target_size = self._get_viewport_size()
                    self.configuration.viewport_size = target_size
                else:
                    target_size = self.configuration.viewport_size
                    self._set_viewport_size(target_size)
                self._is_viewport_size_set = True
            except Exception as e:
                logger.warning("Viewport has not been setup. {}".format(e))
                self._is_viewport_size_set = False
                raise e
