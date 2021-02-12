from __future__ import absolute_import

import contextlib
import typing

import attr
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.switch_to import SwitchTo
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from applitools.common import RectangleSize, deprecated, logger
from applitools.common.geometry import Point
from applitools.common.utils import argument_guard, cached_property, image_utils
from applitools.common.utils.compat import basestring
from applitools.common.utils.general_utils import all_attrs, proxy_to
from applitools.selenium import webdriver_sync
from applitools.selenium.fluent import FrameLocator

from . import eyes_selenium_utils, useragent
from .frames import Frame, FrameChain
from .positioning import ScrollPositionProvider
from .useragent import UserAgent
from .webelement import EyesWebElement

if typing.TYPE_CHECKING:
    from typing import Any, ContextManager, Dict, Generator, List, Optional, Text, Union

    from appium.webdriver import Remote as AppiumWebDriver
    from PIL.Image import Image

    from applitools.common.utils.custom_types import FrameReference, ViewPort

    from .eyes import Eyes


@attr.s
class FrameResolver(object):
    _frame_ref = attr.ib()
    _driver = attr.ib()
    eyes_webelement = attr.ib(init=False)
    webelement = attr.ib(init=False)

    def __attrs_post_init__(self):
        # Find the frame's location and add it to the current driver offset
        frame_ref = self._ref_if_locator(self._frame_ref)
        driver = self._driver
        if isinstance(frame_ref, basestring):
            try:
                frame_eyes_webelement = driver.find_element_by_name(frame_ref)
            except NoSuchElementException:
                frame_eyes_webelement = driver.find_element_by_id(frame_ref)
        elif isinstance(frame_ref, int):
            frame_elements_list = driver.find_elements_by_css_selector("frame, iframe")
            frame_eyes_webelement = frame_elements_list[frame_ref]
        elif isinstance(frame_ref, EyesWebElement):
            frame_eyes_webelement = frame_ref
        else:
            # It must be a WebElement
            frame_eyes_webelement = EyesWebElement(frame_ref, driver)

        self.eyes_webelement = frame_eyes_webelement
        self.webelement = frame_eyes_webelement.element

    def _ref_if_locator(self, frame_ref):
        if isinstance(frame_ref, FrameLocator):
            frame_locator = frame_ref
            if frame_locator.frame_index is not None:
                frame_ref = frame_locator.frame_index
            if frame_locator.frame_name_or_id:
                frame_ref = frame_locator.frame_name_or_id
            if frame_locator.frame_element:
                frame_ref = frame_locator.frame_element
            if frame_locator.frame_selector:
                by, value = frame_locator.frame_selector
                frame_ref = self._driver.find_element(by, value)
        return frame_ref


@proxy_to("_switch_to")
class _EyesSwitchTo(object):
    """
    Wraps :py:class:`selenium.webdriver.remote.switch_to.SwitchTo` object, so we can
    keep track of  switching between frames. It names EyesTargetLocator in other SDK's
    """

    PARENT_FRAME = 1
    _position_memento = None

    def __init__(self, driver, switch_to):
        # type: (EyesWebDriver, SwitchTo) -> None
        """
        Ctor.

        :param driver: EyesWebDriver instance.
        :param switch_to: Selenium switchTo object.
        """
        self._proxy_to_fields = all_attrs(switch_to)
        self._switch_to = switch_to  # type: SwitchTo
        self._driver = driver  # type: EyesWebDriver

    @contextlib.contextmanager
    def frame_and_back(self, frame_reference):
        # type: (FrameReference) -> Generator
        cur_frame = None
        if not self._driver.is_mobile_app:
            self.frame(frame_reference)
            cur_frame = self._driver.frame_chain.peek
        try:
            yield cur_frame
        finally:
            if not self._driver.is_mobile_app:
                self.parent_frame()

    @contextlib.contextmanager
    def frames_and_back(self, frame_chain):
        # type: (FrameChain) -> Generator
        cur_frame = None
        origin_fc = self._driver.frame_chain.clone()
        if not self._driver.is_mobile_app:
            self.frames(frame_chain)
            cur_frame = self._driver.frame_chain.peek
        try:
            yield cur_frame
        finally:
            if not self._driver.is_mobile_app:
                self.frames(origin_fc)

    def frame(self, frame_reference):
        # type: (FrameReference) -> None
        """
        Switch to a given frame.

        :param frame_reference: The reference to the frame.
        """
        frame_res = FrameResolver(frame_reference, self._driver)
        self._do_switch_to_frame(frame_res.eyes_webelement)

    def frames(self, frame_chain):
        # type: (FrameChain) -> None
        """
        Switches to the frames one after the other.

        :param frame_chain: A list of frames.
        """
        self.default_content()
        for frame in frame_chain:
            self.frame(frame.reference)
            logger.debug(
                "frame.reference: {}; frame.scroll_root_element: {}".format(
                    getattr(frame.reference, "id", None),
                    getattr(frame.scroll_root_element, "id", None),
                )
            )
            new_frame = self._driver.frame_chain.peek
            new_frame.scroll_root_element = frame.scroll_root_element
        logger.debug("Done switching into nested frame")

    def default_content(self):
        # type: () -> None
        """
        Switch to default content.
        """
        del self._driver.frame_chain[:]
        self._switch_to.default_content()

    def parent_frame(self):
        """
        Switch to parent frame.
        """
        if len(self._driver.frame_chain) > 0:
            frame = self._driver.frame_chain.pop()
            self.parent_frame_static(self._switch_to, self._driver.frame_chain)
            return frame

    def window(self, window_name):
        # type: (Text) -> None
        """
        Switch to window.
        """
        del self._driver.frame_chain[:]
        self._switch_to.window(window_name)

    def _do_switch_to_frame(self, target_frame):
        # type: (EyesWebElement) -> None
        """
        Will be called when switching into a frame.

        :param target_frame: The element to be switched to.
        """
        argument_guard.not_none(target_frame)

        size_and_borders = target_frame.size_and_borders
        borders = size_and_borders.borders
        frame_inner_size = size_and_borders.size
        bounds = target_frame.bounding_client_rect

        content_location = Point(
            bounds["x"] + borders["left"], bounds["y"] + borders["top"]
        )
        outer_size = RectangleSize.from_(target_frame.size)
        inner_size = RectangleSize.from_(frame_inner_size)
        original_location = target_frame.scroll_location

        self._switch_to.frame(target_frame.element)

        scroll_root_element = self._driver.find_element_by_xpath("/*")
        frame = Frame(
            reference=target_frame,
            location=content_location,
            outer_size=outer_size,
            inner_size=inner_size,
            parent_scroll_position=original_location,
            scroll_root_element=scroll_root_element,
        )
        self._driver.frame_chain.push(frame)

    @staticmethod
    def parent_frame_static(switch_to, frame_chain_parent):
        # type: (SwitchTo, FrameChain) -> None
        try:
            switch_to.parent_frame()
        except WebDriverException:
            switch_to.default_content()
            for frame in frame_chain_parent:
                switch_to.frame(frame.reference)

    @contextlib.contextmanager
    def frames_do_scroll(self, frame_chain):
        self.default_content()
        scroll_provider = self._get_scroll_provider()
        self._position_memento = scroll_provider.get_state()
        for frame in frame_chain:
            logger.debug("Scrolling by parent scroll position...")
            frame_location = frame.location
            scroll_provider.set_position(frame_location)
            logger.debug("Done! Switching to frame...")
            self.frame(frame.reference)
            new_frame = self._driver.frame_chain.peek
            new_frame.scroll_root_element = frame.scroll_root_element
            logger.debug("Done switching to frame")
        logger.debug("Done switching into nested frames!")
        return self._driver

    def reset_scroll(self):
        if self._position_memento:
            self._get_scroll_provider().restore_state(self._position_memento)
            self._position_memento = None

    def _get_scroll_provider(self):
        scroll_root_element = eyes_selenium_utils.curr_frame_scroll_root_element(
            self._driver
        )
        return ScrollPositionProvider(self._driver, scroll_root_element)


@proxy_to("_driver")
class EyesWebDriver(object):
    """
    A wrapper for selenium web driver which creates wrapped elements,
    and notifies us about events / actions.
    """

    # This should pretty much cover all scroll bars
    # (and some fixed position footer elements :) ).
    _MAX_SCROLL_BAR_SIZE = 50

    _MIN_SCREENSHOT_PART_HEIGHT = 10

    def __init__(self, driver, eyes):
        # type: (WebDriver, Eyes) -> None
        """
        Ctor.

        :param driver: remote WebDriver instance.
        :param eyes: A Eyes sdk instance.
        :param stitch_mode: How to stitch a page (default is with scrolling).
        """
        self._proxy_to_fields = all_attrs(driver)
        self._driver = driver  # type: Union[WebDriver, AppiumWebDriver]
        self._eyes = eyes  # type: Eyes
        # List of frames the user switched to, and the current offset,
        # so we can properly calculate elements' coordinates
        self._frame_chain = FrameChain()
        self._default_content_viewport_size = None  # type: Optional[ViewPort]

        self.driver_takes_screenshot = driver.capabilities.get("takesScreenshot", False)
        self.rotation = None  # type: Optional[int]
        self._user_agent = None  # type: Optional[UserAgent]

    @property
    def eyes(self):
        # type: () -> Eyes
        return self._eyes

    @property
    def user_agent(self):
        # type: () -> useragent.UserAgent
        if self.is_mobile_app:
            major_version = minor_version = None
            if self.platform_version:
                if "." in self.platform_version:
                    version_parts = self.platform_version.split(".", 2)
                    major_version, minor_version = version_parts[:2]
                else:
                    major_version = self.platform_version
            self._user_agent = useragent.UserAgent(
                os=self.platform_name,
                os_major_version=major_version,
                os_minor_version=minor_version,
            )
        if self._user_agent:
            return self._user_agent
        try:
            ua_string = self._driver.execute_script("return navigator.userAgent")
            self._user_agent = useragent.parse_user_agent_string(ua_string)
        except WebDriverException as e:
            logger.exception(e)
        return self._user_agent

    @property
    def session_id(self):
        return self._driver.session_id

    @cached_property
    def platform_name(self):
        # type: () -> Optional[Text]
        return self._driver.desired_capabilities.get("platformName", None)

    @cached_property
    def platform_version(self):
        # type: () -> Optional[Text]
        return self._driver.desired_capabilities.get("platformVersion", None)

    @deprecated.attribute("use `is_mobile_platform` property instead")
    def is_mobile_device(self):
        return self.is_mobile_platform

    @property
    def is_mobile_platform(self):
        # type: () -> bool
        """
        Returns whether the platform running is a mobile device or not.

        :return: True if the platform running the test is a mobile platform.
                 False otherwise.
        """
        return eyes_selenium_utils.is_mobile_platform(self._driver)

    @property
    def is_mobile_web(self):
        return eyes_selenium_utils.is_mobile_web(self._driver)

    @property
    def is_mobile_app(self):
        return eyes_selenium_utils.is_mobile_app(self._driver)

    @staticmethod
    def normalize_rotation(driver, image, rotation):
        # type: (WebDriver, Image, Optional[int]) -> Image
        """
        Rotates the image as necessary. The rotation is either manually forced
        by passing a non-null rotation, or automatically inferred.

        :param driver: The underlying driver which produced the screenshot.
        :param image: The image to normalize.
        :param rotation: The degrees by which to rotate the image:
                         positive values = clockwise rotation,
                         negative values = counter-clockwise,
                         0 = force no rotation,
                         null = rotate automatically as needed.
        :return: A normalized image.
        """
        argument_guard.not_none(driver)
        argument_guard.not_none(image)
        normalized_image = image
        if rotation and rotation != 0:
            normalized_image = image_utils.rotate_image(image, rotation)
        else:  # Do automatic rotation if necessary
            try:
                logger.info("Trying to automatically normalize rotation...")
                if (
                    eyes_selenium_utils.is_mobile_app(driver)
                    and eyes_selenium_utils.is_landscape_orientation(driver)
                    and image.height > image.width
                ):
                    # For Android, we need to rotate images to the right,
                    # and for iOS to the left.
                    degree = 90 if eyes_selenium_utils.is_android(driver) else -90
                    normalized_image = image_utils.rotate_image(image, degree)
            except Exception as e:
                logger.exception(e)
                logger.info("Skipped automatic rotation handling.")
        return normalized_image

    def get(self, url):
        # type: (Text) -> Optional[Any]
        """
        Navigates the driver to the given url.

        :param url: The url to navigate to.
        :return: A driver that navigated to the given url.
        """
        # We're loading a new page, so the frame location resets
        del self._frame_chain[:]
        return self._driver.get(url)

    def find_element(self, by=By.ID, value=None):
        # type: (Text, Text) -> EyesWebElement
        """
        Returns a WebElement denoted by "By".

        :param by: By which option to search for (default is by ID).
        :param value: The value to search for.
        :return: A element denoted by "By".
        """
        # Get result from the original implementation of the underlying driver.
        element = self._driver.find_element(by, value)
        # Wrap the element.
        if element:
            element = EyesWebElement(element, self)
        return element

    def find_elements(self, by=By.ID, value=None):
        # type: (Text, Text) -> List[EyesWebElement]
        """
        Returns a list of web elements denoted by "By".

        :param by: By which option to search for (default is by ID).
        :param value: The value to search for.
        :return: List of elements denoted by "By".
        """
        # Get result from the original implementation of the underlying driver.
        elements = self._driver.find_elements(by, value)
        # Wrap all returned elements.
        if elements:
            elements = [EyesWebElement(el, self) for el in elements]
        return elements

    def find_element_by_id(self, id_):
        # type: (Text) -> EyesWebElement
        """
        Finds an element by id.

        :params id_: The id of the element to be found.
        """
        return self.find_element(by=By.ID, value=id_)

    def find_elements_by_id(self, id_):
        # type: (Text) -> List[EyesWebElement]
        """
        Finds multiple elements by id.

        :param id_: The id of the elements to be found.
        """
        return self.find_elements(by=By.ID, value=id_)

    def find_element_by_xpath(self, xpath):
        # type: (Text) -> EyesWebElement
        """
        Finds an element by xpath.

        :param xpath: The xpath locator of the element to find.
        """
        return self.find_element(by=By.XPATH, value=xpath)

    def find_elements_by_xpath(self, xpath):
        # type: (Text) -> List[EyesWebElement]
        """
        Finds multiple elements by xpath.

        :param xpath: The xpath locator of the elements to be found.
        """
        return self.find_elements(by=By.XPATH, value=xpath)

    def find_element_by_link_text(self, link_text):
        # type: (Text) -> EyesWebElement
        """
        Finds an element by link text.

        :param link_text: The text of the element to be found.
        """
        return self.find_element(by=By.LINK_TEXT, value=link_text)

    def find_elements_by_link_text(self, text):
        # type: (Text) -> List[EyesWebElement]
        """
        Finds elements by link text.

        :param text: The text of the elements to be found.
        """
        return self.find_elements(by=By.LINK_TEXT, value=text)

    def find_element_by_partial_link_text(self, link_text):
        # type: (Text) -> EyesWebElement
        """
        Finds an element by a partial match of its link text.

        :param link_text: The text of the element to partially match on.
        """
        return self.find_element(by=By.PARTIAL_LINK_TEXT, value=link_text)

    def find_elements_by_partial_link_text(self, link_text):
        # type: (Text) -> List[EyesWebElement]
        """
        Finds elements by a partial match of their link text.

        :param link_text: The text of the element to partial match on.
        """
        return self.find_elements(by=By.PARTIAL_LINK_TEXT, value=link_text)

    def find_element_by_name(self, name):
        # type: (Text) -> EyesWebElement
        """
        Finds an element by name.

        :param name: The name of the element to find.
        """
        return self.find_element(by=By.NAME, value=name)

    def find_elements_by_name(self, name):
        # type: (Text) -> List[EyesWebElement]
        """
        Finds elements by name.

        :param name: The name of the elements to find.
        """
        return self.find_elements(by=By.NAME, value=name)

    def find_element_by_tag_name(self, name):
        # type: (Text) -> EyesWebElement
        """
        Finds an element by tag name.

        :param name: The tag name of the element to find.
        """
        return self.find_element(by=By.TAG_NAME, value=name)

    def find_elements_by_tag_name(self, name):
        # type: (Text) -> List[EyesWebElement]
        """
        Finds elements by tag name.

        :param name: The tag name to use when finding elements.
        """
        return self.find_elements(by=By.TAG_NAME, value=name)

    def find_element_by_class_name(self, name):
        # type: (Text) -> EyesWebElement
        """
        Finds an element by class name.

        :param name: The class name of the element to find.
        """
        return self.find_element(by=By.CLASS_NAME, value=name)

    def find_elements_by_class_name(self, name):
        # type: (Text) -> List[EyesWebElement]
        """
        Finds elements by class name.

        :param name: The class name of the elements to find.
        """
        return self.find_elements(by=By.CLASS_NAME, value=name)

    def find_element_by_css_selector(self, css_selector):
        # type: (Text) -> EyesWebElement
        """
        Finds an element by css selector.

        :param css_selector: The css selector to use when finding elements.
        """
        return self.find_element(by=By.CSS_SELECTOR, value=css_selector)

    def find_elements_by_css_selector(self, css_selector):
        # type: (Text) -> List[EyesWebElement]
        """
        Finds elements by css selector.

        :param css_selector: The css selector to use when finding elements.
        """
        return self.find_elements(by=By.CSS_SELECTOR, value=css_selector)

    def get_screenshot_as_base64(self):
        # type: () -> Text
        """
        Gets the screenshot of the current window as a base64 encoded string
           which is useful in embedded images in HTML.
        """
        screenshot64 = self._driver.get_screenshot_as_base64()
        screenshot = image_utils.image_from_base64(screenshot64)
        screenshot = self.normalize_rotation(self._driver, screenshot, self.rotation)
        screenshot64 = image_utils.get_base64(screenshot)
        return screenshot64

    def extract_full_page_width(self):
        # type: () -> int
        """
        Extracts the full page width.

        :return: The width of the full page.
        """
        # noinspection PyUnresolvedReferences
        default_scroll_width = int(
            round(
                self._driver.execute_script(
                    "return document.documentElement.scrollWidth"
                )
            )
        )
        body_scroll_width = int(
            round(self._driver.execute_script("return document.body.scrollWidth"))
        )
        return max(default_scroll_width, body_scroll_width)

    def extract_full_page_height(self):
        # type: () -> int
        """
        Extracts the full page height.

        :return: The height of the full page.
        IMPORTANT: Notice there's a major difference between scrollWidth and scrollHeight.
        While scrollWidth is the maximum between an element's width and its content width,
        scrollHeight might be smaller(!) than the clientHeight, which is why we take the
        maximum between them.
        """
        # noinspection PyUnresolvedReferences
        default_client_height = int(
            round(
                self._driver.execute_script(
                    "return document.documentElement.clientHeight"
                )
            )
        )
        # noinspection PyUnresolvedReferences
        default_scroll_height = int(
            round(
                self._driver.execute_script(
                    "return document.documentElement.scrollHeight"
                )
            )
        )
        # noinspection PyUnresolvedReferences
        body_client_height = int(
            round(self._driver.execute_script("return document.body.clientHeight"))
        )
        # noinspection PyUnresolvedReferences
        body_scroll_height = int(
            round(self._driver.execute_script("return document.body.scrollHeight"))
        )
        max_document_element_height = max(default_client_height, default_scroll_height)
        max_body_height = max(body_client_height, body_scroll_height)
        return max(max_document_element_height, max_body_height)

    def get_entire_page_size(self):
        # type: () -> Dict[Text, int]
        """
        Extracts the size of the current page from the browser using Javascript.

        :return: The page width and height.
        """
        return {
            "width": self.extract_full_page_width(),
            "height": self.extract_full_page_height(),
        }

    def wait_for_page_load(self, timeout=3, throw_on_timeout=False):
        # type: (int, bool) -> None
        """
        Waits for the current document to be "loaded".

        :param timeout: The maximum time to wait, in seconds.
        :param throw_on_timeout: Whether to throw an exception when timeout is reached.
        """
        # noinspection PyBroadException
        try:
            WebDriverWait(self._driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState")
                == "complete"
            )
        except Exception:
            logger.debug("Page load timeout reached!")
            if throw_on_timeout:
                raise

    @property
    def frame_chain(self):
        # type: () -> FrameChain
        """
        Gets the frame chain.

        :return: A list of Frame instances which represents the path to the current
            frame. This can later be used as an argument to _EyesSwitchTo.frames().
        """
        return self._frame_chain

    def get_default_content_viewport_size(self, force_query=True):
        # type: (bool) -> ViewPort
        """
        Args:
            force_query: If true, we will perform the query even if we have a cached
                         viewport size.

        Returns:
            The viewport size of the default content (outer most frame).
        """
        if self._default_content_viewport_size and not force_query:
            return self._default_content_viewport_size

        current_frames = self.frame_chain.clone()
        # If we're inside a frame, then we should first switch to the most outer frame.
        # Optimization
        if current_frames:
            self.switch_to.default_content()
        self._default_content_viewport_size = (
            eyes_selenium_utils.get_viewport_size_or_display_size(self._driver)
        )

        if current_frames:
            self.switch_to.frames(current_frames)

        return self._default_content_viewport_size

    @property
    def switch_to(self):
        return _EyesSwitchTo(self, self._driver.switch_to)

    def execute_script(self, script, *args):
        def extract_origin_webelement(value):
            if isinstance(value, EyesWebElement):
                return value.element
            elif isinstance(value, list) or isinstance(value, tuple):
                return list(extract_origin_webelement(item) for item in value)
            return value

        args = extract_origin_webelement(args)
        return self._driver.execute_script(script, *args)

    def get_window_size(self, windowHandle="current"):
        size = self._driver.get_window_size(windowHandle)
        return RectangleSize(**size)

    def get_window_position(self, windowHandle="current"):
        loc = self._driver.get_window_position(windowHandle)
        return Point(**loc)

    def set_window_size(self, width, height, windowHandle="current"):
        self._driver.set_window_size(width, height, windowHandle)

    def set_window_position(self, x, y, windowHandle="current"):
        self._driver.set_window_position(x, y, windowHandle)

    @property
    def desired_capabilities(self):
        # type: () -> Dict
        """
        returns the drivers current desired capabilities being used
        """
        return self._driver.desired_capabilities

    def close(self):
        """
        Closes the current window.

        :Usage:
            driver.close()
        """
        self._driver.close()

    def quit(self):
        """
        Quits the driver and closes every associated window.

        :Usage:
            driver.quit()
        """
        self._driver.quit()

    @contextlib.contextmanager
    def saved_frame_chain(self):
        # type: () -> ContextManager
        """Context manager that saves and restores driver's frame chain"""
        original_fc = self.frame_chain.clone()
        try:
            yield
        finally:
            if original_fc is not None:
                self.switch_to.frames(original_fc)

    def ensure_sync_with_underlying_driver(self):
        webdriver_sync.ensure_sync_with_underlying_driver(self, self._driver)
