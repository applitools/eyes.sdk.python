from __future__ import absolute_import

import time
import typing as tp
from contextlib import contextmanager

from appium.webdriver import Remote as AppiumWebDriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from applitools.common import Point, RectangleSize, logger

if tp.TYPE_CHECKING:
    from typing import Text, Optional, Any, Union, Generator
    from applitools.core import PositionProvider
    from applitools.selenium.webdriver import EyesWebDriver
    from applitools.selenium.webelement import EyesWebElement
    from applitools.selenium.fluent import SeleniumCheckSettings, FrameLocator
    from applitools.common.utils.custom_types import (
        AnyWebDriver,
        ViewPort,
        AnyWebElement,
        Num,
    )

__all__ = (
    "get_current_frame_content_entire_size",
    "get_device_pixel_ratio",
    "get_viewport_size",
    "get_window_size",
    "set_window_size",
    "set_browser_size",
    "set_browser_size_by_viewport_size",
    "set_viewport_size",
    "hide_scrollbars",
    "set_overflow",
    "parse_location_string",
)

_NATIVE_APP = "NATIVE_APP"
_JS_GET_VIEWPORT_SIZE = """
    var height = undefined;
    var width = undefined;
    if (window.innerHeight) {
        height = window.innerHeight;
    } else if (document.documentElement && document.documentElement.clientHeight) {
        height = document.documentElement.clientHeight;
    } else {
            var b = document.getElementsByTagName('body')[0];
            if (b.clientHeight) {height = b.clientHeight;}
        }
    if (window.innerWidth) {
        width = window.innerWidth;
    } else if (document.documentElement && document.documentElement.clientWidth) {
        width = document.documentElement.clientWidth;
    } else {
        var b = document.getElementsByTagName('body')[0];
    if (b.clientWidth) {
        width = b.clientWidth;}
    }
    return [width, height];"""

_JS_GET_CURRENT_SCROLL_POSITION = """
    var doc = document.documentElement;
    var x = window.scrollX || ((window.pageXOffset || doc.scrollLeft) - (doc.clientLeft || 0));
    var y = window.scrollY || ((window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0));
    return [x, y]"""

_JS_GET_CONTENT_ENTIRE_SIZE = """
    var scrollWidth = document.documentElement.scrollWidth;
    var bodyScrollWidth = document.body.scrollWidth;
    var totalWidth = Math.max(scrollWidth, bodyScrollWidth);
    var clientHeight = document.documentElement.clientHeight;
    var bodyClientHeight = document.body.clientHeight;
    var scrollHeight = document.documentElement.scrollHeight;
    var bodyScrollHeight = document.body.scrollHeight;
    var maxDocElementHeight = Math.max(clientHeight, scrollHeight);
    var maxBodyHeight = Math.max(bodyClientHeight, bodyScrollHeight);
    var totalHeight = Math.max(maxDocElementHeight, maxBodyHeight);
    return [totalWidth, totalHeight];";
"""
_JS_SET_OVERFLOW = """
var origOF = arguments[0].style.overflow;
arguments[0].style.overflow = '%s';
return origOF;
if ('%s'.toUpperCase() === 'HIDDEN' && origOF.toUpperCase() !== 'HIDDEN')
arguments[0].setAttribute('data-applitools-original-overflow',origOF);
return origOF;
"""
_JS_DATA_APPLITOOLS_SCROLL = (
    "arguments[0].setAttribute('data-applitools-scroll', 'true');"
)
_JS_DATA_APPLITOOLS_ORIGINAL_OVERFLOW = (
    "arguments[0].setAttribute('data-applitools-original-overflow', '%s');"
)
_JS_TRANSFORM_KEYS = ("transform", "-webkit-transform")
_OVERFLOW_HIDDEN = "hidden"
_MAX_DIFF = 3
_SLEEP_SEC = 1
_RETRIES = 3


def is_mobile_platform(driver):
    # type: (AnyWebDriver) -> bool
    """
    Returns whether the platform running is a mobile browser or app.
    """
    driver = get_underlying_driver(driver)
    if isinstance(driver, AppiumWebDriver):
        return True
    return is_mobile_web(driver) or is_mobile_app(driver)


def is_mobile_web(driver):
    # type: (AnyWebDriver) -> bool
    """
    Returns whether the platform running is a mobile browser.
    """
    # if driver is selenium based
    platform_name = driver.desired_capabilities.get("platformName", "").lower()
    browser_name = driver.desired_capabilities.get("browserName", "").lower()
    is_mobile = "android" in platform_name or "ios" in platform_name
    if is_mobile and browser_name:
        return True
    return False


def is_mobile_app(driver):
    # type: (AnyWebDriver) -> bool
    """
    Returns whether the platform running is a mobile app.
    """
    platform_name = driver.desired_capabilities.get("platformName", "").lower()
    browser_name = driver.desired_capabilities.get("browserName", "").lower()
    app = driver.desired_capabilities.get("app", None)
    is_mobile = "android" in platform_name or "ios" in platform_name
    if is_mobile and app and not browser_name:
        return True
    return False


def get_underlying_driver(driver):
    # type: (AnyWebDriver) -> tp.Union[WebDriver, AppiumWebDriver]
    from applitools.selenium.webdriver import EyesWebDriver

    if isinstance(driver, EyesWebDriver):
        driver = driver._driver
    return driver


def get_underlying_webelement(element):
    # type: (AnyWebElement) -> WebElement
    from applitools.selenium.webelement import EyesWebElement

    if isinstance(element, EyesWebElement):
        element = element.element
    return element


def get_current_frame_content_entire_size(driver):
    # type: (AnyWebDriver) -> ViewPort
    """
    :return: The size of the entire content.
    """
    try:
        width, height = driver.execute_script(_JS_GET_CONTENT_ENTIRE_SIZE)
    except WebDriverException:
        raise WebDriverException("Failed to extract entire size!")
    return RectangleSize(width, height)


def get_device_pixel_ratio(driver):
    # type: (AnyWebDriver) -> float
    return driver.execute_script("return window.devicePixelRatio;")


def get_viewport_size(driver):
    # type: (AnyWebDriver) -> RectangleSize
    """
    Tries to get the viewport size using Javascript. If fails, gets the entire browser window
    size!

    :param driver: The webdriver to use for getting the viewport size.
    """
    # noinspection PyBroadException
    try:
        width, height = driver.execute_script(_JS_GET_VIEWPORT_SIZE)
        return RectangleSize(width=width, height=height)
    except WebDriverException:
        logger.warning("Failed to get viewport size. Only window size is available")
        return get_window_size(driver)


def get_window_size(driver):
    # type: (AnyWebDriver) -> RectangleSize
    return driver.get_window_size()


def set_window_size(driver, size):
    # type: (AnyWebDriver, ViewPort) -> None
    driver.set_window_size(size["width"], size["height"])


def set_browser_size(driver, required_size):
    # type: (AnyWebDriver, ViewPort) -> bool

    retries_left = _RETRIES

    # set browser size for mobile devices isn't working
    if is_mobile_web(driver):
        return True

    while True:
        logger.info("Trying to set browser size to: " + str(required_size))
        set_window_size(driver, required_size)
        time.sleep(_SLEEP_SEC)
        current_size = get_window_size(driver)
        logger.info("Current browser size: " + str(required_size))

        if retries_left or current_size != required_size:
            break
        retries_left -= 1

    return current_size == required_size


def set_browser_size_by_viewport_size(driver, actual_viewport_size, required_size):
    # type: (AnyWebDriver, ViewPort, ViewPort) -> bool

    browser_size = get_window_size(driver)
    logger.debug("Current browser size: {}".format(browser_size))
    required_browser_size = dict(
        width=browser_size["width"]
        + (required_size["width"] - actual_viewport_size["width"]),
        height=browser_size["height"]
        + (required_size["height"] - actual_viewport_size["height"]),
    )
    return set_browser_size(driver, required_browser_size)


def set_viewport_size(driver, required_size):
    # type: (AnyWebDriver, ViewPort) -> None

    logger.debug("set_viewport_size({})".format(str(required_size)))

    actual_viewport_size = get_viewport_size(driver)
    if actual_viewport_size == required_size:
        logger.info("Required size already set.")
        return None

    try:
        # We move the window to (0,0) to have the best chance to be able to
        # set the viewport size as requested.
        driver.set_window_position(0, 0)
    except WebDriverException:
        logger.warning("Failed to move the browser window to (0,0)")
    set_browser_size_by_viewport_size(driver, actual_viewport_size, required_size)
    actual_viewport_size = get_viewport_size(driver)
    if actual_viewport_size == required_size:
        return None

    # Additional attempt. This Solves the "maximized browser" bug
    # (border size for maximized browser sometimes different than
    # non-maximized, so the original browser size calculation is
    # wrong).
    logger.info("Trying workaround for maximization...")
    set_browser_size_by_viewport_size(driver, actual_viewport_size, required_size)
    actual_viewport_size = get_viewport_size(driver)
    logger.debug("Current viewport size: {}".format(actual_viewport_size))
    if actual_viewport_size == required_size:
        return None

    width_diff = abs(actual_viewport_size["width"] - required_size["width"])
    width_step = -1 if width_diff > 0 else 1  # -1 for smaller size, 1 for larger
    height_diff = abs(actual_viewport_size["height"] - required_size["height"])
    height_step = -1 if height_diff > 0 else 1

    browser_size = get_window_size(driver)
    curr_width_change = 0
    curr_height_change = 0

    if width_diff <= _MAX_DIFF and height_diff <= _MAX_DIFF:
        logger.info("Trying workaround for zoom...")
        last_required_browser_size = None

        while (
            abs(curr_width_change) <= width_diff
            and abs(curr_height_change) <= height_diff
        ):
            if abs(curr_width_change) <= width_diff:
                curr_width_change += width_step
            if abs(curr_height_change) <= height_diff:
                curr_height_change += height_step

            required_browser_size = dict(
                width=browser_size["width"] + curr_width_change,
                height=browser_size["height"] + curr_height_change,
            )
            if required_browser_size == last_required_browser_size:
                logger.info(
                    "Browser size is as required but viewport size does not match!"
                )
                logger.info(
                    "Browser size: {}, Viewport size: {}".format(
                        required_browser_size, actual_viewport_size
                    )
                )
                logger.info("Stopping viewport size attempts.")
                break

            set_browser_size(driver, required_browser_size)
            last_required_browser_size = required_browser_size

            actual_viewport_size = get_viewport_size(driver)
            logger.info("Current viewport size: {}".format(actual_viewport_size))

            if actual_viewport_size == required_size:
                return None
        else:
            logger.info("Zoom workaround failed.")
    raise WebDriverException("Failed to set the viewport size.")


def hide_scrollbars(driver, root_element):
    # type: (EyesWebDriver, AnyWebElement) -> Text
    return set_overflow_and_add_attribute(driver, _OVERFLOW_HIDDEN, root_element)


def return_to_original_overflow(driver, root_element, origin_overflow):
    # type: (EyesWebDriver, AnyWebElement, Text) -> Text
    return set_overflow(driver, origin_overflow, root_element)


def set_overflow(driver, overflow, root_element):
    # type: (EyesWebDriver, Text, AnyWebElement) -> Optional[Text]
    root_element = get_underlying_webelement(root_element)
    with timeout(0.1):
        try:
            return driver.execute_script(
                _JS_SET_OVERFLOW % (overflow, overflow), root_element
            )
        except WebDriverException as e:
            logger.warning(
                "Couldn't sent overflow {} to element {}".format(overflow, root_element)
            )
            logger.exception(e)
    return None


def set_overflow_and_add_attribute(driver, overflow, root_element):
    # type: (EyesWebDriver, Text, AnyWebElement) -> Text
    overflow = set_overflow(driver, overflow, root_element)
    add_data_overflow_to_element(driver, root_element, overflow)
    return overflow


def add_data_overflow_to_element(driver, element, overflow):
    # type: (EyesWebDriver, EyesWebElement, Text) -> Optional[Any]
    if element is None:
        element = driver.find_element_by_tag_name("html")
    element = get_underlying_webelement(element)
    return driver.execute_script(
        _JS_DATA_APPLITOOLS_ORIGINAL_OVERFLOW % overflow, element
    )


def add_data_scroll_to_element(driver, element):
    # type: (EyesWebDriver, WebElement) -> Optional[Any]
    return driver.execute_script(_JS_DATA_APPLITOOLS_SCROLL, element)


@contextmanager
def timeout(timeout):
    # type: (Num) -> Generator
    time.sleep(timeout)
    yield


def is_landscape_orientation(driver):
    if is_mobile_web(driver):
        # could be AppiumRemoteWebDriver
        appium_driver = get_underlying_driver(
            driver
        )  # type: tp.Union[AppiumWebDriver, WebDriver]

        try:
            # We must be in native context in order to ask for orientation,
            # because of an Appium bug.
            original_context = appium_driver.context
            if (
                len(appium_driver.contexts) > 1
                and not original_context.uppar() == "NATIVE_APP"
            ):
                appium_driver.switch_to.context("NATIVE_APP")
            else:
                original_context = None
        except WebDriverException:
            original_context = None

        try:
            orieintation = appium_driver.orientation
            return orieintation.lower() == "landscape"
        except WebDriverException:
            logger.warning("Couldn't get device orientation. Assuming Portrait.")
        finally:
            if original_context is not None:
                appium_driver.switch_to.context(original_context)

        return False


def get_viewport_size_or_display_size(driver):
    logger.debug("get_viewport_size_or_display_size()")

    try:
        return get_viewport_size(driver)
    except Exception as e:
        logger.warning(
            "Failed to extract viewport size using Javascript: {}".format(str(e))
        )
    # If we failed to extract the viewport size using JS, will use the
    # window size instead.

    logger.debug("Using window size as viewport size.")
    window_size = get_window_size(driver)
    width = window_size["width"]
    height = window_size["height"]
    try:
        if is_landscape_orientation(driver) and height > width:
            height, width = width, height
    except WebDriverException:
        # Not every WebDriver supports querying for orientation.
        pass
    logger.debug("Done! Size {:d} x {:d}".format(width, height))
    return RectangleSize(width=width, height=height)


def parse_location_string(position):
    # type: (Text) -> Point
    xy = position.split(";")
    if len(xy) != 2:
        raise WebDriverException("Could not get scroll position!")
    return Point(float(xy[0]), float(xy[1]))


def get_current_position(driver, element):
    # type: (AnyWebDriver, AnyWebElement) -> Point
    element = get_underlying_webelement(element)
    xy = driver.execute_script(
        "return arguments[0].scrollLeft+';'+arguments[0].scrollTop;", element
    )
    return parse_location_string(xy)


@contextmanager
def get_and_restore_state(position_provider):
    # type: (PositionProvider)-> Generator
    state = position_provider.get_state()
    yield state
    position_provider.restore_state(state)


def scroll_root_element_from(driver, container=None):
    # type: (EyesWebDriver, Union[SeleniumCheckSettings, FrameLocator]) -> EyesWebElement
    def root_html():
        # type: () -> EyesWebElement
        return driver.find_element_by_tag_name("html")

    scroll_root_element = None
    if not driver.is_mobile_app:
        if container is None:
            scroll_root_element = root_html()
        else:
            if hasattr(container, "values"):
                # check settings
                container = container.values  # type: ignore
            scroll_root_element = container.scroll_root_element  # type: ignore
            if not scroll_root_element:
                scroll_root_selector = container.scroll_root_selector  # type: ignore
                if scroll_root_selector:
                    scroll_root_element = driver.find_element_by_css_selector(
                        scroll_root_selector
                    )
                else:
                    scroll_root_element = root_html()
    return scroll_root_element


def curr_frame_scroll_root_element(driver, scroll_root_element=None):
    # type: (EyesWebDriver, Optional[AnyWebElement]) -> EyesWebElement
    fc = driver.frame_chain.clone()
    cur_frame = fc.peek
    root_element = None
    if cur_frame:
        root_element = cur_frame.scroll_root_element
    if root_element is None and not driver.is_mobile_app:
        if scroll_root_element:
            root_element = scroll_root_element
        else:
            root_element = driver.find_element_by_tag_name("html")
    return root_element
