from __future__ import absolute_import

import typing

from applitools.common import SeleniumConfiguration, logger
from applitools.common.utils import argument_guard

from .fluent import Target
from .selenium_eyes import SeleniumEyes
from .visual_grid import VisualGridEyes, VisualGridRunner
from .webdriver import EyesWebDriver

if typing.TYPE_CHECKING:
    from typing import Text, Optional, Union, Callable, Any, List, Tuple
    from selenium.webdriver.remote.webelement import WebElement
    from applitools.common import MatchResult, TestResults, Region, SessionType
    from applitools.common.utils.custom_types import (
        AnyWebDriver,
        ViewPort,
        FrameReference,
    )
    from .fluent import SeleniumCheckSettings
    from .webelement import EyesWebElement


class Eyes(object):
    EYES_COMMON = [
        "base_agent_id",
        "is_debug_screenshot_provided",
        "abort_if_not_closed",
        "original_frame_chain",
        "close",
        "viewport_size",
        "stitch_content",
        "device_pixel_ratio",
        "scale_ratio",
        "position_provider",
        "_original_frame_chain",
        "full_agent_id",
        "agent_setup",
        "add_property",
        "is_opened",
        "clear_properties",
        "set_viewport_size_static",
        "get_viewport_size_static",
        "add_mouse_trigger_by_element",
        "add_text_trigger_by_element",
        "current_frame_position_provider",
    ]
    DELEGATE_TO_CONFIG = SeleniumConfiguration.all_fields()

    _is_visual_grid_eyes = False  # type: bool
    _visual_grid_eyes = None  # type: VisualGridEyes
    _selenium_eyes = None  # type: SeleniumEyes
    _runner = None  # type: Optional[VisualGridRunner]
    _driver = None  # type: Optional[EyesWebDriver]

    @property
    def configuration(self):
        return self._configuration

    @configuration.setter
    def configuration(self, new_conf):
        argument_guard.is_a(new_conf, SeleniumConfiguration)
        if self._configuration.api_key and not new_conf.api_key:
            new_conf.api_key = self._configuration.api_key
        if self._configuration.server_url and not new_conf.server_url:
            new_conf.server_url = self._configuration.server_url
        self._configuration = new_conf

    def __init__(self, runner=None):
        # type: (Optional[Any]) -> None
        self._configuration = SeleniumConfiguration()  # type: SeleniumConfiguration

        # backward compatibility with settings server_url
        if isinstance(runner, str):
            self.configuration.server_url = runner
            runner = None

        if runner is None:
            self._selenium_eyes = SeleniumEyes(self)
        elif isinstance(runner, VisualGridRunner):
            self._runner = runner
            self._visual_grid_eyes = VisualGridEyes(runner, self)
            self._is_visual_grid_eyes = True
        else:
            raise ValueError("Wrong runner")

    @property
    def driver(self):
        # type: () -> EyesWebDriver
        return self._driver

    @property
    def send_dom(self):
        # type: () -> bool
        if not self._is_visual_grid_eyes:
            return self.configuration.send_dom
        return False

    def check(self, name, check_settings):
        # type: (Text, SeleniumCheckSettings) -> MatchResult
        """
        Takes a snapshot and matches it with the expected output.

        :param name: The name of the tag.
        :param check_settings: target which area of the window to check.
        :return: The match results.
        """
        return self._current_eyes.check(name, check_settings)

    def check_window(
        self, tag=None, match_timeout=SeleniumConfiguration.DEFAULT_MATCH_TIMEOUT_MS
    ):
        # type: (Optional[Text], int) -> MatchResult
        """
        Takes a snapshot of the application under test and matches it with the expected output.

        :param tag: An optional tag to be associated with the snapshot.
        :param match_timeout:  The amount of time to retry matching (milliseconds)
        :return: The match results.
        """
        logger.debug("check_window('%s')" % tag)
        return self.check(tag, Target.window().timeout(match_timeout))

    def check_region(
        self,
        region,  # type: Union[Region,Text,List,Tuple,WebElement,EyesWebElement]
        tag=None,  # type: Optional[Text]
        match_timeout=SeleniumConfiguration.DEFAULT_MATCH_TIMEOUT_MS,  # type: int
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
        # TODO: remove this disable
        if self.configuration.is_disabled:
            logger.info("check_region_in_frame_by_selector(): ignored (disabled)")
            return MatchResult()
        logger.debug("check_region_in_frame_by_selector('%s')" % tag)
        return self.check(
            tag,
            Target.region(region, frame_reference)
            .stitch_content(stitch_content)
            .timeout(match_timeout),
        )

    def open(
        self,
        driver,  # type: AnyWebDriver
        app_name=None,  # type: Optional[Text]
        test_name=None,  # type: Optional[Text]
        viewport_size=None,  # type: Optional[ViewPort]
        session_type=None,  # type: Optional[SessionType]
    ):
        # type: (...) -> EyesWebDriver
        """
        Starts a test.

        :param driver: The driver that controls the browser hosting the application
            under the test.
        :param app_name: The name of the application under test.
        :param test_name: The test name.
        :param viewport_size: The client's viewport size (i.e.,
            the visible part of the document's body) or None to allow any viewport size.
        :param session_type: The type of test (e.g., Progression for timing tests)
             or Sequential by default.
        :return: An updated web driver
        :raise EyesError: If the session was already open.
        """
        if app_name:
            self.configuration.app_name = app_name
        if test_name:
            self.configuration.test_name = test_name
        if viewport_size:
            self.configuration.viewport_size = viewport_size  # type: ignore
        if session_type:
            self.configuration.session_type = session_type  # type: ignore

        self._init_driver(driver)
        return self._current_eyes.open(self.driver)

    def close(self, raise_ex=True):
        # type: (bool) -> Optional[TestResults]
        """
        Ends the test.

        :param raise_ex: If true, an exception will be raised for failed/new tests.
        :return: The test results.
        """
        return self._current_eyes.close(raise_ex)

    def close_async(self):
        if self._is_visual_grid_eyes:
            self._current_eyes.close_async()

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

    def __getattr__(self, name):
        # type: (str) -> Union[Callable, bool]
        if name in self.DELEGATE_TO_CONFIG:
            return getattr(self.configuration, name)
        if name in self.EYES_COMMON:
            return getattr(self._current_eyes, name)
        raise AttributeError("{} has not attr {}".format(self.__class__.__name__, name))

    def __setattr__(self, name, value):
        # type: (str, Any) -> None
        if name in self.DELEGATE_TO_CONFIG:
            setattr(self.configuration, name, value)
            return
        if name in self.EYES_COMMON:
            setattr(self._current_eyes, name, value)
        else:
            super(Eyes, self).__setattr__(name, value)
