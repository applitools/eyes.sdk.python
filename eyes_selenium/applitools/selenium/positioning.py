from __future__ import absolute_import

import typing

from selenium.common.exceptions import WebDriverException

from applitools.common import EyesError, Point, StitchMode, logger
from applitools.common.geometry import RectangleSize
from applitools.core import PositionMemento, PositionProvider

from . import eyes_selenium_utils
from .useragent import BrowserNames, OSNames

if typing.TYPE_CHECKING:
    from typing import Optional

    from applitools.common.utils.custom_types import AnyWebDriver, AnyWebElement

    from . import EyesWebDriver, EyesWebElement


class SeleniumPositionProvider(PositionProvider):
    """ Encapsulates page/element positioning """

    _JS_GET_ENTIRE_PAGE_SIZE = """
    var width = Math.max(arguments[0].clientWidth, arguments[0].scrollWidth);
    var height = Math.max(arguments[0].clientHeight, arguments[0].scrollHeight);
    return [width, height];
    """
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

    def __init__(self, driver, scroll_root_element):
        # type: (EyesWebDriver, AnyWebElement) -> None
        super(SeleniumPositionProvider, self).__init__()
        self._driver = driver
        self._scroll_root_element = eyes_selenium_utils.get_underlying_webelement(
            scroll_root_element
        )
        self._data_attribute_added = False
        logger.debug("Creating {}".format(self.__class__.__name__))

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self._scroll_root_element == other._scroll_root_element
        return False

    def get_entire_size(self):
        # type: () -> RectangleSize
        """
        :return: The entire size of the container which the position is relative to.
        """
        try:
            if self._driver.is_mobile_app:
                width, height = self._driver.execute_script(
                    self._JS_GET_CONTENT_ENTIRE_SIZE
                )
            else:
                width, height = self._driver.execute_script(
                    self._JS_GET_ENTIRE_PAGE_SIZE, self._scroll_root_element
                )
        except WebDriverException as e:
            raise WebDriverException("Failed to extract entire size! \n{}".format(e))
        return RectangleSize(width=width, height=height)

    def _add_data_attribute_to_element(self):
        # type: () -> None
        if not self._data_attribute_added:
            if hasattr(self, "_element"):
                element = self._element
            elif self._scroll_root_element:
                element = self._scroll_root_element
            else:
                element = self._driver.find_element_by_tag_name("html")
            element = eyes_selenium_utils.get_underlying_webelement(element)
            eyes_selenium_utils.add_data_scroll_to_element(self._driver, element)


class ScrollPositionProvider(SeleniumPositionProvider):
    def set_position(self, location):
        # type: (Point) -> Point
        logger.debug(
            "setting position of %s to %s" % (location, self._scroll_root_element)
        )

        scroll_command = (
            "arguments[0].scrollLeft=%d; arguments[0].scrollTop=%d; "
            "return (arguments[0].scrollLeft+';'+arguments["
            "0].scrollTop);" % (location["x"], location["y"])
        )
        self._last_set_position = eyes_selenium_utils.parse_location_string(
            self._driver.execute_script(scroll_command, self._scroll_root_element)
        )
        self._add_data_attribute_to_element()
        return self._last_set_position

    def get_current_position(self):
        # type: () -> Point
        """
        The scroll position of the current frame.
        """
        return eyes_selenium_utils.get_current_position(
            self._driver, self._scroll_root_element
        )


class CSSTranslatePositionProvider(SeleniumPositionProvider):
    def __init__(self, driver, scroll_root_element):
        # type: (EyesWebDriver, AnyWebElement) -> None
        self._last_set_position = Point.ZERO()
        super(CSSTranslatePositionProvider, self).__init__(driver, scroll_root_element)

    def get_current_position(self):
        # type: () -> Optional[Point]
        if self._last_set_position:
            return self._last_set_position

        return eyes_selenium_utils.get_current_position(
            self._driver, self._scroll_root_element
        )

    def set_position(self, location):
        # type: (Point) -> Point
        logger.info(
            "CssTranslatePositionProvider - Setting position to: {}".format(location)
        )
        negated_location = -location

        # fix for CSS stitching in Chrome 78
        self._driver.execute_script(
            (
                "arguments[0].style.transform='translate(10px,-{:d}px';".format(
                    -location.y
                )
            ),
            self._scroll_root_element,
        )

        self._driver.execute_script(
            (
                "arguments[0].style.transform='translate({:d}px,{:d}px';".format(
                    negated_location["x"], negated_location["y"]
                )
            ),
            self._scroll_root_element,
        )
        self._last_set_position = location.clone()
        self._add_data_attribute_to_element()
        return self._last_set_position

    def get_state(self):
        # type: () -> PositionMemento
        state = super(CSSTranslatePositionProvider, self).get_state()
        state.transform = self._driver.execute_script(
            "return arguments[0].style.transform;", self._scroll_root_element
        )
        return state

    def restore_state(self, state):
        # type: (PositionMemento) -> None
        self._driver.execute_script(
            """\
            var originalTransform = arguments[0].style.transform;\
            arguments[0].style.transform = '{}';\
            return originalTransform;""".format(
                state.transform
            ),
            self._scroll_root_element,
        )
        self._last_set_position = state.position


class ElementPositionProvider(SeleniumPositionProvider):
    def __init__(self, driver, element):
        # type: (AnyWebDriver, Optional[AnyWebElement]) -> None
        super(ElementPositionProvider, self).__init__(driver, element)
        self._element = element

    def get_current_position(self):
        position = Point(
            self._element.get_scroll_left(), self._element.get_scroll_top()
        )
        logger.debug("Current position: {}".format(position))
        return position

    def set_position(self, location):
        # type: (Point) -> Point
        logger.debug("Scrolling element to {}".format(location))
        position = self._element.scroll_to(location)
        logger.debug("Done scrolling element!")
        self._add_data_attribute_to_element()
        return position

    def get_entire_size(self):
        try:
            size = {
                "width": self._element.get_scroll_width(),
                "height": self._element.get_scroll_height(),
            }
        except WebDriverException as e:
            raise WebDriverException("Failed to extract entire size! \n {}".format(e))
        logger.debug("ElementPositionProvider - Entire size: {}".format(size))
        return RectangleSize(**size)


class CSSMobileSafariPositionProvider(CSSTranslatePositionProvider):
    def __init__(self, driver, scroll_root_element, target_element):
        # type: (EyesWebDriver, AnyWebElement, EyesWebElement) -> None
        super(CSSMobileSafariPositionProvider, self).__init__(
            driver, scroll_root_element
        )
        self._element = target_element

    def set_position(self, location):
        if self._element:
            element_location = self._element.location  # scroll to element
            if Point.from_(location) == element_location:
                # hide header which hides actual element
                self._driver.execute_script(
                    "arguments[0].style.transform='translate(0px,0px)';",
                    self._scroll_root_element,
                )
                return Point.from_(element_location)
        return super(CSSMobileSafariPositionProvider, self).set_position(location)

    def get_current_position(self):
        return eyes_selenium_utils.get_current_position(
            self._driver, self._scroll_root_element
        )


def create_position_provider(driver, stitch_mode, scroll_root_element, target_element):
    # type: (EyesWebDriver,StitchMode,EyesWebElement,Optional[EyesWebElement])->PositionProvider
    logger.debug("initializing position provider. stitch_mode: {}".format(stitch_mode))
    if stitch_mode == StitchMode.Scroll:
        return ScrollPositionProvider(driver, scroll_root_element)
    elif stitch_mode == StitchMode.CSS:
        if (
            driver.user_agent.os == OSNames.IOS
            and driver.user_agent.browser == BrowserNames.MobileSafari
        ):
            return CSSMobileSafariPositionProvider(
                driver, scroll_root_element, target_element
            )
        return CSSTranslatePositionProvider(driver, scroll_root_element)
    else:
        raise EyesError("Wrong sitch_mode")
