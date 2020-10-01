from __future__ import absolute_import

import json
import threading
import typing as tp
from collections import OrderedDict
from contextlib import contextmanager

from appium.webdriver import Remote as AppiumWebDriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from applitools.common import EyesError, Point, RectangleSize, logger
from applitools.common.utils import datetime_utils
from applitools.common.utils.compat import urlparse, raise_from

if tp.TYPE_CHECKING:
    from typing import Any, Dict, Generator, Optional, Text, Union

    from applitools.common.utils.custom_types import (
        AnyWebDriver,
        AnyWebElement,
        Num,
        ViewPort,
    )
    from applitools.core import PositionProvider
    from applitools.selenium.fluent import FrameLocator, SeleniumCheckSettings
    from applitools.selenium.frames import FrameChain
    from applitools.selenium.positioning import SeleniumPositionProvider
    from applitools.selenium.webdriver import EyesWebDriver
    from applitools.selenium.webelement import EyesWebElement

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
    "get_cur_position_provider",
    "get_updated_scroll_position",
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
_SLEEP_MS = 1000
_RETRIES = 3


class SwitchToParentIsNotSupported(Exception):
    pass


class EyesWebDriverIsOutOfSync(Exception):
    pass


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


def is_android(driver):
    return "android" in driver.desired_capabilities.get("platformName", "").lower()


def is_mobile_app(driver):
    # type: (AnyWebDriver) -> bool
    """
    Returns whether the platform running is a mobile app.
    """
    caps = driver.desired_capabilities
    platform_name = caps.get("platformName", "").lower()
    browser_name = caps.get("browserName", "").lower()
    is_app = any(
        param in caps
        for param in ["app", "appActivity", "appPackage", "bundleId", "appName"]
    )
    is_mobile = "android" in platform_name or "ios" in platform_name
    if is_mobile and is_app and not browser_name:
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
    width, height = driver.execute_script(_JS_GET_VIEWPORT_SIZE)
    return RectangleSize(width=width, height=height)


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
    if is_mobile_platform(driver):
        return True

    while True:
        logger.debug("Trying to set browser size to: " + str(required_size))
        set_window_size(driver, required_size)
        datetime_utils.sleep(_SLEEP_MS)
        current_size = get_window_size(driver)
        logger.debug("Current browser size: " + str(current_size))

        if retries_left or current_size != required_size:
            break
        retries_left -= 1

    if current_size == required_size:
        logger.debug(
            "Browser size has been successfully set to {}".format(current_size)
        )
        return True
    logger.debug("Browser size wasn't set: {}".format(current_size))
    return False


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
    set_browser_size(driver, required_browser_size)
    # Browser size and Viewport size are different things.
    # We need to compare the by Viewport sizes to be sure that it fit.
    actual_viewport_size = get_viewport_size(driver)
    logger.info("Current viewport size: {}".format(actual_viewport_size))
    return actual_viewport_size == required_size


def set_viewport_size(driver, required_size):  # noqa
    # type: (AnyWebDriver, ViewPort) -> None
    actual_viewport_size = get_viewport_size(driver)
    if actual_viewport_size == required_size:
        logger.info("Required viewport size already set")
        return None
    logger.info(
        "Actual Viewport Size: {}\n\tTrying to set viewport size to: {}".format(
            str(actual_viewport_size), str(required_size)
        )
    )

    try:
        # We move the window to (0,0) to have the best chance to be able to
        # set the viewport size as requested.
        driver.set_window_position(0, 0)
    except WebDriverException:
        logger.warning("Failed to move the browser window to (0,0)")
    if set_browser_size_by_viewport_size(driver, actual_viewport_size, required_size):
        return None

    # Additional attempt. This Solves the "maximized browser" bug
    # (border size for maximized browser sometimes different than
    # non-maximized, so the original browser size calculation is
    # wrong).
    logger.info("Trying workaround for maximization...")
    actual_viewport_size = get_viewport_size(driver)
    width_diff = abs(actual_viewport_size["width"] - required_size["width"])
    width_step = -1 if width_diff > 0 else 1  # -1 for smaller size, 1 for larger
    height_diff = abs(actual_viewport_size["height"] - required_size["height"])
    height_step = -1 if height_diff > 0 else 1

    browser_size = get_window_size(driver)
    curr_width_change = curr_height_change = 0

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

    # Attempt to fix by minimizing window
    logger.info("Trying workaround for minimization...")
    try:
        # some webdriver's don't support minimize_window
        driver.minimize_window()
    except WebDriverException as e:
        logger.exception(e)
    if set_browser_size_by_viewport_size(driver, actual_viewport_size, required_size):
        return None
    logger.error("Minimization workaround failed.")
    raise EyesError("Failed to set the viewport size.")


def hide_scrollbars(driver, root_element):
    # type: (EyesWebDriver, AnyWebElement) -> Text
    return set_overflow_and_add_attribute(driver, _OVERFLOW_HIDDEN, root_element)


def return_to_original_overflow(driver, root_element, origin_overflow):
    # type: (EyesWebDriver, AnyWebElement, Text) -> Text
    return set_overflow(driver, origin_overflow, root_element)


def set_overflow(driver, overflow, root_element):
    # type: (EyesWebDriver, Text, AnyWebElement) -> Optional[Text]
    root_element = get_underlying_webelement(root_element)
    with timeout(100):
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
def timeout(timeout_ms):
    # type: (Num) -> Generator
    datetime_utils.sleep(timeout_ms)
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
                and not original_context.upper() == "NATIVE_APP"
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

    if not is_mobile_app(driver):
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
    # type: (Union[Text, Dict]) -> Point
    if isinstance(position, dict):
        return Point.from_(position)
    xy = position.split(";")
    if len(xy) != 2:
        raise WebDriverException("Could not get scroll position!")
    return Point(round(float(xy[0])), round(float(xy[1])))


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
                    by, value = scroll_root_selector
                    scroll_root_element = driver.find_element(by, value)
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


def get_cur_position_provider(driver):
    # type: (EyesWebDriver) -> SeleniumPositionProvider
    cur_frame_position_provider = driver.eyes.current_frame_position_provider
    if cur_frame_position_provider:
        return cur_frame_position_provider
    else:
        return driver.eyes.position_provider


def get_updated_scroll_position(position_provider):
    # type: (SeleniumPositionProvider) -> Point
    try:
        sp = position_provider.get_current_position()
        if not sp:
            sp = Point.ZERO()
    except WebDriverException:
        sp = Point.ZERO()

    return sp


def get_default_content_scroll_position(current_frames, driver):
    # type: (FrameChain, EyesWebDriver) -> Point
    if current_frames.size == 0:

        scroll_position = get_current_position(
            driver, curr_frame_scroll_root_element(driver)
        )
    else:
        current_fc = driver.eyes.original_fc
        with driver.switch_to.frames_and_back(current_fc):
            scroll_position = get_current_position(
                driver, curr_frame_scroll_root_element(driver)
            )
    return scroll_position


def get_dom_script_result(driver, dom_extraction_timeout, timer_name, script_for_run):
    # type: (AnyWebDriver, int, Text, Text) -> Dict
    is_check_timer_timeout = []
    script_response = {}
    status = None

    def start_timer():
        def set_timer():
            is_check_timer_timeout.append(True)

        timer = threading.Timer(
            datetime_utils.to_sec(dom_extraction_timeout), set_timer
        )
        timer.daemon = True
        timer.setName(timer_name)
        timer.start()
        return timer

    timer = start_timer()
    while True:
        if status == "SUCCESS" or is_check_timer_timeout:
            del is_check_timer_timeout[:]
            break
        script_result_string = driver.execute_script(script_for_run)
        try:
            script_response = json.loads(
                script_result_string, object_pairs_hook=OrderedDict
            )
            status = script_response.get("status")
        except Exception as e:
            logger.exception(e)
        datetime_utils.sleep(1000, "Waiting for the end of DOM extraction")
    timer.cancel()
    script_result = script_response.get("value")
    if script_result is None or status == "ERROR":
        raise EyesError("Failed to capture script_result")
    return script_result


def get_app_name(driver):
    caps = driver.desired_capabilities
    return caps.get("appPackage", None) or caps.get("app", "").split("/")[-1] or None


def get_webapp_domain(driver):
    return urlparse(driver.current_url).hostname


def get_check_source(driver):
    return get_app_name(driver) if is_mobile_app(driver) else get_webapp_domain(driver)


def ensure_sync_with_underlying_driver(eyes_driver, selenium_driver):
    # type: (EyesWebDriver) -> None
    """
    Checks if frame selected in selenium_driver matches frame_chain in eyes_driver.
    If it doesn't, follows parent frames up to default content and then repeats
    all the chain of frame selections with eyes_driver.
    """
    if not eyes_driver.is_mobile_app:
        try:
            if eyes_driver.frame_chain.size == 0:
                in_sync = _has_no_frame_selected(selenium_driver)
            else:
                selected_frame = eyes_driver.frame_chain.peek
                in_sync = selected_frame.scroll_root_element.is_attached_to_page
        except SwitchToParentIsNotSupported:
            logger.info(
                "Unable to ensure frame chain sync with the underlying driver due to "
                "unsupported 'switch to parent frame' call in the driver"
            )
        if not in_sync:
            try:
                _do_sync_with_underlying_driver(eyes_driver, selenium_driver)
            except Exception as e:
                raise_from(
                    EyesWebDriverIsOutOfSync(
                        "EyesWebDriver frame chain is out of sync. "
                        "Please use web driver returned by Eyes.open call "
                        "for frame switching."
                    ),
                    e,
                )


def _has_no_frame_selected(driver):
    # type: (WebDriver) -> bool
    """
    Predicate that checks if given selenium driver has no frame selected (in other
    words, default content is selected)
    """
    root_element = _current_root_element(driver)
    _swith_to_parent_frame(driver)
    parent_element = _current_root_element(driver)
    if root_element == parent_element:
        return True
    else:
        _switch_to_frame_with_root_element(driver, root_element)
        return False


def _do_sync_with_underlying_driver(eyes_driver, selenium_driver):
    # type: (EyesWebDriver, WebDriverException) -> None
    """
    Goes from currently selected frame in selenium_driver up to
    the topmost default content and remembers the trace.
    Then follows that trace with eyes_driver to get to original frame and have
    frame_chain synchronized.
    """
    root_elements_trace = [_current_root_element(selenium_driver)]
    while True:
        _swith_to_parent_frame(selenium_driver)
        root_element = _current_root_element(selenium_driver)
        if root_element != root_elements_trace[-1]:
            root_elements_trace.append(root_element)
        else:
            root_elements_trace.pop()
            break
    eyes_driver.frame_chain.clear()
    for root_element in reversed(root_elements_trace):
        _switch_to_frame_with_root_element(eyes_driver, root_element)


def _switch_to_frame_with_root_element(driver, root_element):
    # type: (AnyWebDriver, AnyWebElement) -> None
    """
    Tries to find and switch given driver to a frame that has given root_element
    as it's root element.
    """
    for frame in driver.find_elements_by_xpath("//iframe|//frame"):
        driver.switch_to.frame(frame)
        if _current_root_element(driver) == root_element:
            break
        else:
            _swith_to_parent_frame(driver)
    else:
        raise RuntimeError("Failed to reach element {}".format(root_element))


def _current_root_element(driver):
    # type: (WebDriver) -> WebElement
    """
    Finds root WebElement within currently selected frame in given driver.
    Usually it's the 'html' element.
    """
    return driver.find_element_by_xpath("/*")


def _swith_to_parent_frame(driver):
    # type: (WebDriver) -> None
    """
    Switches given driver to the parent frame or raises specific exception
    """
    try:
        driver.switch_to.parent_frame()
    except WebDriverException as e:
        if "Method is not implemented" in e.msg:
            raise_from(SwitchToParentIsNotSupported, e)
        else:
            raise
