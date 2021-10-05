from __future__ import absolute_import, unicode_literals

import typing
from typing import List, Optional, Text, Tuple, Union

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from six import string_types

from applitools.common import (
    DiffsFoundError,
    EyesError,
    NewTestError,
    TestFailedError,
    TestResultContainer,
    TestResultsSummary,
    deprecated,
    logger,
)
from applitools.common.selenium import Configuration

from ..common.config import DEFAULT_ALL_TEST_RESULTS_TIMEOUT
from .command_executor import CommandExecutor, ManagerType
from .fluent.selenium_check_settings import SeleniumCheckSettings
from .fluent.target import Target
from .universal_sdk_types import (
    demarshal_match_result,
    demarshal_test_results,
    marshal_check_settings,
    marshal_configuration,
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
    def __init__(self, manager_type, concurrency=None, is_legacy=None):
        # type: (ManagerType, Optional[int], Optional[bool]) -> None
        from . import server

        self.logger = logger.bind(runner=id(self))
        self._manager_args = (manager_type, concurrency, is_legacy)
        self._manager_ref = None
        self._remote_sdk = server.connect()

    def get_all_test_results(
        self, should_raise_exception=True, timeout=DEFAULT_ALL_TEST_RESULTS_TIMEOUT
    ):
        # type: (bool, Optional[int]) -> TestResultsSummary
        # TODO: implement timeout
        if self._manager_ref:
            results = self._remote_sdk.manager_close_all_eyes(self._manager_ref)
            self._manager_ref = None
            structured_results = demarshal_test_results(results)
            for r in structured_results:
                _log_session_results_and_raise_exception(
                    self.logger, should_raise_exception, r
                )
        else:
            structured_results = []
        return TestResultsSummary(
            [TestResultContainer(result, None, None) for result in structured_results]
        )

    def _get_manager_ref(self):
        if self._manager_ref is None:
            self._manager_ref = self._remote_sdk.core_make_manager(*self._manager_args)
        return self._manager_ref


class RunnerOptions(object):
    concurrency = 5

    def test_concurrency(self, value):
        # type: (int) -> RunnerOptions
        self.concurrency = value
        return self


class VisualGridRunner(_EyesManager):
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
            self._manager = ClassicRunner()
        elif isinstance(runner, string_types):
            self.configure.server_url = runner
            self._manager = ClassicRunner()
        else:
            self._manager = runner  # type: _EyesManager
        self.logger = self._manager.logger.bind(eyes_id=id(self))
        self.__setattr__ = self.__setattr_delayed

    def __getattr__(self, item):
        return getattr(self.configure, item)

    def __setattr_delayed(self, key, value):
        return setattr(self.configure, key, value)

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
            remote_sdk = self._manager._remote_sdk  # noqa
            manager_ref = self._manager._get_manager_ref()  # noqa
            self._driver = driver
            self._eyes_ref = remote_sdk.manager_open_eyes(
                manager_ref,
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

        remote_sdk = self._manager._remote_sdk  # noqa
        results = remote_sdk.eyes_check(
            self._eyes_ref,
            marshal_check_settings(check_settings),
            marshal_configuration(self.configure),
        )
        return demarshal_match_result(results)

    def locate(self, visual_locator_settings):
        # type: (VisualLocatorSettings) -> LOCATORS_TYPE
        raise NotImplementedError

    def extract_text(self, *regions):
        # type: (*OCRRegion) -> List[Text]
        raise NotImplementedError

    def extract_text_regions(self, config):
        # type: (TextRegionSettings) -> PATTERN_TEXT_REGIONS
        raise NotImplementedError

    def close(self, raise_ex=True):
        # type: (bool) -> Optional[List[TestResults]]
        """
        Ends the test.

        :param raise_ex: If true, an exception will be raised for failed/new tests.
        :return: The test results.
        """
        if self.configure.is_disabled:
            self.logger.info("close(): ignored (disabled)")
            return None
        if not self.is_open:
            raise EyesError("Eyes not open")
        remote_sdk = self._manager._remote_sdk  # noqa
        results = remote_sdk.eyes_close_eyes(self._eyes_ref)
        self._eyes_ref = None
        results = demarshal_test_results(results)
        for r in results:
            _log_session_results_and_raise_exception(self.logger, raise_ex, r)
        return results[0]

    def abort(self):
        # type: () -> Optional[List[TestResults]]
        """
        If a test is running, aborts it. Otherwise, does nothing.
        """
        if self.configure.is_disabled:
            self.logger.info("abort(): ignored (disabled)")
            return None
        elif self.is_open:
            remote_sdk = self._manager._remote_sdk  # noqa
            results = remote_sdk.eyes_abort_eyes(self._eyes_ref)
            return demarshal_test_results(results)

    @staticmethod
    def get_viewport_size(driver):
        # type: (WebDriver) -> ViewPort
        raise NotImplementedError

    @staticmethod
    def set_viewport_size(driver, size):
        # type: (WebDriver, ViewPort) -> None
        raise NotImplementedError

    def get_configuration(self):
        # type:() -> Configuration
        return self.configure.clone()

    def set_configuration(self, configuration):
        # type:(Configuration) -> None
        self.configure = configuration.clone()

    @property
    def server_connector(self):
        raise NotImplementedError

    @server_connector.setter
    def server_connector(self, server_connector):
        raise NotImplementedError

    @property
    def is_open(self):
        # type: () -> bool
        return self._eyes_ref is not None

    @property
    def rotation(self):
        # type: () -> Optional[int]
        raise NotImplementedError

    @rotation.setter
    def rotation(self, rotation):
        # type: (Union[int,float]) -> None
        raise NotImplementedError

    @property
    def base_agent_id(self):
        # type: () -> Text
        """
        Must return version of SDK. (e.g. selenium, visualgrid) in next format:
            "eyes.{package}.python/{lib_version}"
        """
        raise NotImplementedError

    @property
    def full_agent_id(self):
        # type: () -> Text
        """
        Gets the agent id, which identifies the current library using the SDK.

        """
        raise NotImplementedError

    @property
    def match_level(self):
        # type: () -> MatchLevel
        return self.configure.match_level

    @match_level.setter
    def match_level(self, match_level):
        # type: (MatchLevel) -> None
        self.configure.match_level = match_level

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
    def scale_ratio(self):
        # type: () -> float
        raise NotImplementedError

    @scale_ratio.setter
    def scale_ratio(self, value):
        # type: (float) -> None
        """
        Manually set the scale ratio for the images being validated.
        """
        raise NotImplementedError

    @property
    def position_provider(self):
        """
        Sets position provider.
        """
        raise NotImplementedError

    @property
    def save_debug_screenshots(self):
        # type: () -> bool
        """True if screenshots saving enabled."""
        raise NotImplementedError

    @save_debug_screenshots.setter
    def save_debug_screenshots(self, save):
        # type: (bool) -> None
        """If True, will save all screenshots to local directory."""
        raise NotImplementedError

    @property
    def debug_screenshots_provider(self):
        raise NotImplementedError

    @property
    def debug_screenshots_path(self):
        # type: () -> Optional[Text]
        """The path where you save the debug screenshots."""
        raise NotImplementedError

    @debug_screenshots_path.setter
    def debug_screenshots_path(self, path_to_save):
        # type: (Text) -> None
        """The path where you want to save the debug screenshots."""
        raise NotImplementedError

    @property
    def debug_screenshots_prefix(self):
        # type: () -> Optional[Text]
        """The prefix for the screenshots' names."""
        raise NotImplementedError

    @debug_screenshots_prefix.setter
    def debug_screenshots_prefix(self, prefix):
        # type: (Text) -> None
        """The prefix for the screenshots' names."""
        raise NotImplementedError

    @position_provider.setter
    def position_provider(self, provider):
        """
        Gets position provider.
        """
        raise NotImplementedError

    @property
    def cut_provider(self):
        """
        Gets current cut provider
        """
        raise NotImplementedError

    @cut_provider.setter
    def cut_provider(self, cutprovider):
        """
        Manually set the the sizes to cut from an image before it's validated.
        """
        raise NotImplementedError

    @property
    def is_cut_provider_explicitly_set(self):
        # type: () -> bool
        """
        Gets is cut provider explicitly set.
        """
        raise NotImplementedError

    @property
    def agent_setup(self):
        # type: () -> Optional[Text]
        """
        Gets agent setup.
        """
        raise NotImplementedError

    @property
    def current_frame_position_provider(self):
        # type: () -> Optional[PositionProvider]
        raise NotImplementedError

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
    def driver(self):
        # type: () -> WebDriver
        return self._driver

    @property
    def send_dom(self):
        # type: () -> bool
        return self.configure.send_dom

    @send_dom.setter
    def send_dom(self, value):
        # type: (bool) -> None
        self.configure.send_dom = value

    def check_window(self, tag=None, match_timeout=-1, fully=True):
        # type: (Optional[Text], int, Optional[bool]) -> MatchResult
        """
        Takes a snapshot of the application under test and matches it with the expected
         output.

        :param tag: An optional tag to be associated with the snapshot.
        :param match_timeout:  The amount of time to retry matching (milliseconds)
        :param fully: Defines that the screenshot will contain the entire window.
        """
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

    def close_async(self):
        # type: () -> Optional[TestResults]
        raise NotImplementedError

    def abort_async(self):
        # type: () -> Optional[TestResults]
        raise NotImplementedError

    @deprecated.attribute("use `abort()` instead")
    def abort_if_not_closed(self):
        self.abort()


def _log_session_results_and_raise_exception(logger, raise_ex, results):
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
