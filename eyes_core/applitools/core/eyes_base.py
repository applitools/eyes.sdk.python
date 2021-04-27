from __future__ import absolute_import

import abc
import platform
import typing
import uuid

from applitools.common import (
    AppOutput,
    RectangleSize,
    Region,
    RunningSession,
    deprecated,
    logger,
)
from applitools.common.config import Configuration
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
from applitools.common.ultrafastgrid import RenderingInfo
from applitools.common.utils import ABC, argument_guard
from applitools.common.utils.compat import raise_from
from applitools.core.capture import AppOutputProvider, AppOutputWithScreenshot
from applitools.core.cut import (
    FixedCutProvider,
    NullCutProvider,
    UnscaledFixedCutProvider,
)
from applitools.core.debug import (
    FileDebugScreenshotsProvider,
    NullDebugScreenshotsProvider,
)
from applitools.core.eyes_mixins import EyesConfigurationMixin

from .__version__ import __version__
from .extract_text import (
    PATTERN_TEXT_REGIONS,
    BaseOCRRegion,
    ExtractTextProvider,
    TextRegionSettings,
)
from .match_window_task import MatchWindowTask
from .positioning import InvalidPositionProvider, PositionProvider, RegionProvider
from .scaling import FixedScaleProvider, NullScaleProvider, ScaleProvider
from .server_connector import ServerConnector

if typing.TYPE_CHECKING:
    from typing import List, Optional, Text, Union

    from applitools.common import MatchLevel
    from applitools.common.capture import EyesScreenshot
    from applitools.common.utils.custom_types import Num, UserInputs, ViewPort
    from applitools.core.fluent.check_settings import CheckSettings

__all__ = ("EyesBase",)


class _EyesBaseAbstract(ABC):
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
        """"""

    @property
    @abc.abstractmethod
    def _inferred_environment(self):
        pass


class DebugScreenshotsAbstract(ABC):
    @property
    @abc.abstractmethod
    def debug_screenshots_provider(self):
        pass

    @property
    @abc.abstractmethod
    def save_debug_screenshots(self):
        # type: () -> bool
        """True if screenshots saving enabled."""
        pass

    @save_debug_screenshots.setter
    @abc.abstractmethod
    def save_debug_screenshots(self, save):
        # type: (bool) -> None
        """If True, will save all screenshots to local directory."""
        pass

    @property
    @abc.abstractmethod
    def debug_screenshots_path(self):
        # type: () -> Optional[Text]
        """The path where you save the debug screenshots."""
        pass

    @debug_screenshots_path.setter
    @abc.abstractmethod
    def debug_screenshots_path(self, path_to_save):
        # type: (Text) -> None
        """The path where you want to save the debug screenshots."""
        pass

    @property
    @abc.abstractmethod
    def debug_screenshots_prefix(self):
        # type: () -> Optional[Text]
        """The prefix for the screenshots' names."""
        pass

    @debug_screenshots_prefix.setter
    @abc.abstractmethod
    def debug_screenshots_prefix(self, prefix):
        # type: (Text) -> None
        """The prefix for the screenshots' names."""
        pass


class ExtractTextMixin(object):
    _extract_text_provider = None  # type: Optional[ExtractTextProvider]

    def extract_text(self, *regions):
        # type: (*BaseOCRRegion) -> List[Text]
        argument_guard.not_none(self._extract_text_provider)
        logger.info("extract_text", regions=regions)
        return self._extract_text_provider.get_text(*regions)

    def extract_text_regions(self, config):
        # type: (TextRegionSettings) -> PATTERN_TEXT_REGIONS
        argument_guard.not_none(self._extract_text_provider)
        argument_guard.is_a(config, TextRegionSettings)
        logger.info("extract_text_regions", config=config)
        return self._extract_text_provider.get_text_regions(config)


class EyesBase(
    EyesConfigurationMixin,
    DebugScreenshotsAbstract,
    _EyesBaseAbstract,
    ExtractTextMixin,
    ABC,
):
    _MAX_ITERATIONS = 10
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
    _app_output_provider = None  # type: Optional[AppOutputProvider]
    _render = False
    _cut_provider = None
    _should_get_title = False  # type: bool
    _config_cls = Configuration
    _agent_run_id = None  # type: Text
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
        super(EyesBase, self).__init__()
        self._server_connector = ServerConnector()  # type: ServerConnector
        self._user_inputs = []  # type: UserInputs
        self._debug_screenshots_provider = NullDebugScreenshotsProvider()

    @property
    def match_level(self):
        # type: () -> MatchLevel
        return self.configure.match_level

    @match_level.setter
    def match_level(self, match_level):
        # type: (MatchLevel) -> None
        self.configure.match_level = match_level

    @property
    def is_cut_provider_explicitly_set(self):
        return self._cut_provider and not (
            isinstance(self._cut_provider, NullCutProvider)
        )

    @property
    def server_connector(self):
        # type: () -> ServerConnector
        return self._server_connector

    @server_connector.setter
    def server_connector(self, server_connector):
        # type: (ServerConnector) -> None
        argument_guard.is_a(server_connector, ServerConnector)
        self._server_connector = server_connector

    @property
    def cut_provider(self):
        # type: () -> Union[FixedCutProvider, UnscaledFixedCutProvider, NullCutProvider]
        return self._cut_provider

    @cut_provider.setter
    def cut_provider(self, cutprovider):
        # type: (Union[FixedCutProvider,UnscaledFixedCutProvider,NullCutProvider])->None
        argument_guard.is_in(
            cutprovider, [FixedCutProvider, UnscaledFixedCutProvider, NullCutProvider]
        )
        self._cut_provider = cutprovider

    @property
    def debug_screenshots_provider(self):
        return self._debug_screenshots_provider

    @property
    def save_debug_screenshots(self):
        # type: () -> bool
        """True if screenshots saving enabled."""
        return isinstance(
            self._debug_screenshots_provider, FileDebugScreenshotsProvider
        )

    @save_debug_screenshots.setter
    def save_debug_screenshots(self, save):
        # type: (bool) -> None
        prev = self._debug_screenshots_provider
        if save:
            self._debug_screenshots_provider = FileDebugScreenshotsProvider(
                prev.prefix, prev.path
            )
        else:
            self._debug_screenshots_provider = NullDebugScreenshotsProvider()

    @property
    def debug_screenshots_path(self):
        # type: () -> Optional[Text]
        return self._debug_screenshots_provider.path

    @debug_screenshots_path.setter
    def debug_screenshots_path(self, path_to_save):
        # type: (Text) -> None
        self._debug_screenshots_provider.path = path_to_save

    @property
    def debug_screenshots_prefix(self):
        # type: () -> Optional[Text]
        return self._debug_screenshots_provider.prefix

    @debug_screenshots_prefix.setter
    def debug_screenshots_prefix(self, prefix):
        # type: (Text) -> None
        self._debug_screenshots_provider.prefix = prefix

    @property
    def _environment(self):
        # type: () -> AppEnvironment
        """
        Application environment is the environment (e.g., the host OS)
        which runs the application under test.

        :return: The current application environment.
        """

        app_env = AppEnvironment(
            os=self.configure.host_os,
            hosting_app=self.configure.host_app,
            display_size=self.configure.viewport_size,
            inferred=self._inferred_environment,
        )
        return app_env

    @property
    def scale_ratio(self):
        # type: () -> float
        return self._scale_provider.scale_ratio

    @scale_ratio.setter
    def scale_ratio(self, scale_ratio):
        # type: (float) -> None
        if scale_ratio:
            self._scale_provider = FixedScaleProvider(scale_ratio)
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
        if self.configure.agent_id is None:
            return self.base_agent_id
        return "{0} [{1}]".format(self.configure.agent_id, self.base_agent_id)

    @property
    def agent_setup(self):
        # Saved for backward compatibility
        return None

    def add_property(self, name, value):
        # type: (Text, Text) -> None
        """
        Associates a key/value pair with the test. This can be used later for filtering.
        :param name: (string) The property name.
        :param value: (string) The property value
        """
        self.configure.add_property(name, value)

    def clear_properties(self):
        """
        Clears the list of custom properties.
        """
        self.configure.clear_properties()

    @property
    def is_open(self):
        # type: () -> bool
        """
        Returns whether the session is currently running.
        """
        return self._is_opened

    @staticmethod
    def log_session_results_and_raise_exception(raise_ex, results):
        logger.info("close({}): {}".format(raise_ex, results))
        results_url = results.url
        scenario_id_or_name = results.name
        app_id_or_name = results.app_name
        if results.is_unresolved:
            if results.is_new:
                logger.info(
                    "--- New test ended. \n\tPlease approve the new baseline at {}".format(
                        results_url
                    )
                )
                if raise_ex:
                    raise NewTestError(results, scenario_id_or_name, app_id_or_name)
            else:
                logger.info(
                    "--- Differences are found. \n\tSee details at {}".format(
                        results_url
                    )
                )
                if raise_ex:
                    raise DiffsFoundError(results, scenario_id_or_name, app_id_or_name)
        elif results.is_failed:
            logger.info(
                "--- Failed test ended. \n\tSee details at {}".format(results_url)
            )
            if raise_ex:
                raise TestFailedError(results, scenario_id_or_name, app_id_or_name)
        else:
            logger.info("--- Test passed. \n\tSee details at {}".format(results_url))

    def close(self, raise_ex=True):
        # type: (bool) -> Optional[TestResults]
        """
        Ends the test.

        :param raise_ex: If true, an exception will be raised for failed/new tests.
        :return: The test results.
        """
        if self.configure.is_disabled:
            logger.debug("close(): ignored (disabled)")
            return None
        try:
            logger.debug("close({})".format(raise_ex))
            if not self._is_opened:
                raise EyesError("Eyes not open")

            self._is_opened = False

            self._reset_last_screenshot()
            self._init_providers(hard_reset=True)

            # If there's no running session, we simply return the default test results.
            if not self._running_session:
                logger.debug("close(): Server session was not started")
                logger.info("close(): --- Empty test ended.")
                return TestResults(status="Failed")

            is_new_session = self._running_session.is_new_session
            results_url = self._running_session.url

            logger.info("close(): Ending server session...")
            should_save = (is_new_session and self.configure.save_new_tests) or (
                (not is_new_session) and self.configure.save_failed_tests
            )
            logger.info("close(): Automatically save session? %s" % should_save)
            results = self._server_connector.stop_session(
                self._running_session, False, should_save
            )
            results.is_new = is_new_session
            results.url = results_url
            self.log_session_results_and_raise_exception(raise_ex, results)

            return results
        finally:
            self._running_session = None
            self._session_start_info = None

    def abort(self):
        # type: () -> Optional[TestResults]
        """
        If a test is running, aborts it. Otherwise, does nothing.
        """
        if self.configure.is_disabled:
            logger.debug("abort(): ignored (disabled)")
            return
        self._reset_last_screenshot()

        if self._running_session:
            results_url = self._running_session.url

            logger.debug("abort(): Aborting session...")
            try:
                logger.info(
                    "--- Test aborted. \n\tSee details at {}".format(results_url)
                )
                results = self._server_connector.stop_session(
                    self._running_session, True, False
                )
                results.url = results_url
                return results
            except EyesError as e:
                logger.info("Failed to abort server session: %s " % e)
            finally:
                self._running_session = None

    @deprecated.attribute("use `abort()` instead")
    def abort_if_not_closed(self):
        self.abort()

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
        if self.configure.is_disabled:
            logger.debug("open_base(): ignored (disabled)")
            return

        if self._server_connector is None:
            raise EyesError("Server connector not set.")

        # If there's no default application name, one must be provided for the current test.
        if self.configure.app_name is None:
            argument_guard.not_none(app_name)
            self.configure.app_name = app_name

        argument_guard.not_none(test_name)
        self.configure.test_name = test_name

        logger.info("\nAgent: {}\n".format(self.full_agent_id))
        logger.info(
            "open_base(%s, %s, %s, %s)"
            % (app_name, test_name, viewport_size, self.configure.failure_reports)
        )
        self.configure.session_type = session_type
        self.configure.viewport_size = viewport_size

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
            self._debug_screenshots_provider = NullDebugScreenshotsProvider()

        if self._scale_provider is None:
            self._scale_provider = NullScaleProvider()

        if self._position_provider is None:
            self._position_provider = InvalidPositionProvider()

        if self._cut_provider is None:
            self._cut_provider = NullCutProvider()

    def _open_base(self):
        if self.configure.is_disabled:
            logger.debug("open_base(): ignored (disabled)")
            return
        self._log_open_base()

        retry = 0
        while retry < self._MAX_ITERATIONS:
            try:
                self._validate_session_open()
                self._init_providers()

                self._is_viewport_size_set = False

                self._before_open()
                try:
                    # postpone session opening if no viewport_size set
                    if self.configure.viewport_size:
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
                raise e

        raise EyesError("eyes.open_base() failed")

    def _validate_session_open(self):
        if self.is_open:
            self.abort()
            raise EyesError("A test is already running")

    def _log_open_base(self):
        logger.info(
            "Applitools SDK {}, running on: {} {} {}".format(
                __version__,
                platform.platform(),
                platform.python_implementation(),
                platform.python_version(),
            )
        )
        logger.info("Eyes server URL is '{}'".format(self.configure.server_url))
        logger.info("Timeout = {} ms".format(self.configure._timeout))
        logger.debug("match_timeout = {} ms".format(self.configure.match_timeout))
        logger.info(
            "Default match settings = '{}' ".format(
                self.configure.default_match_settings
            )
        )
        logger.info("FailureReports = '{}' ".format(self.configure.failure_reports))

    def _create_session_start_info(self):
        # type: () -> None
        self._session_start_info = self._session_start_info or SessionStartInfo(
            agent_id=self.full_agent_id,
            session_type=self.configure.session_type,
            app_id_or_name=self.configure.app_name,
            ver_id=None,
            scenario_id_or_name=self.configure.test_name,
            batch_info=self.configure.batch,
            baseline_env_name=self.configure.baseline_env_name,
            environment_name=self.configure.environment_name,
            environment=self._environment,
            default_match_settings=self.configure.default_match_settings,
            branch_name=self.configure.branch_name,
            parent_branch_name=self.configure.parent_branch_name,
            baseline_branch_name=self.configure.baseline_branch_name,
            save_diffs=self.configure.save_diffs,
            render=self._render,
            properties=self.configure.properties,
            agent_session_id=str(uuid.uuid4()),
            agent_run_id=self._agent_run_id,
        )

    def _start_session(self):
        # type: () -> None
        logger.debug("_start_session()")
        self.__ensure_viewport_size()

        # initialization of Eyes parameters if empty from ENV variables
        logger.info("Batch is {}".format(self.configure.batch))

        self._server_connector.update_config(
            self.get_configuration(), self.full_agent_id
        )
        self._create_session_start_info()
        # Actually start the session.
        self._running_session = self._server_connector.start_session(
            self._session_start_info
        )
        self._should_match_once_on_timeout = self._running_session.is_new_session

    def _reset_last_screenshot(self):
        # type: () -> None
        self._last_screenshot = None
        del self._user_inputs[:]

    def _ensure_running_session(self):
        if self._running_session:
            logger.debug("Session already running.")
            return

        logger.debug("No running session, calling start session...")
        self._start_session()

        self._app_output_provider = AppOutputProvider(
            self._get_app_output_with_screenshot
        )
        self._match_window_task = MatchWindowTask(
            self._server_connector,
            self._running_session,
            self.configure.match_timeout,
            eyes=self,
            app_output_provider=self._app_output_provider,
        )

    def _get_app_output_with_screenshot(self, region, last_screenshot, check_settings):
        # type: (Region, EyesScreenshot, CheckSettings) -> AppOutputWithScreenshot
        logger.info("Getting screenshot...")
        screenshot = self._get_screenshot()
        logger.info("Done getting screenshot!")
        if not region.is_size_empty:
            screenshot = screenshot.sub_screenshot(region)
            self._debug_screenshots_provider.save(screenshot.image, "sub_screenshot")

        if not self._dom_url and (
            self.configure.send_dom or check_settings.values.send_dom
        ):
            logger.info("Capturing DOM")
            dom_json = self._try_capture_dom()
            self._dom_url = self._try_post_dom_capture(dom_json)
            logger.info("Captured DOM URL: {}".format(self._dom_url))

        app_output = AppOutput(
            title=self._title, screenshot_bytes=None, dom_url=self._dom_url
        )
        result = AppOutputWithScreenshot(app_output, screenshot)
        logger.info("Done getting screenshot and DOM!")
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
        self,
        region_provider,  # type: RegionProvider
        ignore_mismatch=False,  # type: bool
        check_settings=None,  # type: CheckSettings
        source=None,  # type: Optional[Text]
    ):
        # type: (...) -> MatchResult
        if self.configure.is_disabled:
            logger.info(
                "check_window(%s): ignored (disabled)" % check_settings.values.name
            )
            return MatchResult(as_expected=True)

        self._ensure_running_session()

        self._before_match_window()

        result = self._match_window(region_provider, check_settings, source)

        if not ignore_mismatch:
            del self._user_inputs[:]
            self._last_screenshot = result.screenshot

        self._after_match_window()
        self._handle_match_result(result, check_settings.values.name)
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
                if self.configure.failure_reports == FailureReports.IMMEDIATE:
                    raise TestFailedError(
                        "Mismatch found in '%s' of '%s'"
                        % (
                            self._session_start_info.scenario_id_or_name,
                            self._session_start_info.app_id_or_name,
                        )
                    )

    def _try_post_dom_capture(self, dom_json):
        # type: (Text) -> Optional[Text]
        """
        In case DOM data is valid uploads it to the server and return URL where it stored.
        """
        if dom_json is None:
            return None
        try:
            return self._server_connector.post_dom_capture(dom_json)
        except Exception as e:
            logger.warning(
                "Couldn't send DOM Json. Passing...\n Got next error: {}".format(e)
            )
            return None

    def _match_window(self, region_provider, check_settings, source):
        # type: (RegionProvider, CheckSettings, Optional[Text]) -> MatchResult
        # Update retry timeout if it wasn't specified.
        retry_timeout_ms = -1  # type: Num
        if check_settings:
            retry_timeout_ms = check_settings.values.timeout

        region = region_provider.get_region()
        logger.debug(
            "params: ([{}], {}, {} ms)".format(
                region, check_settings.values.name, retry_timeout_ms
            )
        )
        result = self._match_window_task.match_window(
            self._user_inputs,
            region,
            self._should_match_once_on_timeout,
            check_settings,
            retry_timeout_ms,
            source,
        )
        return result

    def __ensure_viewport_size(self):
        # type: () -> None
        """
        Assign the viewport size we need to be in the default content frame.
        """
        if self._is_viewport_size_set:
            return
        try:
            if self.configure.viewport_size is None:
                # TODO: ignore if viewport_size settled explicitly
                target_size = self._get_viewport_size()
                self.configure.viewport_size = target_size
            else:
                target_size = self.configure.viewport_size
                self._set_viewport_size(target_size)
            self._is_viewport_size_set = True
        except Exception as e:
            self._is_viewport_size_set = False
            raise_from(EyesError("Viewport has not been setup"), e)
