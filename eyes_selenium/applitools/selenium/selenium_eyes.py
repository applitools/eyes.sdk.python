import contextlib
import typing

from selenium.common.exceptions import WebDriverException

from applitools.common import (
    AppEnvironment,
    CoordinatesType,
    MatchResult,
    RectangleSize,
    Region,
    TestResults,
    logger,
)
from applitools.common.geometry import Point
from applitools.common.selenium import StitchMode
from applitools.common.utils import argument_guard, datetime_utils, image_utils
from applitools.core import (
    NULL_REGION_PROVIDER,
    ContextBasedScaleProvider,
    EyesBase,
    FixedScaleProvider,
    ImageProvider,
    MouseTrigger,
    NullCutProvider,
    NullScaleProvider,
    PositionProvider,
    RegionProvider,
    TextTrigger,
)
from applitools.core.feature import Feature

from . import eyes_selenium_utils
from .__version__ import __version__
from .capture import EyesWebDriverScreenshot, dom_capture
from .capture.eyes_webdriver_screenshot import EyesWebDriverScreenshotFactory
from .capture.full_page_capture_algorithm import FullPageCaptureAlgorithm
from .capture.image_providers import get_image_provider
from .capture.screenshot_utils import cut_to_viewport_size_if_required
from .classic_runner import ClassicRunner
from .frames import FrameChain
from .positioning import (
    ElementPositionProvider,
    ScrollPositionProvider,
    create_position_provider,
)
from .region_compensation import (
    RegionPositionCompensation,
    get_region_position_compensation,
)
from .useragent import BrowserNames
from .webdriver import EyesWebDriver
from .webelement import EyesWebElement, adapt_element

if typing.TYPE_CHECKING:
    from typing import Generator, Optional, Text

    from applitools.common import ScaleProvider
    from applitools.common.utils.custom_types import (
        AnyWebDriver,
        AnyWebElement,
        ViewPort,
    )
    from applitools.core import MatchWindowTask, PositionMemento

    from .eyes import Eyes
    from .fluent import SeleniumCheckSettings
    from .frames import Frame


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
    _original_fc = None  # type: Optional[FrameChain]
    _scroll_root_element = None  # type: Optional[EyesWebElement]
    _effective_viewport = None  # type: Optional[Region]
    _target_element = None  # type: Optional[EyesWebElement]
    _screenshot_factory = None  # type: Optional[EyesWebDriverScreenshotFactory]
    _image_provider = None  # type: Optional[ImageProvider]
    _region_position_compensation = None  # type: Optional[RegionPositionCompensation]
    _switched_to_frame_count = 0  # int
    _full_region_to_check = None  # type: Optional[Region]
    _position_memento = None  # type: Optional[PositionMemento]
    _is_check_region = None  # type: Optional[bool]
    _current_frame_position_provider = None  # type: Optional[PositionProvider]
    _runner = None  # type: Optional[ClassicRunner]

    @staticmethod
    def set_viewport_size(driver, size=None, viewportsize=None):
        # type: (AnyWebDriver, Optional[ViewPort], Optional[ViewPort]) -> None
        assert driver is not None
        if size is None and viewportsize is None:
            raise ValueError("set_viewport_size require `size` parameter")
        if viewportsize:
            logger.deprecation("Use `size` parameter instead")
        eyes_selenium_utils.set_viewport_size(driver, size)

    @staticmethod
    def get_viewport_size(driver):
        # type: (AnyWebDriver) -> ViewPort
        argument_guard.not_none(driver)
        return eyes_selenium_utils.get_viewport_size_or_display_size(driver)

    def __init__(self, config_provider, runner):
        # type: (Eyes, Optional[ClassicRunner]) -> None
        super(SeleniumEyes, self).__init__()

        self._config_provider = config_provider
        self._do_not_get_title = False
        self._device_pixel_ratio = self._UNKNOWN_DEVICE_PIXEL_RATIO
        self._stitch_content = False  # type: bool
        self._runner = runner if runner else ClassicRunner()

    @property
    def original_fc(self):
        # type: () -> FrameChain
        return self._original_fc

    @property
    def should_stitch_content(self):
        # type: () -> bool
        return self._stitch_content

    @property
    def device_pixel_ratio(self):
        # type: () -> int
        return self._device_pixel_ratio

    @property
    def should_scrollbars_be_hidden(self):
        # type: () -> bool
        return self.configure.hide_scrollbars or (
            self.configure.stitch_mode == StitchMode.CSS and self._stitch_content
        )

    @property
    def base_agent_id(self):
        # type: () -> Text
        return "eyes.selenium.python/{version}".format(version=__version__)

    @property
    def driver(self):
        # type: () -> EyesWebDriver
        """
        Returns the current web driver.
        """
        return self._driver

    def open(self, driver, skip_start_session=False):
        # type: (AnyWebDriver, bool) -> EyesWebDriver
        self._driver = driver
        self._screenshot_factory = EyesWebDriverScreenshotFactory(self.driver)
        self._ensure_viewport_size()

        if skip_start_session:
            self._server_connector.update_config(
                self.get_configuration(), self.full_agent_id
            )
            self._init_providers()
        else:
            self._open_base()
        self._image_provider = get_image_provider(self._driver.user_agent, self)
        self._region_position_compensation = get_region_position_compensation(
            self._driver.user_agent, self
        )
        return self._driver

    def _try_hide_scrollbars(self, frame=None):
        # type: (Optional[Frame]) -> bool
        if self._driver.is_mobile_platform:
            return False
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
        if self._driver.is_mobile_platform:
            return False
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

    def _create_position_provider(self, scroll_root_element):

        return create_position_provider(
            self.driver,
            self.configure.stitch_mode,
            scroll_root_element,
            self._target_element,
        )

    def check(self, check_settings):
        # type: (Text, SeleniumCheckSettings) -> MatchResult
        source = eyes_selenium_utils.get_check_source(self.driver)
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

        self._original_fc = self.driver.frame_chain.clone()

        if not self.driver.is_mobile_app:
            self._position_memento = ScrollPositionProvider(
                self.driver, self.scroll_root_element
            ).get_state()

            # hide scrollbar for main window
            self._try_hide_scrollbars()

            logger.info("Current URL: {}".format(self._driver.current_url))
            with self._switch_to_frame(check_settings):
                result = self._check_result_flow(name, check_settings, source)

            # restore scrollbar of main window
            self._scroll_root_element = eyes_selenium_utils.scroll_root_element_from(
                self.driver, check_settings
            )
            self._try_restore_scrollbars()
        else:
            result = self._check_result_flow(name, check_settings, source)

        self._stitch_content = False
        self._scroll_root_element = None
        if self._position_memento:
            ScrollPositionProvider(self.driver, self.scroll_root_element).restore_state(
                self._position_memento
            )

        if not self.driver.is_mobile_app:
            self.driver.switch_to.frames(self._original_fc)
        self._position_provider = None
        self._current_frame_position_provider = None
        self._position_memento = None
        self._original_fc = None
        logger.debug("check - done!")
        return result

    def close(self, raise_ex=True):
        # type: (bool) -> Optional[TestResults]
        results = super(SeleniumEyes, self).close(raise_ex)
        if self._runner:
            self._runner.aggregate_result(results)
        self._screenshot_factory = None
        return results

    def _check_result_flow(self, name, check_settings, source):
        target_region = check_settings.values.target_region
        result = None
        if target_region and self._switched_to_frame_count == 0:
            logger.debug("have target region")
            target_region = target_region.clone()
            target_region.coordinates_type = CoordinatesType.CONTEXT_RELATIVE
            result = self._check_window_base(
                RegionProvider(target_region), name, False, check_settings, source
            )
        elif check_settings:
            target_element = self._element_from(check_settings)
            total_frames = len(check_settings.values.frame_chain)
            if self.configure.is_feature_activated(
                Feature.TARGET_WINDOW_CAPTURES_SELECTED_FRAME
            ):
                total_frames += self.driver.frame_chain.size
            if target_element:
                logger.debug("have target element")
                self._target_element = target_element
                if self._stitch_content:
                    result = self._check_element(name, check_settings, source)
                else:
                    result = self._check_region(name, check_settings, source)
                self._target_element = None
            elif total_frames > 0:
                logger.debug("have frame chain")
                if self._stitch_content:
                    result = self._check_full_frame_or_element(
                        name, check_settings, source
                    )
                else:
                    result = self._check_frame_fluent(name, check_settings, source)
            else:
                logger.debug("default case")
                if not self.driver.is_mobile_app:
                    # required to prevent cut line on the last stitched part of the
                    # page on some browsers (like firefox).
                    self.driver.switch_to.default_content()
                    self._current_frame_position_provider = (
                        self._create_position_provider(
                            self.driver.find_element_by_tag_name("html")
                        )
                    )
                result = self._check_window_base(
                    NULL_REGION_PROVIDER,
                    name,
                    False,
                    check_settings,
                    source,
                )
        if result is None:
            result = MatchResult()
        return result

    @property
    def current_frame_position_provider(self):
        if self._current_frame_position_provider:
            return self._current_frame_position_provider
        else:
            return self.position_provider

    def _check_full_frame_or_element(self, name, check_settings, source):
        self._check_frame_or_element = True

        def full_frame_or_element_region(check_settings):
            logger.debug(
                "check_frame_or_element: {}".format(self._check_frame_or_element)
            )
            if self._check_frame_or_element:
                fc = self._ensure_frame_visible()
                # FIXME - Scaling should be handled in a single place instead
                scale_factory = self.update_scaling_params()
                screenshot_image = self._image_provider.get_image()
                scale_factory.update_scale_ratio(screenshot_image.width)
                self.driver.switch_to.frames(fc)
                screenshot = EyesWebDriverScreenshot.create_viewport(
                    self.driver, screenshot_image
                )
                # TODO HERE
                logger.debug("replacing region_to_check")
                self._region_to_check = screenshot.frame_window
                self._full_region_to_check = Region.EMPTY()

            target_region = check_settings.values.target_region
            if target_region is None:
                target_region = Region.EMPTY()
            return target_region

        result = self._check_window_base(
            RegionProvider(lambda: full_frame_or_element_region(check_settings)),
            name,
            False,
            check_settings,
            source,
        )
        self._check_frame_or_element = False
        self._region_to_check = None
        return result

    def _check_frame_fluent(self, name, check_settings, source):
        fc = self.driver.frame_chain.clone()
        target_frame = fc.pop()
        self._target_element = target_frame.reference

        self.driver.switch_to.frames_do_scroll(fc)
        result = self._check_region(name, check_settings, source)
        self._target_element = None
        return result

    def _check_element(self, name, check_settings, source):
        element = self._target_element  # type: EyesWebElement

        scroll_root_element = eyes_selenium_utils.curr_frame_scroll_root_element(
            self.driver, self._scroll_root_element
        )
        pos_provider = self._create_position_provider(scroll_root_element)

        self._region_to_check = Region.EMPTY()
        self._full_region_to_check = Region.EMPTY()

        result = None
        with eyes_selenium_utils.get_and_restore_state(pos_provider):
            with self._ensure_element_visible(element):
                pl = element.location
                try:
                    self._check_frame_or_element = True
                    display_style = element.get_computed_style("display")

                    if self.configure.hide_scrollbars:
                        element.hide_scrollbars()

                    size_and_borders = element.size_and_borders
                    border_widths = size_and_borders.borders
                    element_size = size_and_borders.size

                    use_entire_size = False
                    if display_style != "inline" and (
                        element_size["height"] <= self._effective_viewport["height"]
                        and element_size["width"] <= self._effective_viewport["width"]
                    ):
                        self._element_position_provider = ElementPositionProvider(
                            self.driver, element
                        )
                        use_entire_size = True
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

                    if use_entire_size:
                        self._full_region_to_check = Region.from_(
                            element_region.location,
                            self._element_position_provider.get_entire_size(),
                        )
                    else:
                        self._full_region_to_check = Region(
                            left=element_region.left,
                            top=element_region.top,
                            width=element_region.width,
                            height=element_region.height,
                        )

                    if not self._effective_viewport.is_size_empty:
                        self._region_to_check = self._region_to_check.intersect(
                            self._effective_viewport
                        )

                    result = self._check_window_base(
                        NULL_REGION_PROVIDER,
                        name,
                        False,
                        check_settings,
                        source,
                    )
                except Exception as e:
                    logger.exception(e)
                    raise e
                finally:
                    if self.configure.hide_scrollbars:
                        element.return_to_original_overflow()
                    self._check_frame_or_element = False
                    self._region_to_check = None
                    self._element_position_provider = None
                    self._full_region_to_check = None
                    self._effective_viewport = None
        return result

    def _check_region(self, name, check_settings, source):
        self._is_check_region = True

        def get_region():
            rect = check_settings.values.target_region
            if rect is None:
                if self.driver.is_mobile_platform:
                    bounds = self._target_element.rect
                else:
                    bounds = self._target_element.bounding_client_rect
                region = Region(
                    bounds["x"],
                    bounds["y"],
                    bounds["width"],
                    bounds["height"],
                    coordinates_type=CoordinatesType.CONTEXT_RELATIVE,
                )
            else:
                s = self._target_element.size_and_borders.size
                b = self._target_element.size_and_borders.borders
                p = Point.from_(self._target_element.location)
                p = p.offset(b["left"], b["top"])

                x = p.x + rect.left
                y = p.y + rect.top
                w = min(p.x + s["width"], rect.right) - x
                h = min(p.y + s["height"], rect.bottom) - y
                region = Region(x, y, w, h, CoordinatesType.CONTEXT_RELATIVE)
            return region

        result = self._check_window_base(
            RegionProvider(get_region),
            name,
            False,
            check_settings,
            source,
        )
        self._is_check_region = False
        return result

    def _ensure_frame_visible(self):
        logger.debug("scroll_root_element_: {}".format(self._scroll_root_element))
        current_fc = self.driver.frame_chain.clone()
        if not current_fc:
            # if no frames no point to go below
            return current_fc
        fc = self.driver.frame_chain.clone()
        self.driver.execute_script("window.scrollTo(0,0);")
        origin_driver = eyes_selenium_utils.get_underlying_driver(self.driver)

        while len(fc) > 0:
            logger.debug("fc count: {}".format(fc.size))
            self.driver.switch_to.parent_frame_static(origin_driver.switch_to, fc)
            self.driver.execute_script("window.scrollTo(0,0);")
            child_frame = fc.pop()
            parent_frame = fc.peek
            scroll_root_element = None
            if fc.size == self._original_fc.size:
                logger.debug("PositionProvider: {}".format(self.position_provider))
                self._position_memento = self.position_provider.get_state()
                scroll_root_element = self._scroll_root_element
            else:
                if parent_frame:
                    scroll_root_element = parent_frame.scroll_root_element
                if not scroll_root_element:
                    scroll_root_element = self.driver.find_element_by_tag_name("html")
            logger.debug("scroll_root_element {}".format(scroll_root_element))

            position_provider = self._element_position_provider_from(
                scroll_root_element
            )
            position_provider.set_position(child_frame.location)
            reg = Region.from_(Point.ZERO(), child_frame.inner_size)
            self._effective_viewport = self._effective_viewport.intersect(reg)
        self.driver.switch_to.frames(current_fc)
        return current_fc

    def _element_position_provider_from(self, scroll_root_element):
        # type: (EyesWebElement) -> PositionProvider
        position_provider = scroll_root_element.position_provider
        if not position_provider:
            position_provider = self._create_position_provider(scroll_root_element)
            scroll_root_element.position_provider = position_provider
        logger.debug("position provider: {}".format(position_provider))
        self._current_frame_position_provider = position_provider
        return position_provider

    @contextlib.contextmanager
    def _switch_to_frame(self, check_settings):
        # type: (SeleniumCheckSettings) -> Generator
        self._switched_to_frame_count = 0
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
            frames[self._switched_to_frame_count] = cur_frame
            self._switched_to_frame_count += 1

        yield

        while self._switched_to_frame_count > 0:
            cur_frame = frames.get(self._switched_to_frame_count - 1)
            if cur_frame:
                self._try_restore_scrollbars(cur_frame)
            self.driver.switch_to.parent_frame()
            self.driver.switch_to.reset_scroll()
            self._switched_to_frame_count -= 1

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
        # Triggers are activated on the last checked window.
        if self._last_screenshot is None:
            logger.debug("add_mouse_trigger: Ignoring %s (no screenshot)" % action)
            return
        if self._driver.frame_chain != self._last_screenshot.frame_chain:
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
        size = self.configure.viewport_size
        if size is None:
            size = self.driver.get_default_content_viewport_size()
        return size

    def _ensure_viewport_size(self):
        if self.configure.viewport_size is None:
            self.configure.viewport_size = (
                self.driver.get_default_content_viewport_size()
            )

    def _set_viewport_size(self, size):
        """
        Use this method only if you made a previous call to `open`.
        """
        # if self.viewport_size:
        #     logger.info("Ignored (viewport size given explicitly)")
        #     return None

        if not self.driver.is_mobile_platform:
            original_frame = self.driver.frame_chain.clone()
            self.driver.switch_to.default_content()

            try:
                self.set_viewport_size(self._driver, size)
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
        self.configure.viewport_size = RectangleSize(size["width"], size["height"])

    @property
    def _environment(self):
        os = self.configure.host_os

        device_info = (
            self._driver.desired_capabilities.get("deviceName", "")
            if self.driver.is_mobile_platform
            else "Desktop"
        )

        # If no host OS was set, check for mobile OS
        if os is None:
            logger.info("No OS set, checking for mobile OS...")
            if self._driver.is_mobile_app:
                os = self.driver.user_agent.os_name_with_major_version
                logger.info("Setting OS: " + os)
            else:
                logger.info("No mobile app detected. Using inferred environment")
        app_env = AppEnvironment(
            os,
            hosting_app=self.configure.host_app,
            display_size=self.configure.viewport_size,
            inferred=self._inferred_environment,
            device_info=device_info,
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
                    False  # Couldn't get _title, return empty string.
                )
        return ""

    @property
    def _inferred_environment(self):
        # type: () -> Optional[Text]
        user_agent = self._driver.user_agent
        if user_agent.origin_ua_string:
            return "useragent:%s" % user_agent.origin_ua_string
        return None

    def update_scaling_params(self):
        # type: () -> Optional[ScaleProvider]
        if (
            self.device_pixel_ratio != self._UNKNOWN_DEVICE_PIXEL_RATIO
            or not isinstance(self._scale_provider, NullScaleProvider)
        ):
            logger.debug("Device pixel ratio was already changed")
            return self._scale_provider

        logger.debug("Trying to extract device pixel ratio...")

        try:
            if (
                self.driver.is_mobile_app
                and Feature.SCALE_MOBILE_APP in self.configure.features
            ):
                device_pixel_ratio = self.driver.session["pixelRatio"]
            else:
                device_pixel_ratio = self._driver.execute_script(
                    "return window.devicePixelRatio;"
                )
        except Exception as e:
            logger.info(
                "Failed to extract device pixel ratio! Using default. Error %s " % e
            )
            device_pixel_ratio = self._DEFAULT_DEVICE_PIXEL_RATIO
        logger.info("Device pixel ratio: {}".format(device_pixel_ratio))

        self._device_pixel_ratio = device_pixel_ratio
        logger.debug("Setting scale provider...")
        try:
            self._scale_provider = ContextBasedScaleProvider(
                top_level_context_entire_size=self._driver.get_entire_page_size(),
                viewport_size=self.configure.viewport_size,
                device_pixel_ratio=device_pixel_ratio,
                is_mobile_device=False,  # TODO: fix scaling for mobile
            )  # type: ScaleProvider
        except Exception:
            # This can happen in Appium for example.
            logger.info("Failed to set ContextBasedScaleProvider.")
            logger.info("Using FixedScaleProvider instead...")
            self._scale_provider = FixedScaleProvider(1 / device_pixel_ratio)
        logger.debug("Scaling provider has been set")
        return self._scale_provider

    def _try_capture_dom(self):
        if self.driver.is_mobile_app:
            # While capture dom for native apps, appium throw an exception
            # "Method is not implemented" which shown in output as a warning msg
            # and mislead users.
            return None
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
        # type: (SeleniumCheckSettings) -> Optional[EyesWebElement]
        target_element = check_settings.values.target_element
        target_selector = check_settings.values.target_selector
        if not target_element and target_selector:
            by, value = target_selector
            target_element = self._driver.find_element(by, value)

        if target_element:
            if not isinstance(target_element, EyesWebElement):
                target_element = EyesWebElement(target_element, self.driver)
            return adapt_element(target_element)

    def _create_full_page_capture_algorithm(self, scale_provider):
        scroll_root_element = eyes_selenium_utils.curr_frame_scroll_root_element(
            self.driver, self._scroll_root_element
        )
        origin_provider = ScrollPositionProvider(self.driver, scroll_root_element)
        return FullPageCaptureAlgorithm(
            self.configure.wait_before_screenshots,
            self._debug_screenshots_provider,
            self._screenshot_factory,
            origin_provider,
            scale_provider,
            self._cut_provider,
            self.configure.stitch_overlap,
            self._image_provider,
            self._region_position_compensation,
        )

    @contextlib.contextmanager
    def _try_hide_caret(self):
        active_element = None
        if self.configure.hide_caret and not self.driver.is_mobile_app:
            try:
                active_element = self.driver.execute_script(
                    "var activeElement = document.activeElement; activeElement "
                    "&& activeElement.blur(); return activeElement;"
                )
            except WebDriverException as e:
                logger.warning("Cannot hide caret! \n{}".format(e))
        yield

        if self.configure.hide_caret and not self.driver.is_mobile_app:
            try:
                self.driver.execute_script("arguments[0].focus();", active_element)
            except WebDriverException as e:
                logger.warning("Cannot hide caret! \n{}".format(e))

    def _get_screenshot(self):
        with self._driver.switch_to.frames_and_back(self._original_fc):
            if self.position_provider and not self.driver.is_mobile_platform:
                state = self.position_provider.get_state()

        with self._try_hide_caret():

            scale_provider = self.update_scaling_params()

            if self._check_frame_or_element and not self.driver.is_mobile_app:
                self._last_screenshot = self._entire_element_screenshot(scale_provider)
            elif (
                self.configure.force_full_page_screenshot or self._stitch_content
            ) and not self.driver.is_mobile_app:
                self._last_screenshot = self._full_page_screenshot(scale_provider)
            else:
                self._last_screenshot = self._element_screenshot(scale_provider)

        with self._driver.switch_to.frames_and_back(self._original_fc):
            if self.position_provider and not self.driver.is_mobile_platform:
                self.position_provider.restore_state(state)

        return self._last_screenshot

    def _crop_if_needed(self, image):
        r_info = self.server_connector.render_info()
        if r_info.max_image_height is None or r_info.max_image_area is None:
            return image
        image = image_utils.crop_to_specific_size_if_needed(
            image, r_info.max_image_height, r_info.max_image_area
        )
        self._debug_screenshots_provider.save(image, "final")
        return image

    def _entire_element_screenshot(self, scale_provider):
        # type: (ScaleProvider) -> EyesWebDriverScreenshot
        logger.info("Entire element screenshot requested")

        elem_position_provider = self._element_position_provider
        if elem_position_provider is None:
            scroll_root_element = eyes_selenium_utils.curr_frame_scroll_root_element(
                self.driver, self.scroll_root_element
            )
            elem_position_provider = self._element_position_provider_from(
                scroll_root_element
            )
        algo = self._create_full_page_capture_algorithm(scale_provider)

        image = algo.get_stitched_region(
            self._region_to_check, self._full_region_to_check, elem_position_provider
        )
        image = self._crop_if_needed(image)
        return EyesWebDriverScreenshot.create_entire_element(
            self._driver,
            image,
            RectangleSize.from_(image),
            -self._full_region_to_check.location,
        )

    def _full_page_screenshot(self, scale_provider):
        # type: (ScaleProvider) -> EyesWebDriverScreenshot
        logger.info("Full page screenshot requested")

        with self.driver.switch_to.frames_and_back(self._original_fc):
            scroll_root_element = eyes_selenium_utils.curr_frame_scroll_root_element(
                self.driver
            )
            origin_provider = ScrollPositionProvider(self.driver, scroll_root_element)
            origin_provider.set_position(Point.ZERO())
            logger.debug("resetting origin_provider location")

            location = self.scroll_root_element.location
            size_and_borders = self.scroll_root_element.size_and_borders
            region = Region(
                location["x"] + size_and_borders.borders["left"],
                location["y"] + size_and_borders.borders["top"],
                size_and_borders.size["width"],
                size_and_borders.size["height"],
            )

            algo = self._create_full_page_capture_algorithm(scale_provider)
            image = algo.get_stitched_region(
                region, Region.EMPTY(), self.position_provider
            )
            image = self._crop_if_needed(image)
            return EyesWebDriverScreenshot.create_full_page(
                self._driver, image, -region.location
            )

    def _element_screenshot(self, scale_provider):
        # type: (ScaleProvider) -> EyesWebDriverScreenshot
        logger.info("Element screenshot requested")
        with self._ensure_element_visible(self._target_element):
            datetime_utils.sleep(self.configure.wait_before_screenshots)
            image = self.get_scaled_cropped_viewport_image(scale_provider)
            if not (self._is_check_region or self._driver.is_mobile_platform):
                # Some browsers return always full page screenshot (IE).
                # So we cut such images to viewport size
                image = cut_to_viewport_size_if_required(self.driver, image)
            return EyesWebDriverScreenshot.create_viewport(self._driver, image)

    def get_scaled_cropped_viewport_image(self, scale_provider):
        image = self._image_provider.get_image()
        self._debug_screenshots_provider.save(image, "original")
        scale_provider.update_scale_ratio(image.width)
        pixel_ratio = 1 / scale_provider.scale_ratio
        if pixel_ratio != 1.0:
            logger.info("Scaling")
            image = image_utils.scale_image(image, 1.0 / pixel_ratio)
            self._debug_screenshots_provider.save(image, "scaled")
        if not isinstance(self.cut_provider, NullCutProvider):
            logger.info("Cutting")
            image = self.cut_provider.cut(image)
            self._debug_screenshots_provider.save(image, "cutted")
        image = self._crop_if_needed(image)
        return image

    def _get_viewport_scroll_bounds(self):
        switch_to = self.driver.switch_to
        with switch_to.frames_and_back(self._original_fc):
            try:
                location = eyes_selenium_utils.get_current_position(
                    self.driver, self.scroll_root_element
                )
            except WebDriverException:
                logger.warning("Failed to _get_viewport_scroll_bounds")
                logger.info("Assuming position is 0,0")
                location = Point(0, 0)
        viewport_bounds = Region.from_(location, self._get_viewport_size())
        return viewport_bounds

    @contextlib.contextmanager
    def _ensure_element_visible(self, element):
        position_provider = fc = None
        if element and not self.driver.is_mobile_app:
            original_fc = self.driver.frame_chain.clone()
            element_bounds = element.bounds

            current_frame_offset = original_fc.current_frame_offset
            element_bounds = element_bounds.offset(current_frame_offset)
            viewport_bounds = self._get_viewport_scroll_bounds()
            logger.info(
                "viewport_bounds: {}; element_bounds: {}".format(
                    viewport_bounds, element_bounds
                )
            )

            if not viewport_bounds.contains(element_bounds):
                self._ensure_frame_visible()
                element_location = Point.from_(element.location)
                if len(original_fc) > 0 and element is not original_fc.peek.reference:
                    fc = original_fc
                    self.driver.switch_to.frames(original_fc)
                    scroll_root_element = (
                        eyes_selenium_utils.curr_frame_scroll_root_element(
                            self.driver, self._scroll_root_element
                        )
                    )
                # This might happen when scroll root element is calculated in the
                # beginning of SeleniumEyes.check when there is a frame in
                # driver's frame_chain but it gets popped out and becomes check target
                elif not self.scroll_root_element.is_attached_to_page:
                    fc = self.driver.frame_chain.clone()
                    scroll_root_element = self.driver.find_element_by_tag_name("html")
                else:
                    fc = self.driver.frame_chain.clone()
                    scroll_root_element = self.scroll_root_element
                position_provider = self._element_position_provider_from(
                    scroll_root_element
                )
                state = position_provider.get_state()
                position_provider.set_position(element_location)

        yield position_provider
        if element and position_provider and fc and not self.driver.is_mobile_app:
            self.driver.switch_to.frames(fc)
            position_provider.restore_state(state)
