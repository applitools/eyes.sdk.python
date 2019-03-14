import typing
from time import sleep

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

from applitools.common import (
    AppEnvironment,
    CoordinatesType,
    EyesError,
    MatchResult,
    RectangleSize,
    Region,
    TestFailedError,
    logger,
)
from applitools.common.geometry import EMPTY_REGION, Point
from applitools.common.utils import image_utils
from applitools.core import (
    NULL_REGION_PROVIDER,
    ContextBasedScaleProvider,
    EyesBase,
    FixedScaleProvider,
    MouseTrigger,
    NullScaleProvider,
    PositionProvider,
    RegionProvider,
    TextTrigger,
)
from applitools.core.capture import ImageProvider
from applitools.selenium.capture.eyes_webdriver_screenshot import (
    EyesWebDriverScreenshotFactory,
)
from applitools.selenium.capture.full_page_capture_algorithm import (
    FullPageCaptureAlgorithm,
)
from applitools.selenium.capture.image_providers import get_image_provider
from applitools.selenium.configuration import SeleniumConfiguration
from applitools.selenium.fluent import SeleniumCheckSettings
from applitools.selenium.region_compensation import (
    RegionPositionCompensation,
    get_region_position_compensation,
)

from . import eyes_selenium_utils, useragent
from .__version__ import __version__
from .capture import EyesWebDriverScreenshot, dom_capture
from .fluent import FrameLocator, Target
from .frames import FrameChain
from .positioning import (
    CSSTranslatePositionProvider,
    ElementPositionProvider,
    ScrollPositionProvider,
    StitchMode,
)
from .webdriver import EyesWebDriver
from .webelement import EyesWebElement

# noinspection PyProtectedMember

if typing.TYPE_CHECKING:
    from typing import Optional, Text
    from applitools.common.utils.custom_types import (
        AnyWebDriver,
        ViewPort,
        FrameReference,
        AnyWebElement,
    )
    from applitools.core import MatchWindowTask
    from applitools.core.scaling import ScaleProvider
    from .useragent import UserAgent
    from .frames import Frame
    from .webdriver import _EyesSwitchTo


class ScreenshotType(object):
    ENTIRE_ELEMENT_SCREENSHOT = "EntireElementScreenshot"
    REGION_OR_ELEMENT_SCREENSHOT = "RegionOrElementScreenshot"
    FULLPAGE_SCREENSHOT = "FullPageScreenshot"
    VIEWPORT_SCREENSHOT = "ViewportScreenshot"


class Eyes(EyesBase):
    """
    Applitools Selenium Eyes API for python.
    """

    _UNKNOWN_DEVICE_PIXEL_RATIO = 0
    _DEFAULT_DEVICE_PIXEL_RATIO = 1

    @staticmethod
    def set_viewport_size_static(driver, size=None, viewportsize=None):
        # type: (AnyWebDriver, Optional[ViewPort], Optional[ViewPort]) -> None
        assert driver is not None
        if size is None and viewportsize is None:
            raise ValueError("set_viewport_size_static require `size` parameter")
        if viewportsize:
            logger.deprecation("Use `size` parameter instead")
        eyes_selenium_utils.set_viewport_size(driver, size)

    @staticmethod
    def get_viewport_size_static(driver):
        # type: (AnyWebDriver) -> ViewPort
        return eyes_selenium_utils.get_viewport_size(driver)

    def __init__(self, server_url=None):
        super(Eyes, self).__init__(server_url)

        self._driver = None  # type: Optional[AnyWebDriver]
        self._match_window_task = None  # type: Optional[MatchWindowTask]
        self._screenshot_type = None  # type: Optional[str]  # ScreenshotType
        self._device_pixel_ratio = self._UNKNOWN_DEVICE_PIXEL_RATIO
        self._element_position_provider = (
            None
        )  # type: Optional[ElementPositionProvider]
        self.current_frame_position_provider = None  # type: Optional[PositionProvider]
        self._original_frame_chain = None  # type: Optional[FrameChain]
        self._scroll_root_element = None
        self._image_location = None
        self._check_frame_or_element = None  # type: bool
        self._effective_viewport = None  # type: Optional[Region]
        self._target_element = None
        self._screenshot_factory = (
            None
        )  # type: Optional[EyesWebDriverScreenshotFactory]
        self._user_agent = None  # type: Optional[UserAgent]
        self._image_provider = None  # type: Optional[ImageProvider]
        self._region_position_compensation = (
            None
        )  # type: Optional[RegionPositionCompensation]

    @property
    def original_frame_chain(self):
        # type: () -> FrameChain
        return self._original_frame_chain

    @property
    def wait_before_screenshots(self):
        return self._config.wait_before_screenshots

    @wait_before_screenshots.setter
    def wait_before_screenshots(self, value):
        self._config.wait_before_screenshots = value

    @property
    def _seconds_to_wait_screenshot(self):
        return self.wait_before_screenshots / 1000.0

    @property
    def hide_scrollbars(self):
        # type: () -> Text
        """
        Gets the stitch mode.

        :return: The stitch mode.
        """
        return self._config.hide_scrollbars

    @hide_scrollbars.setter
    def hide_scrollbars(self, hide):
        # type: (bool) -> None
        self._config.hide_scrollbars = hide

    @property
    def force_full_page_screenshot(self):
        # type: () -> bool
        """
        Gets the stitch mode.

        :return: The stitch mode.
        """
        return self._config.force_full_page_screenshot

    @force_full_page_screenshot.setter
    def force_full_page_screenshot(self, force):
        # type: (bool) -> None
        self._config.force_full_page_screenshot = force

    @property
    def stitch_mode(self):
        # type: () -> Text
        """
        Gets the stitch mode.

        :return: The stitch mode.
        """
        return self._config.stitch_mode

    @stitch_mode.setter
    def stitch_mode(self, stitch_mode):
        # type: (Text) -> None
        """
        Sets the stitch property - default is by scrolling.

        :param stitch_mode: The stitch mode to set - either scrolling or css.
        """
        self._config.stitch_mode = stitch_mode
        if stitch_mode == StitchMode.CSS:
            self._config.hide_scrollbars = True
            self._config.send_dom = True

    @property
    def base_agent_id(self):
        return "eyes.selenium.python/{version}".format(version=__version__)

    @property
    def driver(self):
        # type: () -> EyesWebDriver
        """
        Returns the current web driver.
        """
        return self._driver

    def get_screenshot(self):
        return self._get_screenshot()

    def _init_driver(self, driver):
        if isinstance(driver, EyesWebDriver):
            # If the driver is an EyesWebDriver (as might be the case when tests are ran
            # consecutively using the same driver object)
            self._driver = driver
        else:
            if not isinstance(driver, RemoteWebDriver):
                logger.info(
                    "WARNING: driver is not a RemoteWebDriver (class: {0})".format(
                        driver.__class__
                    )
                )
            self._driver = EyesWebDriver(driver, self)

    def open(self, driver, app_name, test_name, viewport_size=None):
        # type: (AnyWebDriver, Text, Text, Optional[ViewPort]) -> EyesWebDriver
        if self.is_disabled:
            logger.debug("open(): ignored (disabled)")
            return driver
        self._config.app_name = app_name
        self._config.test_name = test_name
        self._config.viewport_size = viewport_size

        self._init_driver(driver)
        self._screenshot_factory = EyesWebDriverScreenshotFactory(self.driver)
        self._ensure_viewport_size()

        self._open_base()

        ua_string = self._session_start_info.environment.inferred
        if ua_string:
            ua_string = ua_string.replace("useragent:", "")
            self._user_agent = useragent.parse_user_agent_string(ua_string)

        self._image_provider = get_image_provider(self._user_agent, self)
        self._region_position_compensation = get_region_position_compensation(
            self._user_agent, self
        )
        return self._driver

    def _get_scroll_root_element_from_(self, container=None):
        def get_root_html():
            return self.driver.find_element_by_tag_name("html")

        scroll_root_element = None
        if not self.driver.is_mobile_device():
            if container is None:
                scroll_root_element = get_root_html()
            else:
                if hasattr(container, "values"):
                    # check settings
                    container = container.values
                scroll_root_element = container.scroll_root_element
                if not scroll_root_element:
                    scroll_root_selector = container.scroll_root_selector
                    if scroll_root_selector:
                        scroll_root_element = self.driver.find_element_by_css_selector(
                            scroll_root_selector
                        )
                    else:
                        scroll_root_element = get_root_html()
        return scroll_root_element

    def _try_hide_scrollbars(self):
        # type: () -> Optional[FrameChain]
        if self.driver.is_mobile_device():
            return FrameChain()

        if self.hide_scrollbars or (
            self.stitch_mode == StitchMode.CSS and self._stitch_content
        ):
            original_fc = self.driver.frame_chain.clone()
            fc = self.driver.frame_chain.clone()

            if len(fc) > 0:
                frame = fc.peek  # type: Frame
                while len(fc) > 0:
                    logger.info("fc count = {}".format(len(fc)))
                    if self._stitch_content or len(fc) != len(original_fc):
                        if frame:
                            frame.hide_scrollbars(self.driver)
                        else:
                            logger.info(
                                "hiding scrollbars of element (1): {}".format(
                                    self._scroll_root_element
                                )
                            )
                            eyes_selenium_utils.set_overflow(
                                self.driver, "hidden", self._scroll_root_element
                            )
                    self.driver.switch_to.parent_frame()
                    fc.pop()
                    frame = fc.peek
            else:
                logger.info(
                    "hiding scrollbars of element (2): {}".format(
                        self._scroll_root_element
                    )
                )
                self._original_overflow = eyes_selenium_utils.set_overflow(
                    self.driver, "hidden", self._scroll_root_element
                )
            logger.info("switching back to original frame")
            self.driver.switch_to.frames(original_fc)
            logger.info("done hiding scrollbars.")
            return original_fc
        return None

    def _try_restore_scrollbars(self, frame_chain):
        if self.driver.is_mobile_device():
            return None
        if self.hide_scrollbars or (
            self.stitch_mode == StitchMode.CSS or self._stitch_content
        ):
            self.driver.switch_to.frames(frame_chain)
            original_fc = frame_chain.clone()
            fc = frame_chain.clone()
            if len(fc) > 0:
                while len(fc) > 0:
                    frame = fc.pop()
                    frame.return_to_original_overflow(self.driver)
                    origin_switch_to = eyes_selenium_utils.get_underlying_driver(
                        self.driver
                    ).switch_to
                    self.driver.switch_to.parent_frame_static(origin_switch_to, fc)
            else:
                logger.info(
                    "returning overflow of element to its original value: {}".format(
                        self._scroll_root_element
                    )
                )
                eyes_selenium_utils.set_overflow(
                    self.driver, self._original_overflow, self._scroll_root_element
                )
            self.driver.switch_to.frames(original_fc)
            logger.info("done restoring scrollbars.")
        else:
            logger.info("no need to restore scrollbars.")
        self.driver.frame_chain.clear()

    def check(self, name, check_settings):  # noqa: C901
        # type: (Text, SeleniumCheckSettings) -> MatchResult
        if name:
            check_settings = check_settings.with_name(name)
        else:
            name = check_settings.values.name

        logger.info("check('{}', check_settings) - begin".format(name))
        self._stitch_content = check_settings.values.stitch_content
        target_region = check_settings.values.target_region

        self.current_frame_position_provider = None
        self._original_frame_chain = self.driver.frame_chain.clone()

        if not eyes_selenium_utils.is_mobile_device(self._driver):
            logger.info("URL: {}".format(self._driver.current_url))

        switch_to = None  # type: _EyesSwitchTo
        if not self.driver.is_mobile_device():
            switch_to = self.driver.switch_to

        self._scroll_root_element = self._get_scroll_root_element_from_(check_settings)
        self.position_provider = self._create_position_provider(
            self._scroll_root_element
        )
        switched_to_frame_count = self._switch_to_frame(check_settings)
        # breakpoint()
        origin_fc = None
        result = None
        if target_region:
            logger.info("have target region")
            origin_fc = self._try_hide_scrollbars()
            target_region = target_region.clone()
            target_region.coordinates_type = CoordinatesType.CONTEXT_RELATIVE
            result = self._check_window_base(
                RegionProvider(target_region), name, False, check_settings
            )
        elif check_settings:
            target_element = self._get_element(check_settings)
            if target_element:
                origin_fc = self._try_hide_scrollbars()
                logger.info("have target element")
                self._target_element = target_element
                if self._stitch_content:
                    result = self._check_element(name, check_settings)
                else:
                    result = self._check_region(name, check_settings)
                self._target_element = None
            elif len(check_settings.values.frame_chain) > 0:
                logger.info("have frame chain")
                if self._stitch_content:
                    result = self._check_full_frame_or_element(name, check_settings)
                else:
                    result = self._check_frame_fluent(name, check_settings)
            else:
                logger.info("default case")
                if switch_to:
                    # required to prevent cut line on the last stitched part of the
                    # page on some browsers (like firefox).
                    switch_to.default_content()
                    self.current_frame_position_provider = self._create_position_provider(
                        self.driver.find_element_by_tag_name("html")
                    )
                result = self._check_window_base(
                    NULL_REGION_PROVIDER, name, False, check_settings
                )
            if switch_to:
                switch_to.frames(self._original_frame_chain)

        if result is None:
            result = MatchResult()

        while switched_to_frame_count > 0:
            switch_to.parent_frame()
            switched_to_frame_count -= 1
        if self.position_provider.states:
            self.position_provider.pop_state()
        if switch_to:
            switch_to.reset_scroll()
            if origin_fc:
                self._try_restore_scrollbars(origin_fc)

            self._try_switch_to_frames(
                self.driver, switch_to, self._original_frame_chain
            )
        self._stitch_content = False
        logger.info("check - done!")
        return result

    def _check_full_frame_or_element(self, name, check_settings):
        self._check_frame_or_element = True
        resutl = self._check_window_base(
            RegionProvider(self._get_full_frame_or_element_region),
            name,
            False,
            check_settings,
        )
        self._check_frame_or_element = False
        return resutl

    def _ensure_frame_visible(self):
        logger.info("scroll_root_element_: []".format(self._scroll_root_element))
        original_fc = self.driver.frame_chain.clone()
        fc = self.driver.frame_chain.clone()
        self.driver.execute_script("window.scrollTo(0,0);")
        origin_driver = eyes_selenium_utils.get_underlying_driver(self.driver)

        while len(fc) > 0:
            logger.debug("fc count: {}".format(fc.size))
            self.driver.switch_to.parent_frame_static(origin_driver.switch_to, fc)
            self.driver.execute_script("window.scrollTo(0,0);")
            prev_frame = fc.pop()
            frame = fc.peek
            scroll_root_element = None
            if fc.size == original_fc.size:
                logger.debug("PositionProvider: {}".format(self.position_provider))
                self.position_provider.push_state()
                scroll_root_element = self._scroll_root_element
            else:
                if frame:
                    scroll_root_element = frame.scroll_root_element
                if not scroll_root_element:
                    scroll_root_element = self.driver.find_element_by_tag_name("html")
            logger.debug("scroll_root_element {}".format(scroll_root_element))

            position_provider = self._get_element_position_provider(scroll_root_element)
            position_provider.set_position(prev_frame.location)
            reg = Region.from_location_size(Point.zero(), prev_frame.inner_size)
            self._effective_viewport.intersect(reg)
        self.driver.switch_to.frames(original_fc)
        return original_fc

    def _get_element_position_provider(self, scroll_root_element):
        # type: (EyesWebElement) -> PositionProvider
        position_provider = scroll_root_element.position_provider
        if not position_provider:
            position_provider = self._create_position_provider(scroll_root_element)
            scroll_root_element.position_provider = position_provider
        logger.debug("position provider: {}".format(position_provider))
        self.current_frame_position_provider = position_provider
        return position_provider

    def _get_full_frame_or_element_region(self):
        if self._check_frame_or_element:
            fc = self._ensure_frame_visible()
            # FIXME - Scaling should be handled in a single place instead
            scale_factory = self._update_scaling_params()
            screenshot_image = self._image_provider.get_image()
            scale_factory.update_scale_ratio(screenshot_image.width)
            self.driver.switch_to.frames(fc)
            screenshot = EyesWebDriverScreenshot.create_viewport(
                self.driver, screenshot_image
            )
            # TODO HERE
            logger.debug("replacing region_to_check")
            self._region_to_check = screenshot.frame_window
        return EMPTY_REGION

    def _check_frame_fluent(self, name, check_settings):
        fc = self.driver.frame_chain.clone()
        target_frame = fc.pop()
        self._target_element = target_frame.reference

        self.driver.switch_to.frames_do_scroll(fc)
        result = self._check_region(name, check_settings)
        self._target_element = None
        return result

    @staticmethod
    def _try_switch_to_frames(driver, switch_to, frames):
        if driver.is_mobile_device():
            return None
        try:
            switch_to.frames(frames)
        except WebDriverException as e:
            logger.warning(
                "Failed to switch to original frame chain! {}".format(str(e))
            )

    def _switch_to_parent_frame(self, frame_count):
        if frame_count > 0:
            self.driver.switch_to.parent_frame()
            return self._switch_to_parent_frame(frame_count - 1)

    def _switch_to_frame(self, check_settings):
        # type: (SeleniumCheckSettings) -> int
        if check_settings is None:
            return 0

        switched_to_frame_count = 0
        frame_chain = check_settings.values.frame_chain
        for frame_locator in frame_chain:
            if self._switch_to_frame_with_locator(frame_locator):
                switched_to_frame_count += 1
        return switched_to_frame_count

    def _switch_to_frame_with_locator(self, frame_locator):
        # type: (FrameLocator) -> bool
        # We don't want to track frames here
        switch_to = self.driver.switch_to
        if frame_locator.frame_index:
            switch_to.frame(frame_locator.frame_index)
            self._update_frame_scroll_root(frame_locator)
            return True
        if frame_locator.frame_name_or_id:
            switch_to.frame(frame_locator.frame_name_or_id)
            self._update_frame_scroll_root(frame_locator)
            return True
        if frame_locator.frame_element:
            switch_to.frame(frame_locator.frame_element)
            self._update_frame_scroll_root(frame_locator)
            return True
        if frame_locator.frame_selector:
            frame_element = self.driver.find_element_by_css_selector(
                frame_locator.frame_selector
            )
            if frame_element:
                switch_to.frame(frame_element)
                self._update_frame_scroll_root(frame_locator)
                return True
        return False

    def _update_frame_scroll_root(self, frame_locator):
        # type: (FrameLocator) -> None
        root_element = self._get_scroll_root_element_from_(frame_locator)
        frame = self.driver.frame_chain.peek
        # breakpoint()
        frame.scroll_root_element = root_element

    @property
    def scroll_root_element(self):
        if self._scroll_root_element is None:
            self._scroll_root_element = self.driver.find_element_by_tag_name("html")
        return self._scroll_root_element

    def check_window(self, tag=None, match_timeout=-1, target=None):
        # type: (Optional[Text], int, Optional[SeleniumCheckSettings]) -> MatchResult
        """
        Takes a snapshot from the browser using the web driver and matches
        it with the expected output.

        :param tag: Description of the visual validation checkpoint.
        :param match_timeout: Timeout for the visual validation checkpoint (
                              milliseconds).
        :return: None
        """
        logger.info("check_window('%s')" % tag)
        if target:
            logger.deprecation(
                "Use fluent interface with check_window is deprecated. "
                "Use `eyes.check()` instead"
            )
        check_settings = target
        if check_settings is None:
            check_settings = Target.window()
        return self.check(tag, check_settings.timeout(match_timeout))

    def check_region(
        self, region, tag=None, match_timeout=-1, target=None, stitch_content=False
    ):
        # type: (Region, Optional[Text], int, Optional[Target], bool) -> MatchResult
        """
        Takes a snapshot of the given region from the browser using the web driver
        and matches it with the expected output. If the current context is a frame,
        the region is offsetted relative to the frame.

        :param region: The region which will be visually validated. The coordinates are
                       relative to the viewport of the current frame.
        :param tag: Description of the visual validation checkpoint.
        :param match_timeout: Timeout for the visual validation checkpoint
                              (milliseconds).
        :return: None
        """
        logger.info("check_region([%s], '%s')" % (region, tag))
        if region.is_empty:
            raise EyesError("region cannot be empty!")
        if target or stitch_content:
            logger.deprecation(
                "Use fluent interface with check_region is deprecated. "
                "Use `eyes.check()` instead"
            )
        return self.check(
            tag,
            Target.region(region).timeout(match_timeout).stitch_content(stitch_content),
        )

    def check_region_by_element(
        self, element, tag=None, match_timeout=-1, target=None, stitch_content=False
    ):
        # type: (AnyWebElement, Optional[Text], int, Optional[Target], bool) -> MatchResult
        """
        Takes a snapshot of the region of the given element from the browser using
        the web driver and matches it with the expected output.

        :param element: The element which region will be visually validated.
        :param tag: Description of the visual validation checkpoint.
        :param match_timeout: Timeout for the visual validation checkpoint
                              (milliseconds).
        :param target: The target for the check_window call
        :return: None
        """
        logger.info("check_region_by_element('%s')" % tag)
        if target or stitch_content:
            logger.deprecation(
                "Use fluent interface with check_region_by_element is deprecated. "
                "Use `eyes.check()` instead"
            )
        result = self.check(
            tag,
            Target.region(element)
            .timeout(match_timeout)
            .stitch_content(stitch_content),
        )
        return result

    def check_region_by_selector(
        self, by, value, tag=None, match_timeout=-1, target=None, stitch_content=False
    ):
        # type: (Text, Text, Optional[Text], int, Optional[Target], bool) -> MatchResult
        """
        Takes a snapshot of the region of the element found by calling find_element
        (by, value) and matches it with the expected output.

        :param by: The way by which an element to be validated should be found
                   (e.g., By.ID).
        :param value: The value identifying the element using the "by" type.
        :param tag: Description of the visual validation checkpoint.
        :param match_timeout: Timeout for the visual validation checkpoint
                              (milliseconds).
        :param target: The target for the check_window call
        :return: None
        """
        logger.debug("calling 'check_region_by_selector'...")
        # hack: prevent stale element exception by saving viewport value
        # before catching element
        self.check_region_by_element(
            self._driver.find_element(by, value),
            tag,
            match_timeout,
            target,
            stitch_content,
        )

    def check_region_in_frame_by_selector(
        self,
        frame_reference,  # type: FrameReference
        by,  # type: Text
        value,  # type: Text
        tag=None,  # type: Optional[Text]
        match_timeout=-1,  # type: int
        target=None,  # type: Optional[Target]
        stitch_content=False,  # type: bool
    ):
        # type: (...) -> MatchResult
        """
        Checks a region within a frame, and returns to the current frame.

        :param frame_reference: A reference to the frame in which the region
                                should be checked.
        :param by: The way by which an element to be validated should be found (By.ID).
        :param value: The value identifying the element using the "by" type.
        :param tag: Description of the visual validation checkpoint.
        :param match_timeout: Timeout for the visual validation checkpoint
                              (milliseconds).
        :param target: The target for the check_window call
        :return: None
        """
        # TODO: remove this disable
        if self.is_disabled:
            logger.info("check_region_in_frame_by_selector(): ignored (disabled)")
            return
        if target or stitch_content:
            logger.deprecation(
                "Use fluent interface with check_region_by_element is deprecated. "
                "Use `eyes.check()` instead"
            )
        logger.info("check_region_in_frame_by_selector('%s')" % tag)
        return self.check(
            tag,
            Target.region((by, value), frame_reference)
            .stitch_content(stitch_content)
            .timeout(match_timeout),
        )

    def add_mouse_trigger_by_element(self, action, element):
        # type: (Text, AnyWebElement) -> None
        """
        Adds a mouse trigger.

        :param action: Mouse action (click, double click etc.)
        :param element: The element on which the action was performed.
        """
        if self.is_disabled:
            logger.debug("add_mouse_trigger: Ignoring %s (disabled)" % action)
            return
        # Triggers are activated on the last checked window.
        if self._last_screenshot is None:
            logger.debug("add_mouse_trigger: Ignoring %s (no screenshot)" % action)
            return
        if not self._driver.frame_chain == self._last_screenshot.frame_chain:
            logger.debug("add_mouse_trigger: Ignoring %s (different frame)" % action)
            return
        control = self._last_screenshot.get_intersected_region_by_element(element)
        # Making sure the trigger is within the last screenshot bounds
        if control.is_empty:
            logger.debug("add_mouse_trigger: Ignoring %s (out of bounds)" % action)
            return
        cursor = control.middle_offset
        trigger = MouseTrigger(action, control, cursor)
        self._user_inputs.append(trigger)
        logger.info("add_mouse_trigger: Added %s" % trigger)

    def add_text_trigger_by_element(self, element, text):
        # type: (AnyWebElement, Text) -> None
        """
        Adds a text trigger.

        :param element: The element to which the text was sent.
        :param text: The trigger's text.
        """
        if self.is_disabled:
            logger.debug("add_text_trigger: Ignoring '%s' (disabled)" % text)
            return
        # Triggers are activated on the last checked window.
        if self._last_screenshot is None:
            logger.debug("add_text_trigger: Ignoring '%s' (no screenshot)" % text)
            return
        if not self._driver.frame_chain == self._last_screenshot.frame_chain:
            logger.debug("add_text_trigger: Ignoring %s (different frame)" % text)
            return
        control = self._last_screenshot.get_intersected_region_by_element(element)
        # Making sure the trigger is within the last screenshot bounds
        if control.is_empty:
            logger.debug("add_text_trigger: Ignoring %s (out of bounds)" % text)
            return
        trigger = TextTrigger(control, text)
        self._user_inputs.append(trigger)
        logger.info("add_text_trigger: Added %s" % trigger)

    def _obtain_screenshot_type(
        self,
        is_element,
        inside_a_frame,
        stitch_content,
        force_fullpage,
        is_region=False,
    ):
        # type:(bool, bool, bool, bool, bool) -> str
        if stitch_content or force_fullpage:
            if is_element and not stitch_content:
                return ScreenshotType.REGION_OR_ELEMENT_SCREENSHOT

            if not inside_a_frame:
                if (force_fullpage and not stitch_content) or (
                    stitch_content and not is_element
                ):
                    return ScreenshotType.FULLPAGE_SCREENSHOT

            if inside_a_frame or stitch_content:
                return ScreenshotType.ENTIRE_ELEMENT_SCREENSHOT

        else:
            if is_region or (is_element and not stitch_content):
                return ScreenshotType.REGION_OR_ELEMENT_SCREENSHOT

            if not stitch_content and not force_fullpage:
                return ScreenshotType.VIEWPORT_SCREENSHOT

        return ScreenshotType.VIEWPORT_SCREENSHOT

    def _get_viewport_size(self):
        return self.get_viewport_size_static(self._driver)

    def _ensure_viewport_size(self):
        if self._config.viewport_size is None:
            self._config.viewport_size = self.driver.get_default_content_viewport_size()

    def _set_viewport_size(self, size):
        """
        Use this method only if you made a previous call to `open`.
        """
        # if self.viewport_size:
        #     logger.info("Ignored (viewport size given explicitly)")
        #     return None
        if not self.driver.is_mobile_device():
            original_frame = self.driver.frame_chain.clone()
            self.driver.switch_to.default_content()

            try:
                self.set_viewport_size_static(self._driver, size)
                self._effective_viewport = Region(
                    0,
                    0,
                    width=size["width"],
                    height=size["height"],
                    coordinates_type=CoordinatesType.SCREENSHOT_AS_IS,
                )
            except Exception as e:
                raise TestFailedError("Failed to set the viewport size", e)
            finally:
                # Just in case the user catches this error
                self.driver.switch_to.frames(original_frame)
        self.viewport_size = RectangleSize(size["width"], size["height"])

    def _ensure_configuration(self):
        if self._config is None:
            self._config = SeleniumConfiguration()

    @property
    def _environment(self):
        os = self.host_os
        # If no host OS was set, check for mobile OS.
        if os is None:
            logger.info("No OS set, checking for mobile OS...")
            # Since in Python Appium driver is the same for Android and iOS,
            # we need to use the desired capabilities to figure this out.
            if eyes_selenium_utils.is_mobile_device(self._driver):
                platform_name = self._driver.platform_name
                logger.info(platform_name + " detected")
                platform_version = self._driver.platform_version
                if platform_version is not None:
                    # Notice that Python's "split" function's +limit+ is the the
                    # maximum splits performed whereas in Ruby it is the maximum
                    # number of elements in the result (which is why they are set
                    # differently).
                    major_version = platform_version.split(".", 1)[0]
                    os = platform_name + " " + major_version
                else:
                    os = platform_name
                logger.info("Setting OS: " + os)
            else:
                logger.info("No mobile OS detected.")
        app_env = AppEnvironment(
            os,
            hosting_app=self._config.host_app,
            display_size=self.viewport_size,
            inferred=self._inferred_environment,
        )
        return app_env

    @property
    def _title(self):
        if self._should_get_title:
            # noinspection PyBroadException
            try:
                return self._driver.title
            except Exception:
                self._should_get_title = (
                    False
                )  # Couldn't get _title, return empty string.
        return ""

    @property
    def _inferred_environment(self):
        # type: () -> Optional[Text]
        try:
            user_agent = self._driver.execute_script("return navigator.userAgent")
        except WebDriverException:
            user_agent = None
        if user_agent:
            return "useragent:%s" % user_agent
        return None

    def _update_scaling_params(self):
        # type: () -> Optional[ScaleProvider]
        if (
            self._device_pixel_ratio != self._UNKNOWN_DEVICE_PIXEL_RATIO
            or not isinstance(self._scale_provider, NullScaleProvider)
        ):
            logger.debug("Device pixel ratio was already changed")
            return self._scale_provider

        logger.info("Trying to extract device pixel ratio...")
        try:
            device_pixel_ratio = eyes_selenium_utils.get_device_pixel_ratio(
                self._driver
            )
        except Exception as e:
            logger.info(
                "Failed to extract device pixel ratio! Using default. Error %s " % e
            )
            device_pixel_ratio = self._DEFAULT_DEVICE_PIXEL_RATIO
        logger.info("Device pixel ratio: {}".format(device_pixel_ratio))

        logger.info("Setting scale provider...")
        try:
            scale_provider = ContextBasedScaleProvider(
                top_level_context_entire_size=self._driver.get_entire_page_size(),
                viewport_size=self.viewport_size,
                device_pixel_ratio=device_pixel_ratio,
                # always False as in Java version
                is_mobile_device=False,
            )  # type: ScaleProvider
        except Exception:
            # This can happen in Appium for example.
            logger.info("Failed to set ContextBasedScaleProvider.")
            logger.info("Using FixedScaleProvider instead...")
            scale_provider = FixedScaleProvider(1 / device_pixel_ratio)
        logger.info("Done!")
        return scale_provider

    def _try_capture_dom(self):
        try:
            dom_json = dom_capture.get_full_window_dom(self._driver)
            return dom_json
        except Exception as e:
            logger.warning(
                "Exception raising during capturing DOM Json. Passing...\n "
                "Got next error: {}".format(str(e))
            )
            return None

    def _get_region(self, check_settings):
        target_element = self._get_element(check_settings)
        target_region = check_settings.values.target_region
        if target_region:
            return target_region
        if target_element:
            return self._get_element_region(target_element)

    def _get_element(self, check_settings):
        # type: (SeleniumCheckSettings) -> EyesWebElement
        target_element = check_settings.values.target_element
        target_selector = check_settings.values.target_selector
        if not target_element and target_selector:
            target_element = self._driver.find_element_by_css_selector(target_selector)
        if target_element and not isinstance(target_element, EyesWebElement):
            target_element = EyesWebElement(target_element, self.driver)
        return target_element

    def _mark_element_for_layout_rca(self, pos_provider):
        # TODO: Update method
        pass

    def _create_full_page_capture_algorithm(self, scale_provider, position_provider):
        scroll_root_element = self.get_current_frame_scroll_root_element()
        origin_provider = ScrollPositionProvider(self.driver, scroll_root_element)
        return FullPageCaptureAlgorithm(
            self.wait_before_screenshots,
            self._debug_screenshot_provider,
            self._screenshot_factory,
            origin_provider,
            scale_provider,
            self._cut_provider,
            self.stitching_overlap,
            self._image_provider,
            self._region_position_compensation,
            position_provider,
        )

    def _try_hide_caret(self):
        if self._config.hide_caret:
            try:
                self.driver.execute_script(
                    "var activeElement = document.activeElement; activeElement "
                    "&& activeElement.blur(); return activeElement;"
                )
            except WebDriverException as e:
                logger.warning("Cannot hide caret! \n{}".format(e))

    def _get_screenshot(self):
        self._screenshot_type = self._obtain_screenshot_type(
            is_element=self._check_frame_or_element,
            inside_a_frame=bool(self._original_frame_chain),
            stitch_content=self._stitch_content,
            force_fullpage=self.force_full_page_screenshot,
        )
        switch_to = self.driver.switch_to
        if switch_to:
            switch_to.frames(self._original_frame_chain)

        position_provider = self.position_provider
        if position_provider and self.driver.is_mobile_device():
            position_provider.push_state()
        # breakpoint()
        original_fc = self.driver.frame_chain.clone()
        if original_fc.size > 0:
            original_frame_position = original_fc.default_content_scroll_position
        else:
            original_frame_position = Point.zero()

        self._try_hide_caret()

        if switch_to:
            switch_to.frames(original_fc)

        scale_provider = self._update_scaling_params()

        algo = self._create_full_page_capture_algorithm(
            scale_provider, self.position_provider
        )
        if self._screenshot_type == ScreenshotType.ENTIRE_ELEMENT_SCREENSHOT:
            self._last_screenshot = self._entire_element_screenshot(
                algo, original_frame_position
            )

        elif self._screenshot_type == ScreenshotType.FULLPAGE_SCREENSHOT:
            self._last_screenshot = self._full_page_screenshot(algo)

        elif self._screenshot_type == ScreenshotType.VIEWPORT_SCREENSHOT:
            self._last_screenshot = self._viewport_screenshot(scale_provider)

        else:
            raise EyesError("No proper ScreenshotType obtained")
        return self._last_screenshot

    def _entire_element_screenshot(self, algo, original_frame_position):
        # type: (FullPageCaptureAlgorithm, Point) -> EyesWebDriverScreenshot
        logger.info("Entire element screenshot requested")

        elem_position_provider = self._element_position_provider
        if elem_position_provider is None:
            scroll_root_element = self.driver.find_element_by_tag_name("html")
            elem_position_provider = self._get_element_position_provider(
                scroll_root_element
            )
        self._mark_element_for_layout_rca(elem_position_provider)

        image = algo.get_stitched_region(
            self._region_to_check, None, self._element_position_provider
        )
        return EyesWebDriverScreenshot.create_entire_frame(
            self._driver, image, original_frame_position
        )

    # def _region_or_screenshot(self, scale_provider):
    # #     type: # (ScaleProvider) -> EyesWebDriverScreenshot
    #     logger.info("Not entire element screenshot requested")
    #     screenshot = self._viewport_screenshot(scale_provider)
    #     region = screenshot.get_element_region_in_frame_viewport(self._region_to_check)
    #     screenshot = screenshot.get_sub_screenshot_by_region(region)
    #     return screenshot

    def _full_page_screenshot(self, algo):
        # type: (FullPageCaptureAlgorithm) -> EyesWebDriverScreenshot
        logger.info("Full page screenshot requested")
        original_fc = self.driver.frame_chain.clone()
        if original_fc.size > 0:
            original_frame_position = original_fc.default_content_scroll_position
        else:
            original_frame_position = Point.zero()
        image = algo.get_stitched_region(EMPTY_REGION, None, self.position_provider)
        return EyesWebDriverScreenshot.create_entire_frame(
            self._driver, image, original_frame_position
        )

    def _viewport_screenshot(self, scale_provider):
        # type: (ScaleProvider) -> EyesWebDriverScreenshot
        logger.info("Viewport screenshot requested")

        sleep(self._seconds_to_wait_screenshot)
        image = self._image_provider.get_image()

        scale_provider.update_scale_ratio(image.width)
        pixel_ratio = 1 / scale_provider.scale_ratio
        if pixel_ratio != 1.0:
            image = image_utils.scale_image(image, 1.0 / pixel_ratio)

        return EyesWebDriverScreenshot.create_viewport(self._driver, image)

    def _ensure_element_visible(self, element):
        # TODO: Need to implement
        pass

    def get_current_frame_scroll_root_element(self):
        fc = self.driver.frame_chain.clone()
        cur_frame = fc.peek
        scrool_root_element = None
        if cur_frame:
            scrool_root_element = cur_frame.scroll_root_element
        if scrool_root_element is None and not self.driver.is_mobile_device():
            scrool_root_element = self.driver.find_element_by_tag_name("html")
        return scrool_root_element

    def _create_position_provider(self, scroll_root_element):
        stitch_mode = self.stitch_mode
        logger.info(
            "initializing position provider. stitch_mode: {}".format(stitch_mode)
        )
        if stitch_mode == StitchMode.Scroll:
            return ScrollPositionProvider(self.driver, scroll_root_element)
        elif stitch_mode == StitchMode.CSS:
            return CSSTranslatePositionProvider(self.driver, scroll_root_element)

    def _check_element(self, name, check_settings):
        element = self._target_element  # type: EyesWebElement
        self._region_to_check = None
        scroll_root_element = self.get_current_frame_scroll_root_element()
        position_provider = self._create_position_provider(scroll_root_element)
        position_provider.push_state()

        self._ensure_element_visible(element)
        original_overflow = None
        pl = element.location
        result = None
        try:
            self._check_frame_or_element = True
            display_style = element.get_computed_style("display")

            if self.hide_scrollbars:
                original_overflow = element.get_overflow()
                element.set_overflow("hidden")

            size_and_borders = element.size_and_borders
            border_widths = size_and_borders.borders
            element_size = size_and_borders.size
            if display_style != "inline" and (
                element_size["height"] <= self._effective_viewport["height"]
                and element_size["width"] <= self._effective_viewport["width"]
            ):
                self._element_position_provider = ElementPositionProvider(
                    self.driver, element
                )
            else:
                self._element_position_provider = None

            element_region = Region(
                pl["x"] + border_widths["left"],
                pl["y"] + border_widths["top"],
                element_size["width"],
                element_size["height"],
                coordinates_type=CoordinatesType.SCREENSHOT_AS_IS,
            )
            self._region_to_check = element_region

            if not self._effective_viewport.is_size_empty:
                self._region_to_check.intersect(self._effective_viewport)

            result = self._check_window_base(
                NULL_REGION_PROVIDER, name, False, check_settings
            )
        except Exception as e:
            logger.warning(str(e))
            raise e
        finally:
            if original_overflow:
                element.set_overflow(original_overflow)
            self._check_frame_or_element = False
            position_provider.pop_state()
            self._region_to_check = None
            self._element_position_provider = None
        return result

    def _check_region(self, name, check_settings):
        location = self._target_element.location
        size = self._target_element.size
        rp = RegionProvider(
            Region(
                location["x"],
                location["y"],
                size["width"],
                size["height"],
                coordinates_type=CoordinatesType.CONTEXT_RELATIVE,
            )
        )
        result = self._check_window_base(rp, name, False, check_settings)
        return result
