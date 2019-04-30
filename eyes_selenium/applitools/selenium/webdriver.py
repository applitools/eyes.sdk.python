from __future__ import absolute_import

import contextlib
import typing

import attr
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.switch_to import SwitchTo
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from applitools.common import RectangleSize, logger
from applitools.common.geometry import Point
from applitools.common.utils import (
    argument_guard,
    cached_property,
    general_utils,
    image_utils,
)
from applitools.common.utils.compat import basestring
from applitools.selenium.fluent import FrameLocator

from . import eyes_selenium_utils
from .frames import Frame, FrameChain
from .positioning import ScrollPositionProvider
from .webelement import EyesWebElement

if typing.TYPE_CHECKING:
    from typing import Generator, Text, Optional, List, Dict, Any
    from applitools.common.utils.custom_types import ViewPort, FrameReference
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
            frame_eyes_webelement = driver.find_element_by_name(frame_ref)
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
            if frame_locator.frame_index:
                frame_ref = frame_locator.frame_index
            if frame_locator.frame_name_or_id:
                frame_ref = frame_locator.frame_name_or_id
            if frame_locator.frame_element:
                frame_ref = frame_locator.frame_element
            if frame_locator.frame_selector:
                frame_ref = self._driver.find_element_by_css_selector(
                    frame_locator.frame_selector
                )
        return frame_ref


class _EyesSwitchTo(object):
    """
    Wraps :py:class:`selenium.webdriver.remote.switch_to.SwitchTo` object, so we can
    keep track of  switching between frames. It names EyesTargetLocator in other SDK's
    """

    # TODO: Make more similar to EyesTargetLocator
    _READONLY_PROPERTIES = ["alert", "active_element"]
    PARENT_FRAME = 1

    def __init__(self, driver, switch_to):
        # type: (EyesWebDriver, SwitchTo) -> None
        """
        Ctor.

        :param driver: EyesWebDriver instance.
        :param switch_to: Selenium switchTo object.
        """
        self._switch_to = switch_to  # type: SwitchTo
        self._driver = driver  # type: EyesWebDriver
        self._scroll_position = ScrollPositionProvider(
            driver, eyes_selenium_utils.current_frame_scroll_root_element(driver)
        )
        general_utils.create_proxy_interface(self, switch_to, self._READONLY_PROPERTIES)

    @contextlib.contextmanager
    def frame_and_back(self, frame_reference):
        # type: (FrameReference) -> Generator
        cur_frame = None
        if not self._driver.is_mobile_device():
            self.frame(frame_reference)
            cur_frame = self._driver.frame_chain.peek

        yield cur_frame

        if not self._driver.is_mobile_device():
            self.parent_frame()

    @contextlib.contextmanager
    def frames_and_back(self, frame_chain):
        # type: (FrameChain) -> Generator
        cur_frame = None
        origin_fc = self._driver.frame_chain.clone()
        if not self._driver.is_mobile_device():
            self.frames(frame_chain)
            cur_frame = self._driver.frame_chain.peek

        yield cur_frame

        if not self._driver.is_mobile_device():
            self.frames(origin_fc)

    def frame(self, frame_reference):
        # type: (FrameReference) -> None
        """
        Switch to a given frame.

        :param frame_reference: The reference to the frame.
        """
        frame_res = FrameResolver(frame_reference, self._driver)
        self.will_switch_to_frame(frame_res.eyes_webelement)
        self._switch_to.frame(frame_res.webelement)

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
                "frame.Reference: %s ; frame.ScrollRootElement: %s"
                % (frame.reference.id, frame.scroll_root_element.id)
            )
            new_frame = self._driver.frame_chain.peek
            new_frame.scroll_root_element = frame.scroll_root_element
        logger.debug("Done switching into nested frame")

    def default_content(self):
        # type: () -> None
        """
        Switch to default content.
        """
        self._driver.frame_chain.clear()
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
        self._driver.frame_chain.clear()
        self._switch_to.window(window_name)

    def will_switch_to_frame(self, target_frame):
        # type: (EyesWebElement) -> None
        """
        Will be called before switching into a frame.

        :param target_frame: The element about to be switched to.
        """
        argument_guard.not_none(target_frame)
        pl = target_frame.location

        size_and_borders = target_frame.size_and_borders
        borders = size_and_borders.borders
        frame_inner_size = size_and_borders.size

        content_location = Point(pl["x"] + borders["left"], pl["y"] + borders["top"])
        sp = ScrollPositionProvider(
            self._driver, self._driver.find_element_by_tag_name("html")
        )
        original_location = sp.get_current_position()
        sp.set_position(original_location)
        frame = Frame(
            target_frame,
            content_location,
            target_frame.size,
            frame_inner_size,
            parent_scroll_position=original_location,
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

    def frames_do_scroll(self, frame_chain):
        self.default_content()
        root_element = eyes_selenium_utils.current_frame_scroll_root_element(
            self._driver
        )
        scroll_provider = ScrollPositionProvider(self._driver, root_element)
        for frame in frame_chain:
            logger.debug("Scrolling by parent scroll position...")
            frame_location = frame.location
            scroll_provider.set_position(frame_location)
            logger.debug("Done! Switching to frame...")
            self.frame(frame.reference)
            new_frame = self._driver.frame_chain.peek
            new_frame.scroll_root_element = frame.scroll_root_element
            logger.debug("Done")
        logger.debug("Done switching into nested frames!")
        return self._driver

    def reset_scroll(self):
        if self._scroll_position.states:
            self._scroll_position.pop_state()


class EyesWebDriver(object):
    """
    A wrapper for selenium web driver which creates wrapped elements,
    and notifies us about events / actions.
    """

    # Properties require special handling since even testing if they're
    # callable "activates" them, which makes copying them automatically a problem.
    _READONLY_PROPERTIES = [
        "application_cache",
        "current_url",
        "current_window_handle",
        "desired_capabilities",
        "log_types",
        "name",
        "page_source",
        "title",
        "window_handles",
        "switch_to",
        "mobile",
        "current_context",
        "context",
        "current_activity",
        "network_connection",
        "available_ime_engines",
        "active_ime_engine",
        "device_time",
        "w3c",
        "contexts",
        "current_package",
    ]
    _READONLY_PROPERTIES += ["battery_info", "location"]  # Appium specific
    _SETTABLE_PROPERTIES = ["orientation", "file_detector"]

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
        self._driver = driver
        self._eyes = eyes
        # List of frames the user switched to, and the current offset,
        # so we can properly calculate elements' coordinates
        self._frame_chain = FrameChain()
        self._default_content_viewport_size = None  # type: Optional[ViewPort]

        self.driver_takes_screenshot = driver.capabilities.get("takesScreenshot", False)

        # Creating the rest of the driver interface by simply forwarding it to the
        # underlying driver.
        general_utils.create_proxy_interface(
            self, driver, self._READONLY_PROPERTIES + self._SETTABLE_PROPERTIES
        )

        for attr_name in self._READONLY_PROPERTIES:
            if not hasattr(self.__class__, attr_name):
                setattr(
                    self.__class__,
                    attr_name,
                    general_utils.create_proxy_property(attr_name, "_driver"),
                )
        for attr_name in self._SETTABLE_PROPERTIES:
            if not hasattr(self.__class__, attr_name):
                setattr(
                    self.__class__,
                    attr_name,
                    general_utils.create_proxy_property(attr_name, "_driver", True),
                )

    @property
    def eyes(self):
        # type: () -> Eyes
        return self._eyes

    def get_display_rotation(self):
        # type: () -> int
        """
        Get the rotation of the screenshot.

        :return: The rotation of the screenshot we get from the webdriver in (degrees).
        """
        if self.platform_name == "Android" and self._driver.orientation == "LANDSCAPE":
            return -90
        return 0

    @cached_property
    def platform_name(self):
        # type: () -> Optional[Text]
        return self._driver.desired_capabilities.get("platformName", None)

    @cached_property
    def platform_version(self):
        # type: () -> Optional[Text]
        return self._driver.desired_capabilities.get("platformVersion", None)

    def is_mobile_device(self):
        # type: () -> bool
        """
        Returns whether the platform running is a mobile device or not.

        :return: True if the platform running the test is a mobile platform.
                 False otherwise.
        """
        return eyes_selenium_utils.is_mobile_device(self._driver)

    def get(self, url):
        # type: (Text) -> Optional[Any]
        """
        Navigates the driver to the given url.

        :param url: The url to navigate to.
        :return: A driver that navigated to the given url.
        """
        # We're loading a new page, so the frame location resets
        self._frame_chain.clear()
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
        result = self._driver.find_element(by, value)
        # Wrap the element.
        if result:
            result = EyesWebElement(result, self)
        return result

    def find_elements(self, by=By.ID, value=None):
        # type: (Text, Text) -> List[EyesWebElement]
        """
        Returns a list of web elements denoted by "By".

        :param by: By which option to search for (default is by ID).
        :param value: The value to search for.
        :return: List of elements denoted by "By".
        """
        # Get result from the original implementation of the underlying driver.
        results = self._driver.find_elements(by, value)
        # Wrap all returned elements.
        if results:
            updated_results = []
            for element in results:
                updated_results.append(EyesWebElement(element, self))
            results = updated_results
        return results

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
        display_rotation = self.get_display_rotation()
        if display_rotation != 0:
            logger.info("Rotation required.")
            # num_quadrants = int(-(display_rotation / 90))
            logger.debug("Done! Creating image object...")
            screenshot = image_utils.image_from_base64(screenshot64)

            # rotating
            if display_rotation == -90:
                screenshot64 = image_utils.get_base64(screenshot.rotate(90))
            logger.debug("Done! Rotating...")

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

    def get_default_content_viewport_size(self, force_query=False):
        # type: (bool) -> ViewPort
        """
        Gets the viewport size.

        :return: The viewport size of the most outer frame.
        """
        if self._default_content_viewport_size and not force_query:
            return self._default_content_viewport_size

        current_frames = self.frame_chain.clone()
        # If we're inside a frame, then we should first switch to the most outer frame.
        # Optimization
        if current_frames:
            self.switch_to.default_content()
        self._default_content_viewport_size = eyes_selenium_utils.get_viewport_size_or_display_size(  # noqa: B950
            self._driver
        )

        if current_frames:
            self.switch_to.frames(current_frames)

        return self._default_content_viewport_size

    @property
    def switch_to(self):
        return _EyesSwitchTo(self, self._driver.switch_to)

    def execute_script(self, script, *args):
        return self._driver.execute_script(script, *args)

    def get_window_size(self, windowHandle="current"):
        size = self._driver.get_window_size(windowHandle)
        return RectangleSize(**size)

    def set_window_size(self, width, height, windowHandle="current"):
        self._driver.set_window_size(width, height, windowHandle)

    def set_window_position(self, x, y, windowHandle="current"):
        self._driver.set_window_position(x, y, windowHandle)
