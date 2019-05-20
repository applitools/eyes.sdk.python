import contextlib
import typing
from time import sleep

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

from applitools.common import (
    AppEnvironment,
    CoordinatesType,
    MatchResult,
    RectangleSize,
    Region,
    logger,
)
from applitools.common.config import SeleniumConfiguration, StitchMode
from applitools.common.geometry import EMPTY_REGION, Point
from applitools.common.utils import image_utils
from applitools.core import (
    NULL_REGION_PROVIDER,
    ContextBasedScaleProvider,
    EyesBase,
    FixedScaleProvider,
    ImageProvider,
    MouseTrigger,
    NullScaleProvider,
    PositionProvider,
    RegionProvider,
    TextTrigger,
)
from applitools.selenium.capture.eyes_webdriver_screenshot import (
    EyesWebDriverScreenshotFactory,
)
from applitools.selenium.capture.full_page_capture_algorithm import (
    FullPageCaptureAlgorithm,
)
from applitools.selenium.capture.image_providers import get_image_provider
from applitools.selenium.region_compensation import (
    RegionPositionCompensation,
    get_region_position_compensation,
)

from . import eyes_selenium_utils, useragent
from .__version__ import __version__
from .capture import EyesWebDriverScreenshot, dom_capture
from .fluent import Target
from .frames import FrameChain
from .positioning import (
    CSSTranslatePositionProvider,
    ElementPositionProvider,
    ScrollPositionProvider,
)
from .useragent import BrowserNames, UserAgent
from .webdriver import EyesWebDriver
from .webelement import EyesWebElement

if typing.TYPE_CHECKING:
    from typing import Optional, Text, Generator
    from applitools.common.utils.custom_types import (
        AnyWebDriver,
        ViewPort,
        AnyWebElement,
    )
    from applitools.core import MatchWindowTask, ScaleProvider
    from .frames import Frame
    from .fluent import SeleniumCheckSettings
    from .eyes import Eyes


class ScreenshotType(object):
    ENTIRE_ELEMENT_SCREENSHOT = "EntireElementScreenshot"
    REGION_OR_ELEMENT_SCREENSHOT = "RegionOrElementScreenshot"
    FULLPAGE_SCREENSHOT = "FullPageScreenshot"
    VIEWPORT_SCREENSHOT = "ViewportScreenshot"


class SeleniumEyes(EyesBase):
    """
    Applitools Selenium SeleniumEyes API for python.
    """

    _UNKNOWN_DEVICE_PIXEL_RATIO = 0
    _DEFAULT_DEVICE_PIXEL_RATIO = 1
    _region_to_check = None  # type: Optional[Region]
    _driver = None  # type: Optional[AnyWebDriver]
    _match_window_task = None  # type: Optional[MatchWindowTask]
    _element_position_provider = None  # type: Optional[ElementPositionProvider]
    _check_frame_or_element = None  # type: bool
    _original_frame_chain = None  # type: Optional[FrameChain]
    _scroll_root_element = None
    _effective_viewport = None  # type: Optional[Region]
    _target_element = None
    _screenshot_factory = None  # type: Optional[EyesWebDriverScreenshotFactory]
    _user_agent = None  # type: Optional[UserAgent]
    _image_provider = None  # type: Optional[ImageProvider]
    _region_position_compensation = None  # type: Optional[RegionPositionCompensation]

    current_frame_position_provider = None  # type: Optional[PositionProvider]

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

    def __init__(self, config):
        # type: (Eyes) -> None
        super(SeleniumEyes, self).__init__()

        self._config_provider = config
        self._do_not_get_title = False
        self._device_pixel_ratio = self._UNKNOWN_DEVICE_PIXEL_RATIO

        self._stitch_content = False  # type: bool

    @property
    def configuration(self):
        # type: () -> SeleniumConfiguration
        return self._config_provider.configuration

    @property
    def original_frame_chain(self):
        # type: () -> FrameChain
        return self._original_frame_chain

    @property
    def stitch_content(self):
        # type: () -> bool
        return self._stitch_content

    @property
    def device_pixel_ratio(self):
        # type: () -> int
        return self._device_pixel_ratio

    @property
    def should_scrollbars_be_hidden(self):
        # type: () -> bool
        return self.configuration.hide_scrollbars or (
            self.configuration.stitch_mode == StitchMode.CSS and self._stitch_content
        )

    @property
    def base_agent_id(self):
        # type: () -> str
        return "eyes.selenium.python/{version}".format(version=__version__)

    @property
    def driver(self):
        # type: () -> EyesWebDriver
        """
        Returns the current web driver.
        """
        return self._driver

    def open(self, driver):
        # type: (AnyWebDriver) -> EyesWebDriver
        if self.configuration.is_disabled:
            logger.debug("open(): ignored (disabled)")
            return driver
        self._driver = driver
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

    def _try_hide_scrollbars(self, frame=None):
        # type: (Optional[Frame]) -> bool
        if self.should_scrollbars_be_hidden:
            if frame:
                frame.hide_scrollbars(self.driver)
            else:
                logger.debug(
                    "hiding scrollbars of element (1): {}".format(
                        self.scroll_root_element
                    )
                )
                self._original_overflow = eyes_selenium_utils.hide_scrollbars(
                    self.driver, self.scroll_root_element
                )
            logger.debug("done hiding scrollbars.")
            return True
        return False

    def _try_restore_scrollbars(self, frame=None):
        # type: (Optional[Frame]) -> bool
        if self.should_scrollbars_be_hidden:
            if frame:
                frame.return_to_original_overflow(self.driver)
            else:
                logger.debug(
                    "returning overflow of element to its original value: {}".format(
                        self.scroll_root_element
                    )
                )
                eyes_selenium_utils.return_to_original_overflow(
                    self.driver, self.scroll_root_element, self._original_overflow
                )
            logger.debug("done restoring scrollbars.")
            return True
        return False

    def check(self, name, check_settings=None):
        # type: (Text, Optional[SeleniumCheckSettings]) -> MatchResult
        if check_settings is None:
            check_settings = Target.window()

        if name:
            check_settings = check_settings.with_name(name)
        else:
            name = check_settings.values.name

        logger.info("check('{}', check_settings) - begin".format(name))

        # Set up required settings
        self._stitch_content = check_settings.values.stitch_content
        self._scroll_root_element = eyes_selenium_utils.scroll_root_element_from(
            self.driver, check_settings
        )
        self._position_provider = self._create_position_provider(
            self._scroll_root_element
        )
        self._original_frame_chain = self.driver.frame_chain.clone()

        if not self.driver.is_mobile_device():
            # hide scrollbar for main window
            self._try_hide_scrollbars()

            logger.info("URL: {}".format(self._driver.current_url))
            with self._switch_to_frame(check_settings):
                result = self._check_result_flow(name, check_settings)

            # restore scrollbar of main window
            self._scroll_root_element = eyes_selenium_utils.scroll_root_element_from(
                self.driver, check_settings
            )
            self._try_restore_scrollbars()
        else:
            result = self._check_result_flow(name, check_settings)

        self._stitch_content = False
        self._scroll_root_element = None
        self._position_provider = None
        self._original_frame_chain = None
        logger.debug("check - done!")
        return result

    def _check_result_flow(self, name, check_settings):
        target_region = check_settings.values.target_region
        result = None
        if target_region:
            logger.debug("have target region")
            target_region = target_region.clone()
            target_region.coordinates_type = CoordinatesType.CONTEXT_RELATIVE
            result = self._check_window_base(
                RegionProvider(target_region), name, False, check_settings
            )
        elif check_settings:
            target_element = self._element_from(check_settings)
            if target_element:
                logger.debug("have target element")
                self._target_element = target_element
                if self._stitch_content:
                    result = self._check_element(name, check_settings)
                else:
                    result = self._check_region(name, check_settings)
                self._target_element = None
            elif len(check_settings.values.frame_chain) > 0:
                logger.debug("have frame chain")
                if self._stitch_content:
                    result = self._check_full_frame_or_element(name, check_settings)
                else:
                    result = self._check_frame_fluent(name, check_settings)
            else:
                logger.debug("default case")
                if not self.driver.is_mobile_device():
                    # required to prevent cut line on the last stitched part of the
                    # page on some browsers (like firefox).
                    self.driver.switch_to.default_content()
                    self.current_frame_position_provider = self._create_position_provider(
                        self.driver.find_element_by_tag_name("html")
                    )
                result = self._check_window_base(
                    NULL_REGION_PROVIDER, name, False, check_settings
                )
        if result is None:
            result = MatchResult()
        return result

    def _check_full_frame_or_element(self, name, check_settings):
        self._check_frame_or_element = True
        resutl = self._check_window_base(
            RegionProvider(self._full_frame_or_element_region),
            name,
            False,
            check_settings,
        )
        self._check_frame_or_element = False
        self._region_to_check = None
        return resutl

    def _ensure_frame_visible(self):
        logger.debug("scroll_root_element_: []".format(self._scroll_root_element))
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

            position_provider = self._element_position_provider_from(
                scroll_root_element
            )
            position_provider.set_position(prev_frame.location)
            reg = Region.from_location_size(Point.zero(), prev_frame.inner_size)
            self._effective_viewport.intersect(reg)
        self.driver.switch_to.frames(original_fc)
        return original_fc

    def _element_position_provider_from(self, scroll_root_element):
        # type: (EyesWebElement) -> PositionProvider
        position_provider = scroll_root_element.position_provider
        if not position_provider:
            position_provider = self._create_position_provider(scroll_root_element)
            scroll_root_element.position_provider = position_provider
        logger.debug("position provider: {}".format(position_provider))
        self.current_frame_position_provider = position_provider
        return position_provider

    def _full_frame_or_element_region(self):
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

    @contextlib.contextmanager
    def _switch_to_frame(self, check_settings):
        # type: (SeleniumCheckSettings) -> Generator
        switched_to_frame_count = 0
        # TODO: refactor frames storing
        frames = {}
        frame_chain = check_settings.values.frame_chain
        for frame_locator in frame_chain:
            self.driver.switch_to.frame(frame_locator)
            root_element = eyes_selenium_utils.scroll_root_element_from(
                self.driver, frame_locator
            )
            cur_frame = self._driver.frame_chain.peek
            cur_frame.scroll_root_element = root_element
            self._try_hide_scrollbars(cur_frame)
            frames[switched_to_frame_count] = cur_frame
            switched_to_frame_count += 1

        yield

        while switched_to_frame_count > 0:
            cur_frame = frames.get(switched_to_frame_count - 1)
            if cur_frame:
                self._try_restore_scrollbars(cur_frame)
            self.driver.switch_to.parent_frame()
            self.driver.switch_to.reset_scroll()
            switched_to_frame_count -= 1

    @property
    def scroll_root_element(self):
        if self._scroll_root_element is None:
            self._scroll_root_element = self.driver.find_element_by_tag_name("html")
        return self._scroll_root_element

    def add_mouse_trigger_by_element(self, action, element):
        # type: (Text, AnyWebElement) -> None
        """
        Adds a mouse trigger.

        :param action: Mouse action (click, double click etc.)
        :param element: The element on which the action was performed.
        """
        if self.configuration.is_disabled:
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
        logger.debug("add_mouse_trigger: Added %s" % trigger)

    def add_text_trigger_by_element(self, element, text):
        # type: (AnyWebElement, Text) -> None
        """
        Adds a text trigger.

        :param element: The element to which the text was sent.
        :param text: The trigger's text.
        """
        if self.configuration.is_disabled:
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
        logger.debug("add_text_trigger: Added %s" % trigger)

    def _get_viewport_size(self):
        size = self.configuration.viewport_size
        if size is None:
            size = self.get_viewport_size_static(self._driver)
        return size

    def _ensure_viewport_size(self):
        if self.configuration.viewport_size is None:
            self.configuration.viewport_size = (
                self.driver.get_default_content_viewport_size()
            )

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
            finally:
                # Just in case the user catches this error
                self.driver.switch_to.frames(original_frame)
        self.configuration.viewport_size = RectangleSize(size["width"], size["height"])

    @property
    def _environment(self):
        os = self.configuration.host_os
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
            hosting_app=self.configuration.host_app,
            display_size=self.configuration.viewport_size,
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

        logger.debug("Trying to extract device pixel ratio...")
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

        logger.debug("Setting scale provider...")
        try:
            scale_provider = ContextBasedScaleProvider(
                top_level_context_entire_size=self._driver.get_entire_page_size(),
                viewport_size=self.configuration.viewport_size,
                device_pixel_ratio=device_pixel_ratio,
                is_mobile_device=False,  # TODO: fix scaling for mobile
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

    def _region_from(self, check_settings):
        target_element = self._element_from(check_settings)
        target_region = check_settings.values.target_region
        if target_region:
            return target_region
        if target_element:
            return self._get_element_region(target_element)

    def _element_from(self, check_settings):
        # type: (SeleniumCheckSettings) -> EyesWebElement
        target_element = check_settings.values.target_element
        target_selector = check_settings.values.target_selector
        if not target_element and target_selector:
            target_element = self._driver.find_element_by_css_selector(target_selector)
        if target_element and not isinstance(target_element, EyesWebElement):
            target_element = EyesWebElement(target_element, self.driver)
        return target_element

    def _create_full_page_capture_algorithm(self, scale_provider):
        scroll_root_element = eyes_selenium_utils.current_frame_scroll_root_element(
            self.driver
        )
        origin_provider = ScrollPositionProvider(self.driver, scroll_root_element)
        return FullPageCaptureAlgorithm(
            self.configuration.wait_before_screenshots,
            self._debug_screenshot_provider,
            self._screenshot_factory,
            origin_provider,
            scale_provider,
            self._cut_provider,
            self.configuration.stitching_overlap,
            self._image_provider,
            self._region_position_compensation,
        )

    def _try_hide_caret(self):
        if self.configuration.hide_caret:
            try:
                self.driver.execute_script(
                    "var activeElement = document.activeElement; activeElement "
                    "&& activeElement.blur(); return activeElement;"
                )
            except WebDriverException as e:
                logger.warning("Cannot hide caret! \n{}".format(e))

    def _get_screenshot(self):
        with self._driver.switch_to.frames_and_back(self._original_frame_chain):
            if self.position_provider and not self.driver.is_mobile_device():
                self.position_provider.push_state()

        self._try_hide_caret()

        scale_provider = self._update_scaling_params()

        if self._check_frame_or_element:
            self._last_screenshot = self._entire_element_screenshot(scale_provider)
        elif self.configuration.force_full_page_screenshot or self._stitch_content:
            self._last_screenshot = self._full_page_screenshot(scale_provider)
        else:
            self._last_screenshot = self._viewport_screenshot(scale_provider)

        with self._driver.switch_to.frames_and_back(self._original_frame_chain):
            if self.position_provider and not self.driver.is_mobile_device():
                self.position_provider.pop_state()

        return self._last_screenshot

    def _entire_element_screenshot(self, scale_provider):
        # type: (ScaleProvider) -> EyesWebDriverScreenshot
        logger.info("Entire element screenshot requested")

        elem_position_provider = self._element_position_provider
        if elem_position_provider is None:
            scroll_root_element = self.driver.find_element_by_tag_name("html")
            elem_position_provider = self._element_position_provider_from(
                scroll_root_element
            )

        # TODO: Should be moved in proper place???
        if self.driver.frame_chain:
            if (
                self._user_agent.browser == BrowserNames.Firefox
                and self._user_agent.browser_major_version < 60
            ) or self._user_agent.browser in (
                BrowserNames.Chrome,
                BrowserNames.HeadlessChrome,
                BrowserNames.Safari,
                BrowserNames.Edge,
                BrowserNames.IE,
            ):
                self._region_to_check.left += int(
                    self._driver.frame_chain.peek.location.x
                )
        algo = self._create_full_page_capture_algorithm(scale_provider)

        image = algo.get_stitched_region(
            self._region_to_check, None, elem_position_provider
        )
        return EyesWebDriverScreenshot.create_entire_frame(
            self._driver, image, RectangleSize.from_(image)
        )

    def _full_page_screenshot(self, scale_provider):
        # type: (ScaleProvider) -> EyesWebDriverScreenshot
        logger.info("Full page screenshot requested")
        original_fc = self.driver.frame_chain.clone()
        if original_fc.size > 0:
            original_frame_position = original_fc.default_content_scroll_position
        else:
            original_frame_position = Point.zero()

        with self.driver.switch_to.frames_and_back(self._original_frame_chain):
            location = self.scroll_root_element.location
            size_and_borders = self.scroll_root_element.size_and_borders
            region = Region(
                location["x"] + size_and_borders.borders["left"],
                location["y"] + size_and_borders.borders["top"],
                size_and_borders.size["width"],
                size_and_borders.size["height"],
            )

            algo = self._create_full_page_capture_algorithm(scale_provider)
            image = algo.get_stitched_region(region, None, self.position_provider)

        return EyesWebDriverScreenshot.create_full_page(
            self._driver, image, original_frame_position
        )

    def _viewport_screenshot(self, scale_provider):
        # type: (ScaleProvider) -> EyesWebDriverScreenshot
        logger.info("Viewport screenshot requested")
        self._ensure_element_visible(self._target_element)

        sleep(self.configuration.wait_before_screenshots / 1000.0)
        image = self._image_provider.get_image()
        self._debug_screenshot_provider.save(image, "original")
        scale_provider.update_scale_ratio(image.width)
        pixel_ratio = 1 / scale_provider.scale_ratio
        if pixel_ratio != 1.0:
            image = image_utils.scale_image(image, 1.0 / pixel_ratio)

        return EyesWebDriverScreenshot.create_viewport(self._driver, image)

    def _get_viewport_scroll_bounds(self):
        switch_to = self.driver.switch_to
        with switch_to.frames_and_back(self.original_frame_chain):
            try:
                location = ScrollPositionProvider.get_current_position_static(
                    self.driver, self.scroll_root_element
                )
            except WebDriverException as e:
                logger.warning(str(e))
                logger.info("Assuming position is 0,0")
                location = Point(0, 0)
        viewport_bounds = Region.from_location_size(location, self._get_viewport_size())
        return viewport_bounds

    def _ensure_element_visible(self, element):
        if self._target_element is None:
            # No element? we must be checking the window.
            return None
        if self.driver.is_mobile_device():
            logger.debug("NATIVE context identified, skipping 'ensure element visible'")
            return None

        original_fc = self.driver.frame_chain.clone()
        switch_to = self.driver.switch_to
        eyes_element = EyesWebElement(element, self.driver)
        element_bounds = eyes_element.bounds

        current_frame_offset = original_fc.current_frame_offset
        element_bounds.offset(current_frame_offset.x, current_frame_offset.y)
        viewport_bounds = self._get_viewport_scroll_bounds()
        logger.info(
            "viewport_bounds: {}; element_bounds: {}".format(
                viewport_bounds, element_bounds
            )
        )
        if not element_bounds.contains(viewport_bounds):
            self._ensure_frame_visible()
            element_location = Point.from_(element.location)
            if len(original_fc) > 0 and element is not original_fc.peek.reference:
                switch_to.frames(original_fc)
                scroll_root_element = self.driver.find_element_by_tag_name("html")
            else:
                scroll_root_element = self.scroll_root_element
            position_provider = self._element_position_provider_from(
                scroll_root_element
            )
            position_provider.set_position(element_location)

    def _create_position_provider(self, scroll_root_element):
        stitch_mode = self.configuration.stitch_mode
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
        scroll_root_element = eyes_selenium_utils.current_frame_scroll_root_element(
            self.driver
        )
        pos_provider = self._create_position_provider(scroll_root_element)
        result = None
        with pos_provider:
            self._ensure_element_visible(element)
            pl = element.location
            try:
                self._check_frame_or_element = True
                display_style = element.get_computed_style("display")

                if self.configuration.hide_scrollbars:
                    # FIXME bug if trying to hide
                    element.hide_scrollbars()

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
                logger.exception(e)
                raise e
            finally:
                if self.configuration.hide_scrollbars:
                    element.return_to_original_overflow()
                self._check_frame_or_element = False
                self._region_to_check = None
                self._element_position_provider = None
        return result

    def _check_region(self, name, check_settings):
        def get_region():
            location = self._target_element.location
            size = self._target_element.size
            return Region(
                location["x"],
                location["y"],
                size["width"],
                size["height"],
                coordinates_type=CoordinatesType.CONTEXT_RELATIVE,
            )

        result = self._check_window_base(
            RegionProvider(get_region), name, False, check_settings
        )
        return result
