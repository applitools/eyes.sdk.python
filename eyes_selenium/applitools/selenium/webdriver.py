from __future__ import absolute_import

import base64
import contextlib
import time
import typing as tp

from PIL import Image
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.switch_to import SwitchTo
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from applitools.core import logger
from applitools.core.errors import EyesError
from applitools.core.geometry import Point, Region
from applitools.core.utils import cached_property, image_utils, general_utils
from . import eyes_selenium_utils, StitchMode
from .positioning import ElementPositionProvider, build_position_provider_for, ScrollPositionProvider
from .webelement import EyesWebElement
from .frames import Frame, FrameChain

if tp.TYPE_CHECKING:
    from applitools.core.scaling import ScaleProvider
    from applitools.core.utils.custom_types import Num, ViewPort, FrameReference, AnyWebDriver, AnyWebElement
    from .eyes import Eyes


class FrameResolver(object):
    def __init__(self, frame_ref, driver):
        # Find the frame's location and add it to the current driver offset
        if isinstance(frame_ref, str):
            frame_eyes_webelement = driver.find_element_by_name(frame_ref)
        elif isinstance(frame_ref, int):
            frame_elements_list = driver.find_elements_by_css_selector('frame, iframe')
            frame_eyes_webelement = frame_elements_list[frame_ref]
        elif isinstance(frame_ref, EyesWebElement):
            frame_eyes_webelement = frame_ref
        else:
            # It must be a WebElement
            frame_eyes_webelement = EyesWebElement(frame_ref, driver)

        self.eyes_webelement = frame_eyes_webelement
        self.webelement = frame_eyes_webelement.element


class _EyesSwitchTo(object):
    """
    Wraps a selenium "SwitchTo" object, so we can keep track of switching between frames.
    It has name EyesTargetLocator in other SDK's
    """
    # TODO: Make more similar to EyesTargetLocator
    _READONLY_PROPERTIES = ['alert', 'active_element']
    PARENT_FRAME = 1

    def __init__(self, driver, switch_to):
        # type: (EyesWebDriver, SwitchTo) -> None
        """
        Ctor.

        :param driver: EyesWebDriver instance.
        :param switch_to: Selenium switchTo object.
        """
        self._switch_to = switch_to
        self._driver = driver
        self._scroll_position = ScrollPositionProvider(driver)
        general_utils.create_proxy_interface(self, switch_to, self._READONLY_PROPERTIES)

    @contextlib.contextmanager
    def frame_and_back(self, frame_reference):
        # type: (FrameReference) -> tp.Generator
        self.frame(frame_reference)
        yield
        self.parent_frame()

    def frame(self, frame_reference):
        # type: (FrameReference) -> None
        """
        Switch to a given frame.

        :param frame_reference: The reference to the frame.
        """
        frame = FrameResolver(frame_reference, self._driver)
        self.will_switch_to_frame(frame.eyes_webelement)
        self._switch_to.frame(frame.webelement)

    def frames(self, frame_chain):
        # type: (FrameChain) -> None
        """
        Switches to the frames one after the other.

        :param frame_chain: A list of frames.
        """
        self._switch_to.default_content()
        for frame in frame_chain:
            self.frame(frame.reference)

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
        frames = self._driver.frame_chain
        if frames:
            frames.pop()

            try:
                self._switch_to.parent_frame()
            except WebDriverException:
                self._switch_to.default_content()
                for frame in frames:
                    self._switch_to.frame(frame.reference)

    def window(self, window_name):
        # type: (tp.Text) -> None
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
        assert target_frame is not None
        pl = target_frame.location

        size_and_borders = target_frame.size_and_borders
        borders = size_and_borders.borders
        frame_inner_size = size_and_borders.size

        content_location = Point(pl['x'] + borders['left'], pl['y'] + borders['top'])
        original_location = self._scroll_position.get_current_position()

        self._driver.scroll_to(content_location)
        frame = Frame(target_frame, content_location, target_frame.size, frame_inner_size,
                      parent_scroll_position=original_location)
        self._driver.frame_chain.push(frame)


class EyesWebDriver(object):
    """
    A wrapper for selenium web driver which creates wrapped elements, and notifies us about
    events / actions.
    """
    # Properties require special handling since even testing if they're callable "activates"
    # them, which makes copying them automatically a problem.
    _READONLY_PROPERTIES = ['application_cache', 'current_url', 'current_window_handle', 'desired_capabilities',
                            'log_types', 'name', 'page_source', 'title', 'window_handles', 'switch_to', 'mobile',
                            'current_context', 'context', 'current_activity', 'network_connection',
                            'available_ime_engines', 'active_ime_engine', 'device_time', 'w3c', 'contexts',
                            'current_package', ]
    _READONLY_PROPERTIES += ['battery_info']  # Appium specific
    _SETTABLE_PROPERTIES = ['orientation', 'file_detector']

    # This should pretty much cover all scroll bars (and some fixed position footer elements :) ).
    _MAX_SCROLL_BAR_SIZE = 50

    _MIN_SCREENSHOT_PART_HEIGHT = 10

    def __init__(self, driver, eyes, stitch_mode=StitchMode.Scroll):
        # type: (WebDriver, Eyes, tp.Text) -> None
        """
        Ctor.

        :param driver: remote WebDriver instance.
        :param eyes: A Eyes sdk instance.
        :param stitch_mode: How to stitch a page (default is with scrolling).
        """
        self.driver = driver
        self._eyes = eyes
        self._origin_position_provider = build_position_provider_for(StitchMode.Scroll, driver)
        self._position_provider = build_position_provider_for(stitch_mode, driver)
        # tp.List of frames the user switched to, and the current offset, so we can properly
        # calculate elements' coordinates
        self._frame_chain = FrameChain()
        self._default_content_viewport_size = None  # type: tp.Optional[ViewPort]

        self.driver_takes_screenshot = driver.capabilities.get('takesScreenshot', False)

        # Creating the rest of the driver interface by simply forwarding it to the underlying
        # driver.
        general_utils.create_proxy_interface(self, driver, self._READONLY_PROPERTIES + self._SETTABLE_PROPERTIES)

        for attr in self._READONLY_PROPERTIES:
            if not hasattr(self.__class__, attr):
                setattr(self.__class__, attr, general_utils.create_proxy_property(attr, 'driver'))
        for attr in self._SETTABLE_PROPERTIES:
            if not hasattr(self.__class__, attr):
                setattr(self.__class__, attr, general_utils.create_proxy_property(attr, 'driver', True))

    def get_display_rotation(self):
        # type: () -> int
        """
        Get the rotation of the screenshot.

        :return: The rotation of the screenshot we get from the webdriver in (degrees).
        """
        if self.platform_name == 'Android' and self.driver.orientation == "LANDSCAPE":
            return -90
        return 0

    def get_platform_name(self):
        return self.platform_name

    def get_platform_version(self):
        return self.platform_version

    @cached_property
    def platform_name(self):
        # type: () -> tp.Optional[tp.Text]
        return self.driver.desired_capabilities.get('platformName', None)

    @cached_property
    def platform_version(self):
        # type: () -> tp.Optional[tp.Text]
        return self.driver.desired_capabilities.get('platformVersion', None)

    @cached_property
    def browser_version(self):
        # type: () -> tp.Optional[float]
        caps = self.driver.capabilities
        version = caps.get('browserVersion', caps.get('version', None))
        if version:
            # convert version that has few dots in to float number (e.g. Edge 1.23.45)
            if version.find('.') != -1:
                version = float(version[:version.index('.') + 2])
            else:
                version = float(version)
        return version

    @cached_property
    def browser_name(self):
        # type: () -> tp.Optional[tp.Text]
        caps = self.driver.capabilities
        return caps.get('browserName', caps.get('browser', None))

    @cached_property
    def user_agent(self):
        try:
            user_agent = self.driver.execute_script("return navigator.userAgent")
            logger.info("user agent: {}".format(user_agent))
        except Exception:
            logger.info("Failed to obtain user-agent string")
            user_agent = None
        return user_agent

    def is_mobile_device(self):
        # type: () -> bool
        """
        Returns whether the platform running is a mobile device or not.

        :return: True if the platform running the test is a mobile platform. False otherwise.
        """
        return eyes_selenium_utils.is_mobile_device(self.driver)

    def get(self, url):
        # type: (tp.Text) -> tp.Optional[tp.Any]
        """
        Navigates the driver to the given url.

        :param url: The url to navigate to.
        :return: A driver that navigated to the given url.
        """
        # We're loading a new page, so the frame location resets
        self._frame_chain.clear()
        return self.driver.get(url)

    def find_element(self, by=By.ID, value=None):
        # type: (tp.Text, tp.Text) -> EyesWebElement
        """
        Returns a WebElement denoted by "By".

        :param by: By which option to search for (default is by ID).
        :param value: The value to search for.
        :return: A element denoted by "By".
        """
        # Get result from the original implementation of the underlying driver.
        result = self.driver.find_element(by, value)
        # Wrap the element.
        if result:
            result = EyesWebElement(result, self)
        return result

    def find_elements(self, by=By.ID, value=None):
        # type: (tp.Text, tp.Text) -> tp.List[EyesWebElement]
        """
        Returns a list of web elements denoted by "By".

        :param by: By which option to search for (default is by ID).
        :param value: The value to search for.
        :return: List of elements denoted by "By".
        """
        # Get result from the original implementation of the underlying driver.
        results = self.driver.find_elements(by, value)
        # Wrap all returned elements.
        if results:
            updated_results = []
            for element in results:
                updated_results.append(EyesWebElement(element, self))
            results = updated_results
        return results

    def find_element_by_id(self, id_):
        # type: (tp.Text) -> EyesWebElement
        """
        Finds an element by id.

        :params id_: The id of the element to be found.
        """
        return self.find_element(by=By.ID, value=id_)

    def find_elements_by_id(self, id_):
        # type: (tp.Text) -> tp.List[EyesWebElement]
        """
        Finds multiple elements by id.

        :param id_: The id of the elements to be found.
        """
        return self.find_elements(by=By.ID, value=id_)

    def find_element_by_xpath(self, xpath):
        # type: (tp.Text) -> EyesWebElement
        """
        Finds an element by xpath.

        :param xpath: The xpath locator of the element to find.
        """
        return self.find_element(by=By.XPATH, value=xpath)

    def find_elements_by_xpath(self, xpath):
        # type: (tp.Text) -> tp.List[EyesWebElement]
        """
        Finds multiple elements by xpath.

        :param xpath: The xpath locator of the elements to be found.
        """
        return self.find_elements(by=By.XPATH, value=xpath)

    def find_element_by_link_text(self, link_text):
        # type: (tp.Text) -> EyesWebElement
        """
        Finds an element by link text.

        :param link_text: The text of the element to be found.
        """
        return self.find_element(by=By.LINK_TEXT, value=link_text)

    def find_elements_by_link_text(self, text):
        # type: (tp.Text) -> tp.List[EyesWebElement]
        """
        Finds elements by link text.

        :param text: The text of the elements to be found.
        """
        return self.find_elements(by=By.LINK_TEXT, value=text)

    def find_element_by_partial_link_text(self, link_text):
        # type: (tp.Text) -> EyesWebElement
        """
        Finds an element by a partial match of its link text.

        :param link_text: The text of the element to partially match on.
        """
        return self.find_element(by=By.PARTIAL_LINK_TEXT, value=link_text)

    def find_elements_by_partial_link_text(self, link_text):
        # type: (tp.Text) -> tp.List[EyesWebElement]
        """
        Finds elements by a partial match of their link text.

        :param link_text: The text of the element to partial match on.
        """
        return self.find_elements(by=By.PARTIAL_LINK_TEXT, value=link_text)

    def find_element_by_name(self, name):
        # type: (tp.Text) -> EyesWebElement
        """
        Finds an element by name.

        :param name: The name of the element to find.
        """
        return self.find_element(by=By.NAME, value=name)

    def find_elements_by_name(self, name):
        # type: (tp.Text) -> tp.List[EyesWebElement]
        """
        Finds elements by name.

        :param name: The name of the elements to find.
        """
        return self.find_elements(by=By.NAME, value=name)

    def find_element_by_tag_name(self, name):
        # type: (tp.Text) -> EyesWebElement
        """
        Finds an element by tag name.

        :param name: The tag name of the element to find.
        """
        return self.find_element(by=By.TAG_NAME, value=name)

    def find_elements_by_tag_name(self, name):
        # type: (tp.Text) -> tp.List[EyesWebElement]
        """
        Finds elements by tag name.

        :param name: The tag name to use when finding elements.
        """
        return self.find_elements(by=By.TAG_NAME, value=name)

    def find_element_by_class_name(self, name):
        # type: (tp.Text) -> EyesWebElement
        """
        Finds an element by class name.

        :param name: The class name of the element to find.
        """
        return self.find_element(by=By.CLASS_NAME, value=name)

    def find_elements_by_class_name(self, name):
        # type: (tp.Text) -> tp.List[EyesWebElement]
        """
        Finds elements by class name.

        :param name: The class name of the elements to find.
        """
        return self.find_elements(by=By.CLASS_NAME, value=name)

    def find_element_by_css_selector(self, css_selector):
        # type: (tp.Text) -> EyesWebElement
        """
        Finds an element by css selector.

        :param css_selector: The css selector to use when finding elements.
        """
        return self.find_element(by=By.CSS_SELECTOR, value=css_selector)

    def find_elements_by_css_selector(self, css_selector):
        # type: (tp.Text) -> tp.List[EyesWebElement]
        """
        Finds elements by css selector.

        :param css_selector: The css selector to use when finding elements.
        """
        return self.find_elements(by=By.CSS_SELECTOR, value=css_selector)

    def get_screenshot_as_base64(self):
        # type: () -> tp.Text
        """
        Gets the screenshot of the current window as a base64 encoded string
           which is useful in embedded images in HTML.
        """
        screenshot64 = self.driver.get_screenshot_as_base64()
        display_rotation = self.get_display_rotation()
        if display_rotation != 0:
            logger.info('Rotation required.')
            # num_quadrants = int(-(display_rotation / 90))
            logger.debug('Done! Creating image object...')
            screenshot = image_utils.image_from_base64(screenshot64)

            # rotating
            if display_rotation == -90:
                screenshot64 = image_utils.get_base64(screenshot.rotate(90))
            logger.debug('Done! Rotating...')

        return screenshot64

    def get_screesnhot_as_base64_from_main_frame(self):
        # type: () -> tp.Text
        """
        Make screenshot from main frame
        """
        original_frame = self.frame_chain.clone()
        self.switch_to.default_content()
        screenshot64 = self.get_screenshot_as_base64()
        self.switch_to.frames(original_frame)
        return screenshot64

    def extract_full_page_width(self):
        # type: () -> int
        """
        Extracts the full page width.

        :return: The width of the full page.
        """
        # noinspection PyUnresolvedReferences
        default_scroll_width = int(round(self.driver.execute_script("return document.documentElement.scrollWidth")))
        body_scroll_width = int(round(self.driver.execute_script("return document.body.scrollWidth")))
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
        default_client_height = int(round(self.driver.execute_script("return document.documentElement.clientHeight")))
        # noinspection PyUnresolvedReferences
        default_scroll_height = int(round(self.driver.execute_script("return document.documentElement.scrollHeight")))
        # noinspection PyUnresolvedReferences
        body_client_height = int(round(self.driver.execute_script("return document.body.clientHeight")))
        # noinspection PyUnresolvedReferences
        body_scroll_height = int(round(self.driver.execute_script("return document.body.scrollHeight")))
        max_document_element_height = max(default_client_height, default_scroll_height)
        max_body_height = max(body_client_height, body_scroll_height)
        return max(max_document_element_height, max_body_height)

    def get_current_position(self):
        # type: () -> Point
        """
        Extracts the current scroll position from the browser.

        :return: The scroll position.
        """
        return self._origin_position_provider.get_current_position()

    def scroll_to(self, point):
        # type: (Point) -> None
        """
        Commands the browser to scroll to a given position.

        :param point: The point to scroll to.
        """
        self._origin_position_provider.set_position(point)

    def get_entire_page_size(self):
        # type: () -> tp.Dict[tp.Text, int]
        """
        Extracts the size of the current page from the browser using Javascript.

        :return: The page width and height.
        """
        return {
            'width':  self.extract_full_page_width(),
            'height': self.extract_full_page_height()
        }

    def set_overflow(self, overflow, stabilization_time=None):
        # type: (tp.Text, tp.Optional[int]) -> tp.Text
        """
        Sets the overflow of the current context's document element.

        :param overflow: The overflow value to set. If the given value is None, then overflow will be set to
                         undefined.
        :param stabilization_time: The time to wait for the page to stabilize after overflow is set. If the value is
                                    None, then no waiting will take place. (Milliseconds)
        :return: The previous overflow value.
        """
        logger.debug("Setting overflow: %s" % overflow)
        if overflow is None:
            script = "var origOverflow = document.documentElement.style.overflow; " \
                     "document.documentElement.style.overflow = undefined; " \
                     "return origOverflow;"
        else:
            script = "var origOverflow = document.documentElement.style.overflow; " \
                     "document.documentElement.style.overflow = \"{0}\"; " \
                     "return origOverflow;".format(overflow)
        # noinspection PyUnresolvedReferences
        original_overflow = self.driver.execute_script(script)
        logger.debug("Original overflow: %s" % original_overflow)
        if stabilization_time is not None:
            time.sleep(stabilization_time / 1000)
        return original_overflow

    def wait_for_page_load(self, timeout=3, throw_on_timeout=False):
        # type: (int, bool) -> None
        """
        Waits for the current document to be "loaded".

        :param timeout: The maximum time to wait, in seconds.
        :param throw_on_timeout: Whether to throw an exception when timeout is reached.
        """
        # noinspection PyBroadException
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete')
        except Exception:
            logger.debug('Page load timeout reached!')
            if throw_on_timeout:
                raise

    def hide_scrollbars(self):
        # type: () -> tp.Text
        """
        Hides the scrollbars of the current context's document element.

        :return: The previous value of the overflow property (could be None).
        """
        logger.debug('HideScrollbars() called. Waiting for page load...')
        self.wait_for_page_load()
        logger.debug('About to hide scrollbars')
        return self.set_overflow('hidden')

    @property
    def frame_chain(self):
        """
        Gets the frame chain.

        :return: A list of Frame instances which represents the path to the current frame.
            This can later be used as an argument to _EyesSwitchTo.frames().
        """
        return self._frame_chain

    def get_viewport_size(self):
        # type: () -> ViewPort
        """
        Returns:
            The viewport size of the current frame.
        """
        return eyes_selenium_utils.get_viewport_size(self)

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
        self._default_content_viewport_size = eyes_selenium_utils.get_viewport_size_or_display_size(self.driver)

        if current_frames:
            self.switch_to.frames(current_frames)

        return self._default_content_viewport_size

    def reset_origin(self):
        # type: () -> None
        """
        Reset the origin position to (0, 0).

        :raise EyesError: Couldn't scroll to position (0, 0).
        """
        self._origin_position_provider.push_state()
        self._origin_position_provider.set_position(Point(0, 0))
        current_scroll_position = self._origin_position_provider.get_current_position()
        if current_scroll_position.x != 0 or current_scroll_position.y != 0:
            self._origin_position_provider.pop_state()
            raise EyesError("Couldn't scroll to the top/left part of the screen!")

    def restore_origin(self):
        # type: () -> None
        """
        Restore the origin position.
        """
        self._origin_position_provider.pop_state()

    def save_position(self):
        """
        Saves the position in the _position_provider list.
        """
        self._position_provider.push_state()

    def restore_position(self):
        """
        Restore the position.
        """
        self._position_provider.pop_state()

    @staticmethod
    def _wait_before_screenshot(seconds):
        logger.debug("Waiting {} ms before taking screenshot..".format(int(seconds * 1000)))
        time.sleep(seconds)
        logger.debug("Finished waiting!")

    def get_full_page_screenshot(self, wait_before_screenshots, scale_provider):
        # type: (Num, ScaleProvider) -> Image.Image
        """
        Gets a full page screenshot.

        :param wait_before_screenshots: Seconds to wait before taking each screenshot.
        :return: The full page screenshot.
        """
        logger.info('getting full page screenshot..')

        # Saving the current frame reference and moving to the outermost frame.
        original_frame = self.frame_chain
        self.switch_to.default_content()

        self.reset_origin()

        entire_page_size = self.get_entire_page_size()

        # Starting with the screenshot at 0,0
        EyesWebDriver._wait_before_screenshot(wait_before_screenshots)
        part64 = self.get_screenshot_as_base64()
        screenshot = image_utils.image_from_bytes(base64.b64decode(part64))

        scale_provider.update_scale_ratio(screenshot.width)
        pixel_ratio = 1.0 / scale_provider.scale_ratio
        need_to_scale = True if pixel_ratio != 1.0 else False
        if need_to_scale:
            screenshot = image_utils.scale_image(screenshot, 1.0 / pixel_ratio)

        # IMPORTANT This is required! Since when calculating the screenshot parts for full size,
        # we use a screenshot size which is a bit smaller (see comment below).
        if (screenshot.width >= entire_page_size['width']) and (screenshot.height >= entire_page_size['height']):
            self.restore_origin()
            self.switch_to.frames(original_frame)

            return screenshot

        #  We use a smaller size than the actual screenshot size in order to eliminate duplication
        #  of bottom scroll bars, as well as footer-like elements with fixed position.
        screenshot_part_size = {
            'width':  screenshot.width,
            'height': max(screenshot.height - self._MAX_SCROLL_BAR_SIZE, self._MIN_SCREENSHOT_PART_HEIGHT)
        }

        logger.debug("Total size: {0}, Screenshot part size: {1}".format(entire_page_size, screenshot_part_size))

        entire_page = Region(0, 0, entire_page_size['width'], entire_page_size['height'])
        screenshot_parts = entire_page.get_sub_regions(screenshot_part_size)

        # Starting with the screenshot we already captured at (0,0).
        stitched_image = Image.new('RGBA', (entire_page.width, entire_page.height))
        stitched_image.paste(screenshot, box=(0, 0))
        self.save_position()

        for part in screenshot_parts:
            # Since we already took the screenshot for 0,0
            if part.left == 0 and part.top == 0:
                logger.debug('Skipping screenshot for 0,0 (already taken)')
                continue
            logger.debug("Taking screenshot for {0}".format(part))
            # Scroll to the part's top/left and give it time to stabilize.
            self.scroll_to(Point(part.left, part.top))
            EyesWebDriver._wait_before_screenshot(wait_before_screenshots)
            # Since screen size might cause the scroll to reach only part of the way
            current_scroll_position = self.get_current_position()
            logger.debug("Scrolled To ({0},{1})".format(current_scroll_position.x, current_scroll_position.y))
            part64 = self.get_screenshot_as_base64()
            part_image = image_utils.image_from_bytes(base64.b64decode(part64))

            if need_to_scale:
                part_image = image_utils.scale_image(part_image, 1.0 / pixel_ratio)

            stitched_image.paste(part_image, box=(current_scroll_position.x, current_scroll_position.y))

        self.restore_position()
        self.restore_origin()
        self.switch_to.frames(original_frame)

        return stitched_image

    def get_stitched_screenshot(self, element_region, wait_before_screenshots, scale_provider):
        # type: (Region, int, ScaleProvider) -> Image.Image
        """
        Gets a stitched screenshot for specific element

        :param element_region: Region of required screenshot
        :param wait_before_screenshots: Seconds to wait before taking each screenshot.
        :param scale_provider: Scale image if needed.
        :return: The full element screenshot.
        """
        logger.info('getting stitched element screenshot..')
        self._position_provider = self._eyes._element_position_provider
        entire_size = self._position_provider.get_entire_size()
        logger.debug("Element region: {}".format(element_region))
        # Firefox 60 and above make a screenshot of the current frame when other browsers
        # make a screenshot of the viewport. So we scroll down to frame at _will_switch_to method
        # and add a left margin here.
        # TODO: Refactor code. Use EyesScreenshot
        if self._frame_chain:
            if ((self.browser_name == 'firefox' and self.browser_version < 60.0)
                    or self.browser_name in ('chrome', 'MicrosoftEdge', 'internet explorer', 'safari')):
                element_region.left += int(self._frame_chain.peek.location.x)

        screenshot_part_size = {
            'width':  element_region.width,
            'height': max(element_region.height - self._MAX_SCROLL_BAR_SIZE, self._MIN_SCREENSHOT_PART_HEIGHT)
        }
        entire_element = Region(0, 0, entire_size['width'], entire_size['height'])

        screenshot_parts = entire_element.get_sub_regions(screenshot_part_size)
        viewport = self.get_viewport_size()
        screenshot = image_utils.image_from_bytes(base64.b64decode(self.get_screenshot_as_base64()))
        scale_provider.update_scale_ratio(screenshot.width)
        pixel_ratio = 1 / scale_provider.scale_ratio
        need_to_scale = True if pixel_ratio != 1.0 else False

        if need_to_scale:
            element_region = element_region.scale(scale_provider.device_pixel_ratio)

        # Starting with element region size part of the screenshot. Use it as a size template.
        stitched_image = Image.new('RGBA', (entire_element.width, entire_element.height))
        for part in screenshot_parts:
            logger.debug("Taking screenshot for {0}".format(part))
            # Scroll to the part's top/left and give it time to stabilize.
            self._position_provider.set_position(Point(part.left, part.top))
            EyesWebDriver._wait_before_screenshot(wait_before_screenshots)
            # Since screen size might cause the scroll to reach only part of the way
            current_scroll_position = self._position_provider.get_current_position()
            logger.debug("Scrolled To ({0},{1})".format(current_scroll_position.x, current_scroll_position.y))
            part64 = self.get_screenshot_as_base64()
            part_image = image_utils.image_from_bytes(base64.b64decode(part64))
            # Cut to viewport size the full page screenshot of main frame for some browsers
            if self._frame_chain:
                if (self.browser_name == 'firefox' and self.browser_version < 60.0
                        or self.browser_name in ('internet explorer', 'safari')):
                    # TODO: Refactor this to make main screenshot only once
                    frame_scroll_position = int(self._frame_chain.peek.location.y)
                    part_image = image_utils.get_image_part(part_image,
                                                            Region(top=frame_scroll_position, height=viewport['height'],
                                                                   width=viewport['width']))
            # We cut original image before scaling to prevent appearing of artifacts
            part_image = image_utils.get_image_part(part_image, element_region)
            if need_to_scale:
                part_image = image_utils.scale_image(part_image, 1.0 / pixel_ratio)

            # first iteration
            if stitched_image is None:
                stitched_image = part_image
                continue
            stitched_image.paste(part_image, box=(current_scroll_position.x, current_scroll_position.y))

        self._position_provider = self._origin_position_provider
        return stitched_image

    @property
    def switch_to(self):
        return _EyesSwitchTo(self, self.driver.switch_to)

    @property
    def current_offset(self):
        # type: () -> Point
        """
        Return the current offset of the context we're in (e.g., due to switching into frames)
        """
        x, y = 0, 0
        for frame in self._frame_chain:
            x += frame.location['x']
            y += frame.location['y']
        return Point(x, y)

    def execute_script(self, script, *args):
        return self.driver.execute_script(script, *args)

    def get_window_size(self, windowHandle='current'):
        return self.driver.get_window_size(windowHandle)

    def set_window_size(self, width, height, windowHandle='current'):
        self.driver.set_window_size(width, height, windowHandle)

    def set_window_position(self, x, y, windowHandle='current'):
        self.driver.set_window_position(x, y, windowHandle)
