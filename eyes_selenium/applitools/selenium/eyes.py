from __future__ import absolute_import, unicode_literals

import typing
from concurrent.futures import TimeoutError
from typing import List, Optional, Text, Tuple, Union

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from six import string_types

from applitools.common import (
    DiffsFoundError,
    EyesError,
    NewTestError,
    RectangleSize,
    TestFailedError,
    TestResultContainer,
    TestResultsSummary,
    deprecated,
    logger,
)
from applitools.common.selenium import Configuration

from ..common.config import DEFAULT_ALL_TEST_RESULTS_TIMEOUT
from .__version__ import __version__
from .command_executor import CommandExecutor, ManagerType
from .fluent.selenium_check_settings import SeleniumCheckSettings
from .fluent.target import Target
from .universal_sdk_types import (
    demarshal_locate_result,
    demarshal_match_result,
    demarshal_test_results,
    marshal_check_settings,
    marshal_configuration,
    marshal_locate_settings,
    marshal_ocr_extract_settings,
    marshal_ocr_search_settings,
    marshal_viewport_size,
    marshal_webdriver_ref,
)

if typing.TYPE_CHECKING:
    from applitools.common import MatchLevel, MatchResult, Region, TestResults
    from applitools.common.utils.custom_types import FrameReference, ViewPort
    from applitools.core import (
        PositionProvider,
        TextRegionSettings,
        VisualLocatorSettings,
    )
    from applitools.core.extract_text import PATTERN_TEXT_REGIONS
    from applitools.core.locators import LOCATORS_TYPE
    from applitools.selenium import OCRRegion


class _EyesManager(object):
    check_window_fully_arg_default = None
    BASE_AGENT_ID = "eyes.sdk.python"

    def __init__(self, manager_type, concurrency=None, is_legacy=None):
        # type: (ManagerType, Optional[int], Optional[bool]) -> None
        self.logger = logger.bind(runner=id(self))
        self._commands = CommandExecutor.create(self.BASE_AGENT_ID, __version__)
        self._ref = self._commands.core_make_manager(
            manager_type, concurrency, is_legacy
        )

    def get_all_test_results(
        self, should_raise_exception=True, timeout=DEFAULT_ALL_TEST_RESULTS_TIMEOUT
    ):
        # type: (bool, Optional[int]) -> TestResultsSummary
        if not self._commands:
            self.logger.error("Test results are already retrieved")
            return TestResultsSummary([])
        try:
            if self._ref:
                try:
                    results = self._commands.manager_close_all_eyes(self._ref, timeout)
                except TimeoutError:
                    self.logger.warning(
                        "Tests completion timeout exceeded", timeout=timeout
                    )
                    raise EyesError("Tests didn't finish in {} seconds".format(timeout))
                # We don't have server_url, api_key and proxy settings in runner
                # USDK should return them back as a part of TestResults
                structured_results = demarshal_test_results(results, None)
                for r in structured_results:
                    _log_session_results_and_raise_exception(
                        self.logger, should_raise_exception, r
                    )
            else:
                structured_results = []
            return TestResultsSummary(
                [
                    TestResultContainer(result, None, None)
                    for result in structured_results
                ]
            )
        finally:
            self._ref = None
            self._commands.close()
            self._commands = None


class RunnerOptions(object):
    concurrency = 5

    def test_concurrency(self, value):
        # type: (int) -> RunnerOptions
        self.concurrency = value
        return self


class VisualGridRunner(_EyesManager):
    check_window_fully_arg_default = True

    def __init__(self, options_or_concurrency=RunnerOptions()):
        # type: (Union[RunnerOptions, int]) -> None
        if isinstance(options_or_concurrency, int):
            concurrency = options_or_concurrency * 5  # legacy factor
            is_legacy = True
        else:
            concurrency = options_or_concurrency.concurrency
            is_legacy = False
        super(VisualGridRunner, self).__init__(ManagerType.VG, concurrency, is_legacy)


class ClassicRunner(_EyesManager):
    def __init__(self):
        super(ClassicRunner, self).__init__(ManagerType.CLASSIC)


class Eyes(object):
    def __init__(self, runner=None):
        # type: (Union[None, _EyesManager, Text]) -> None
        self.configure = Configuration()
        self._driver = None
        self._eyes_ref = None
        if runner is None:
            self._runner = ClassicRunner()
        elif isinstance(runner, string_types):
            self.configure.server_url = runner
            self._runner = ClassicRunner()
        else:
            self._runner = runner  # type: _EyesManager
        self.logger = self._runner.logger.bind(eyes_id=id(self))
        self._commands = None

    def __getattr__(self, item):
        return getattr(self.configure, item)

    def __setattr__(self, key, value):
        if "configure" in vars(self) and (
            key in vars(self.configure)
            or key in ("match_level", "ignore_displacements")
        ):
            return setattr(self.configure, key, value)
        else:
            return super(Eyes, self).__setattr__(key, value)

    def open(
        self,
        driver,  # type: WebDriver
        app_name=None,  # type: Optional[Text]
        test_name=None,  # type: Optional[Text]
        viewport_size=None,  # type: Optional[ViewPort]
    ):
        # type: (...) -> WebDriver
        if app_name is not None:
            self.configure.app_name = app_name
        if test_name is not None:
            self.configure.test_name = test_name
        if viewport_size is not None:
            self.configure.viewport_size = viewport_size
        if self.configure.is_disabled:
            self.logger.info("open(): ignored (disabled)")
        else:
            self._commands = self._runner._commands  # noqa
            self._driver = driver
            self._eyes_ref = self._commands.manager_open_eyes(
                self._runner._ref,  # noqa
                marshal_webdriver_ref(driver),
                marshal_configuration(self.configure),
            )
        return driver

    @typing.overload
    def check(self, name, check_settings):
        # type: (Text, SeleniumCheckSettings) -> MatchResult
        """
        Takes a snapshot and matches it with the expected output.

        :param name: The name of the tag.
        :param check_settings: target which area of the window to check.
        """
        pass

    @typing.overload
    def check(self, check_settings):
        # type: (SeleniumCheckSettings) -> None
        """
        Takes a snapshot and matches it with the expected output.

        :param check_settings: target which area of the window to check.
        """
        pass

    def check(self, check_settings, name=None):
        # type: (SeleniumCheckSettings, Optional[Text]) -> Optional[MatchResult]
        if isinstance(name, SeleniumCheckSettings) or isinstance(
            check_settings, string_types
        ):
            check_settings, name = name, check_settings
        if check_settings is None:
            check_settings = Target.window()
        if name:
            check_settings = check_settings.with_name(name)

        if self.configure.is_disabled:
            self.logger.info("check(): ignored (disabled)")
            return None
        if not self.is_open:
            self.abort()
            raise EyesError("you must call open() before checking")

        results = self._commands.eyes_check(
            self._eyes_ref,
            marshal_check_settings(check_settings),
            marshal_configuration(self.configure),
        )
        if results:
            return demarshal_match_result(results)
        else:
            return None

    def locate(self, visual_locator_settings):
        # type: (VisualLocatorSettings) -> LOCATORS_TYPE
        results = self._commands.eyes_locate(
            self._eyes_ref,
            marshal_locate_settings(visual_locator_settings),
            marshal_configuration(self.configure),
        )
        return demarshal_locate_result(results)

    def extract_text(self, *regions):
        # type: (*OCRRegion) -> List[Text]
        return self._commands.eyes_extract_text(
            self._eyes_ref,
            marshal_ocr_extract_settings(regions),
            marshal_configuration(self.configure),
        )

    def extract_text_regions(self, config):
        # type: (TextRegionSettings) -> PATTERN_TEXT_REGIONS
        return self._commands.eyes_extract_text_regions(
            self._eyes_ref,
            marshal_ocr_search_settings(config),
            marshal_configuration(self.configure),
        )

    def close(self, raise_ex=True):
        # type: (bool) -> Optional[TestResults]
        """
        Ends the test.

        :param raise_ex: If true, an exception will be raised for failed/new tests.
        :return: The test results.
        """
        return self._close(raise_ex, True)

    def close_async(self):
        # type: () -> Optional[TestResults]
        return self._close(False, False)

    def abort(self):
        # type: () -> Optional[TestResults]
        """
        If a test is running, aborts it. Otherwise, does nothing.
        """
        return self._abort(True)

    def abort_async(self):
        return self._abort(False)

    @deprecated.attribute("use `abort()` instead")
    def abort_if_not_closed(self):
        return self.abort()

    @staticmethod
    def get_viewport_size(driver):
        # type: (WebDriver) -> RectangleSize
        with CommandExecutor.create(_EyesManager.BASE_AGENT_ID, __version__) as cmd:
            result = cmd.core_get_viewport_size(marshal_webdriver_ref(driver))
            return RectangleSize.from_(result)

    @staticmethod
    def set_viewport_size(driver, viewport_size):
        # type: (WebDriver, ViewPort) -> None
        with CommandExecutor.create(_EyesManager.BASE_AGENT_ID, __version__) as cmd:
            cmd.core_set_viewport_size(
                marshal_webdriver_ref(driver), marshal_viewport_size(viewport_size)
            )

    @property
    def configuration(self):
        return self.configure

    def get_configuration(self):
        # type:() -> Configuration
        return self.configure.clone()

    def set_configuration(self, configuration):
        # type:(Configuration) -> None
        self.configure = configuration.clone()

    @property
    def is_open(self):
        # type: () -> bool
        return self._eyes_ref is not None

    @property
    def server_connector(self):
        raise NotImplementedError

    @server_connector.setter
    def server_connector(self, server_connector):
        raise NotImplementedError

    @property
    def base_agent_id(self):
        # type: () -> Text
        """
        Must return version of SDK. (e.g. selenium, visualgrid) in next format:
            "eyes.{package}.python/{lib_version}"
        """
        return "{}/{}".format(self._runner.BASE_AGENT_ID, __version__)

    @property
    def full_agent_id(self):
        # type: () -> Text
        """
        Gets the agent id, which identifies the current library using the SDK.

        """
        if self.configure.agent_id is None:
            return self.base_agent_id
        else:
            return "{} [{}]".format(self.configure.agent_id, self.base_agent_id)

    @property
    def is_cut_provider_explicitly_set(self):
        # type: () -> bool
        """
        Gets is cut provider explicitly set.
        """
        raise self.configure.cut_provider is not None

    @property
    def driver(self):
        # type: () -> WebDriver
        return self._driver

    def check_window(self, tag=None, match_timeout=-1, fully=None):
        # type: (Optional[Text], int, Optional[bool]) -> MatchResult
        """
        Takes a snapshot of the application under test and matches it with the expected
         output.

        :param tag: An optional tag to be associated with the snapshot.
        :param match_timeout:  The amount of time to retry matching (milliseconds)
        :param fully: Defines that the screenshot will contain the entire window.
        """
        if fully is None:
            fully = self._runner.check_window_fully_arg_default
        return self.check(tag, Target.window().timeout(match_timeout).fully(fully))

    def check_frame(self, frame_reference, tag=None, match_timeout=-1):
        # type: (FrameReference, Optional[Text], int) -> MatchResult
        """
        Check frame.

        :param frame_reference: The name or id of the frame to check. (The same
                name/id as would be used in a call to driver.switch_to.frame()).
        :param tag: An optional tag to be associated with the match.
        :param match_timeout: The amount of time to retry matching. (Milliseconds)
        """
        return self.check(
            tag, Target.frame(frame_reference).fully().timeout(match_timeout)
        )

    def check_region(
        self,
        region,  # type: Union[Region, Text, List, Tuple, WebElement]
        tag=None,  # type: Optional[Text]
        match_timeout=-1,  # type: int
        stitch_content=False,  # type: bool
    ):
        # type: (...) -> MatchResult
        """
        Takes a snapshot of the given region from the browser using the web driver
        and matches it with the expected output. If the current context is a frame,
        the region is offsetted relative to the frame.

        :param region: The region which will be visually validated. The coordinates are
                       relative to the viewport of the current frame.
        :param tag: Description of the visual validation checkpoint.
        :param match_timeout: Timeout for the visual validation checkpoint
                              (milliseconds).
        :param stitch_content: If `True`, stitch the internal content of the region
        """
        return self.check(
            tag,
            Target.region(region).timeout(match_timeout).fully(stitch_content),
        )

    def check_element(
        self,
        element,  # type: Union[Text,List,Tuple,WebElement]
        tag=None,  # type: Optional[Text]
        match_timeout=-1,  # type: int
    ):
        # type: (...) -> MatchResult
        """
        Takes a snapshot of the given region from the browser using the web driver
        and matches it with the expected output. If the current context is a frame,
        the region is offsetted relative to the frame.

        :param element: The element to check.
        :param tag: Description of the visual validation checkpoint.
        :param match_timeout: Timeout for the visual validation checkpoint
                              (milliseconds).
        """
        return self.check(
            tag,
            Target.region(element).timeout(match_timeout).fully(),
        )

    def check_region_in_frame(
        self,
        frame_reference,  # type: FrameReference
        region,  # type: Union[Region, Text, List, Tuple, WebElement]
        tag=None,  # type: Optional[Text]
        match_timeout=-1,  # type: int
        stitch_content=False,  # type: bool
    ):
        # type: (...) -> MatchResult
        """
        Checks a region within a frame, and returns to the current frame.

        :param frame_reference: A reference to the frame in which the region
                                should be checked.
        :param region: Specifying the region to check inside the frame.
        :param tag: Description of the visual validation checkpoint.
        :param match_timeout: Timeout for the visual validation checkpoint
                              (milliseconds).
        :param stitch_content: If `True`, stitch the internal content of the region
        """
        return self.check(
            tag,
            Target.region(region)
            .frame(frame_reference)
            .stitch_content(stitch_content)
            .timeout(match_timeout),
        )

    # Impossible to implement via universal sdk
    @property
    def should_stitch_content(self):
        # type: () -> bool
        raise NotImplementedError

    @property
    def original_fc(self):
        """Gets original frame chain

        Before check() call we save original frame chain

        Returns:
            Frame chain saved before check() call
        """
        raise NotImplementedError

    @property
    def device_pixel_ratio(self):
        # type: () -> int
        """
        Gets device pixel ratio.

        :return The device pixel ratio, or if the DPR is not known yet or if it wasn't
        possible to extract it.
        """
        raise NotImplementedError

    @property
    def debug_screenshots_provider(self):
        raise NotImplementedError

    @property
    def position_provider(self):
        """
        Sets position provider.
        """
        raise NotImplementedError

    @property
    def current_frame_position_provider(self):
        # type: () -> Optional[PositionProvider]
        raise NotImplementedError

    def add_mouse_trigger_by_element(self, action, element):
        # type: (Text, WebElement) -> None
        """
        Adds a mouse trigger.

        :param action: Mouse action (click, double click etc.)
        :param element: The element on which the action was performed.
        """
        raise NotImplementedError

    def add_text_trigger_by_element(self, element, text):
        # type: (WebElement, Text) -> None
        """
        Adds a text trigger.

        :param element: The element to which the text was sent.
        :param text: The trigger's text.
        """
        raise NotImplementedError

    @property
    def agent_setup(self):
        # Saved for backward compatibility
        return None

    def _close(self, raise_ex, wait_result):
        # type: (bool, bool) -> Optional[TestResults]
        if self.configure.is_disabled:
            self.logger.info("close(): ignored (disabled)")
            return None
        if not self.is_open:
            raise EyesError("Eyes not open")
        results = self._commands.eyes_close_eyes(self._eyes_ref, wait_result)
        self._eyes_ref = None
        self._commands = None
        if wait_result:
            results = demarshal_test_results(results, self.configure)
            for r in results:
                _log_session_results_and_raise_exception(self.logger, raise_ex, r)
            return results[0]  # Original interface returns just one result
        else:
            return None

    def _abort(self, wait_result):
        # type: (bool) -> Optional[List[TestResults]]
        if self.configure.is_disabled:
            self.logger.info("abort(): ignored (disabled)")
            return None
        elif self.is_open:
            results = self._commands.eyes_abort_eyes(self._eyes_ref, wait_result)
            self._eyes_ref = None
            self._commands = None
            if wait_result:
                return demarshal_test_results(results, self.configure)
            else:
                return None


def _log_session_results_and_raise_exception(logger, raise_ex, results):
    logger.info("close({}): {}".format(raise_ex, results))
    results_url = results.url
    scenario_id_or_name = results.name
    app_id_or_name = results.app_name
    if results.steps == 0:
        logger.info("--- Test has no checks. \n\tSee details at {}".format(results_url))
        if raise_ex:
            raise TestFailedError(results, scenario_id_or_name, app_id_or_name)
    elif results.is_unresolved:
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
                "--- Differences are found. \n\tSee details at {}".format(results_url)
            )
            if raise_ex:
                raise DiffsFoundError(results, scenario_id_or_name, app_id_or_name)
    elif results.is_failed:
        logger.info("--- Failed test ended. \n\tSee details at {}".format(results_url))
        if raise_ex:
            raise TestFailedError(results, scenario_id_or_name, app_id_or_name)
    else:
        logger.info("--- Test passed. \n\tSee details at {}".format(results_url))
