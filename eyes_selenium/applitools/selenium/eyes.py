from __future__ import absolute_import

import typing

from applitools.common import EyesError, logger, MatchResult
from applitools.common.selenium import Configuration
from applitools.common.utils import argument_guard
from applitools.common.utils.general_utils import all_fields, proxy_to
from applitools.core.eyes_mixins import EyesConfigurationMixin
from applitools.selenium import ClassicRunner, eyes_selenium_utils

from .fluent import Target
from .selenium_eyes import SeleniumEyes
from .visual_grid import VisualGridEyes, VisualGridRunner
from .webdriver import EyesWebDriver

if typing.TYPE_CHECKING:
    from typing import Text, Optional, Union, List, Tuple
    from selenium.webdriver.remote.webelement import WebElement
    from applitools.common import TestResults, Region
    from applitools.common.utils.custom_types import (
        AnyWebDriver,
        ViewPort,
        FrameReference,
        AnyWebElement,
    )
    from applitools.core import (
        PositionProvider,
        FixedCutProvider,
        UnscaledFixedCutProvider,
        NullCutProvider,
    )
    from .frames import FrameChain
    from .fluent import SeleniumCheckSettings
    from .webelement import EyesWebElement


@proxy_to(
    "configure",
    all_fields(Configuration)
    + ["use_dom", "send_dom", "match_level", "ignore_displacements", "enable_patterns"],
)
class Eyes(EyesConfigurationMixin):
    _is_visual_grid_eyes = False  # type: bool
    _visual_grid_eyes = None  # type: VisualGridEyes
    _selenium_eyes = None  # type: SeleniumEyes
    _runner = None  # type: Optional[VisualGridRunner]
    _driver = None  # type: Optional[EyesWebDriver]
    _is_opened = False  # type: bool
    _config_cls = Configuration

    def __init__(self, runner=None):
        # type: (Optional[VisualGridRunner, ClassicRunner]) -> None
        super(Eyes, self).__init__()

        # backward compatibility with settings server_url
        if isinstance(runner, str):
            self.configure.server_url = runner
            runner = None

        if runner is None:
            self._selenium_eyes = SeleniumEyes(self, None)
        elif isinstance(runner, VisualGridRunner):
            self._runner = runner
            self._visual_grid_eyes = VisualGridEyes(self, runner)
            self._is_visual_grid_eyes = True
        elif isinstance(runner, ClassicRunner):
            self._runner = runner
            self._selenium_eyes = SeleniumEyes(self, runner)
            self._is_visual_grid_eyes = False
        else:
            raise ValueError("Wrong runner")

    def get_configuration(self):
        # type:() -> Configuration
        return super(Eyes, self).get_configuration()

    def set_configuration(self, configuration):
        # type:(Configuration) -> None
        return super(Eyes, self).set_configuration(configuration)

    @property
    def configure(self):
        # type:() -> Configuration
        return super(Eyes, self).configure

    @property
    def is_open(self):
        # type: () -> bool
        return self._is_opened

    @property
    def rotation(self):
        # type: () -> Optional[int]
        if self._selenium_eyes and self.driver:
            return self.driver.rotation
        return None

    @rotation.setter
    def rotation(self, rotation):
        # type: (Union[int,float]) -> None
        argument_guard.is_in(rotation, [int, float])
        if self._selenium_eyes and self.driver:
            self.driver.rotation = int(rotation)

    @property
    def base_agent_id(self):
        # type: () -> Text
        """
        Must return version of SDK. (e.g. selenium, visualgrid) in next format:
            "eyes.{package}.python/{lib_version}"
        """
        return self._current_eyes.base_agent_id

    @property
    def full_agent_id(self):
        # type: () -> Text
        """
        Gets the agent id, which identifies the current library using the SDK.

        """
        return self._current_eyes.full_agent_id

    @property
    def should_stitch_content(self):
        # type: () -> bool
        return self._current_eyes.should_stitch_content

    @property
    def original_fc(self):
        # type: () -> Optional[FrameChain]
        """ Gets original frame chain

        Before check() call we save original frame chain

        Returns:
            Frame chain saved before check() call
        """
        return self._current_eyes.original_fc

    @property
    def device_pixel_ratio(self):
        # type: () -> int
        """
        Gets device pixel ratio.

        :return The device pixel ratio, or if the DPR is not known yet or if it wasn't
        possible to extract it.
        """
        if not self._is_visual_grid_eyes:
            return self._selenium_eyes.device_pixel_ratio
        return 0

    @property
    def scale_ratio(self):
        # type: () -> float
        if not self._is_visual_grid_eyes:
            return self._selenium_eyes.scale_ratio
        return 0

    @scale_ratio.setter
    def scale_ratio(self, value):
        # type: (float) -> None
        """
        Manually set the scale ratio for the images being validated.
        """
        if not self._is_visual_grid_eyes:
            self._selenium_eyes.scale_ratio = value

    @property
    def position_provider(self):
        """
        Sets position provider.
        """
        if not self._is_visual_grid_eyes:
            return self._selenium_eyes.position_provider
        return None

    @property
    def _debug_screenshot_provided(self):
        # type: () -> bool
        """True if screenshots saving enabled."""
        if not self._is_visual_grid_eyes:
            return self._selenium_eyes._debug_screenshot_provided

    @_debug_screenshot_provided.setter
    def _debug_screenshot_provided(self, save):
        # type: (bool) -> None
        if not self._is_visual_grid_eyes:
            self._selenium_eyes._debug_screenshot_provided = save

    @position_provider.setter
    def position_provider(self, provider):
        # type: (PositionProvider) -> None
        """
        Gets position provider.
        """
        if not self._is_visual_grid_eyes:
            self._selenium_eyes.position_provider = provider

    @property
    def cut_provider(self):
        # type:()->Optional[Union[FixedCutProvider,UnscaledFixedCutProvider,NullCutProvider]]
        """
        Gets current cut provider
        """
        if not self._is_visual_grid_eyes:
            return self._selenium_eyes.cut_provider
        return None

    @cut_provider.setter
    def cut_provider(self, cutprovider):
        # type: (Union[FixedCutProvider,UnscaledFixedCutProvider,NullCutProvider])->None
        """
        Manually set the the sizes to cut from an image before it's validated.

        :param provider:
        :return:
        """
        if not self._is_visual_grid_eyes:
            self._selenium_eyes.cut_provider = cutprovider

    @property
    def is_cut_provider_explicitly_set(self):
        """
        Gets is cut provider explicitly set.
        """
        if not self._is_visual_grid_eyes:
            return self._selenium_eyes.is_cut_provider_explicitly_set
        return False

    @property
    def agent_setup(self):
        """
        Gets agent setup.
        """
        if not self._is_visual_grid_eyes:
            return self._selenium_eyes.agent_setup
        return None

    @property
    def current_frame_position_provider(self):
        # type: () -> Optional[PositionProvider]
        if not self._is_visual_grid_eyes:
            return self._selenium_eyes.current_frame_position_provider
        return None

    @staticmethod
    def get_viewport_size(driver):
        # type: (AnyWebDriver) -> ViewPort
        return eyes_selenium_utils.get_viewport_size_or_display_size(driver)

    @staticmethod
    def set_viewport_size(driver, size):
        # type: (AnyWebDriver, ViewPort) -> None
        assert driver is not None
        if size is None:
            raise ValueError("set_viewport_size require `size` parameter")
        eyes_selenium_utils.set_viewport_size(driver, size)

    def add_property(self, name, value):
        # type: (Text, Text) -> None
        """
        Associates a key/value pair with the test. This can be used later for filtering.
        :param name: (string) The property name.
        :param value: (string) The property value
        """
        self._current_eyes.add_property(name, value)

    def clear_properties(self):
        """
        Clears the list of custom properties.
        """
        self._current_eyes.clear_properties()

    def add_mouse_trigger_by_element(self, action, element):
        # type: (Text, AnyWebElement) -> None
        """
        Adds a mouse trigger.

        :param action: Mouse action (click, double click etc.)
        :param element: The element on which the action was performed.
        """
        if self.configure.is_disabled:
            logger.debug("add_mouse_trigger: Ignoring %s (disabled)" % action)
            return
        if not self._is_visual_grid_eyes:
            self._selenium_eyes.add_mouse_trigger_by_element(action, element)

    def add_text_trigger_by_element(self, element, text):
        # type: (AnyWebElement, Text) -> None
        """
        Adds a text trigger.

        :param element: The element to which the text was sent.
        :param text: The trigger's text.
        """
        if self.configure.is_disabled:
            logger.debug("add_text_trigger: Ignoring '%s' (disabled)" % text)
            return
        if not self._is_visual_grid_eyes:
            self._selenium_eyes.add_text_trigger_by_element(element, text)

    @property
    def driver(self):
        # type: () -> EyesWebDriver
        return self._driver

    @property
    def send_dom(self):
        # type: () -> bool
        if not self._is_visual_grid_eyes:
            return self.configure.send_dom
        return False

    @send_dom.setter
    def send_dom(self, value):
        # type: (bool) -> None
        if not self._is_visual_grid_eyes:
            self.configure.send_dom = value

    def check(self, name, check_settings):
        # type: (Text, SeleniumCheckSettings) -> MatchResult
        """
        Takes a snapshot and matches it with the expected output.

        :param name: The name of the tag.
        :param check_settings: target which area of the window to check.
        :return: The match results.
        """
        if self.configure.is_disabled:
            return MatchResult()
        if not self.is_open:
            self.abort()
            raise EyesError("you must call open() before checking")
        return self._current_eyes.check(name, check_settings)

    def check_window(self, tag=None, match_timeout=-1, fully=None):
        # type: (Optional[Text], int, Optional[bool]) -> MatchResult
        """
        Takes a snapshot of the application under test and matches it with the expected
         output.

        :param tag: An optional tag to be associated with the snapshot.
        :param match_timeout:  The amount of time to retry matching (milliseconds)
        :param fully: Defines that the screenshot will contain the entire window.
        :return: The match results.
        """
        logger.debug("check_window('%s')" % tag)
        return self.check(tag, Target.window().timeout(match_timeout).fully(fully))

    def check_frame(self, frame_reference, tag=None, match_timeout=-1):
        # type: (FrameReference, Optional[Text], int) -> MatchResult
        """
        Check frame.

        :param frame_reference: The name or id of the frame to check. (The same
                name/id as would be used in a call to driver.switch_to.frame()).
        :param tag: An optional tag to be associated with the match.
        :param match_timeout: The amount of time to retry matching. (Milliseconds)
        :return: The match results.
        """
        logger.debug("check_frame('%s')" % tag)
        return self.check(
            tag, Target.frame(frame_reference).fully().timeout(match_timeout)
        )

    def check_region(
        self,
        region,  # type: Union[Region,Text,List,Tuple,WebElement,EyesWebElement]
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
        :return: The match results.
        """
        logger.debug("check_region('%s')" % tag)
        return self.check(
            tag,
            Target.region(region).timeout(match_timeout).stitch_content(stitch_content),
        )

    def check_region_in_frame(
        self,
        frame_reference,  # type: FrameReference
        region,  # type: Union[Region,Text,List,Tuple,WebElement,EyesWebElement]
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
        :return: None
        """
        if self.configure.is_disabled:
            logger.info("check_region_in_frame_by_selector(): ignored (disabled)")
            return MatchResult()
        logger.debug("check_region_in_frame_by_selector('%s')" % tag)
        return self.check(
            tag,
            Target.region(region)
            .frame(frame_reference)
            .stitch_content(stitch_content)
            .timeout(match_timeout),
        )

    def open(
        self,
        driver,  # type: AnyWebDriver
        app_name=None,  # type: Optional[Text]
        test_name=None,  # type: Optional[Text]
        viewport_size=None,  # type: Optional[ViewPort]
    ):
        # type: (...) -> Optional[EyesWebDriver]
        """
        Starts a test.

        :param driver: The driver that controls the browser hosting the application
            under the test.
        :param app_name: The name of the application under test.
        :param test_name: The test name.
        :param viewport_size: The client's viewport size (i.e.,
            the visible part of the document's body) or None to allow any viewport size.
        :raise EyesError: If the session was already open.
        """
        if self.configure.is_disabled:
            logger.info("open(): ignored (disabled)")
            return
        if app_name:
            self.configure.app_name = app_name
        if test_name:
            self.configure.test_name = test_name
        if viewport_size:
            self.configure.viewport_size = viewport_size  # type: ignore
        self._init_driver(driver)
        result = self._current_eyes.open(self.driver)
        self._is_opened = True
        return result

    def close(self, raise_ex=True):
        # type: (bool) -> Optional[TestResults]
        """
        Ends the test.

        :param raise_ex: If true, an exception will be raised for failed/new tests.
        :return: The test results.
        """
        if self.configure.is_disabled:
            logger.info("close(): ignored (disabled)")
            return
        result = self._current_eyes.close(raise_ex)
        self._is_opened = False
        return result

    def close_async(self):
        if self.configure.is_disabled:
            logger.info("close_async(): ignored (disabled)")
            return
        if self._is_visual_grid_eyes:
            self._visual_grid_eyes.close_async()
        else:
            self._selenium_eyes.close(False)

    def abort(self):
        """
        If a test is running, aborts it. Otherwise, does nothing.
        """
        if self.configure.is_disabled:
            logger.info("abort(): ignored (disabled)")
            return
        self._current_eyes.abort()

    def abort_async(self):
        if self.configure.is_disabled:
            logger.info("abort_async(): ignored (disabled)")
            return
        if self._is_visual_grid_eyes:
            return self._visual_grid_eyes.abort_async()
        else:
            return self._selenium_eyes.abort()

    def abort_if_not_closed(self):
        logger.deprecation("Use `abort()` instead")
        self.abort()

    def _init_driver(self, driver):
        # type: (AnyWebDriver) -> None
        if isinstance(driver, EyesWebDriver):
            # If the driver is an EyesWebDriver (as might be the case when tests are ran
            # consecutively using the same driver object)
            self._driver = driver
        else:
            self._driver = EyesWebDriver(driver, self)

    @property
    def _current_eyes(self):
        # type: () -> Union[SeleniumEyes, VisualGridEyes]
        if self._is_visual_grid_eyes:
            return self._visual_grid_eyes
        else:
            return self._selenium_eyes

    @property
    def _original_scroll_position(self):
        if self._selenium_eyes:
            return self._selenium_eyes._original_scroll_position
        return None
