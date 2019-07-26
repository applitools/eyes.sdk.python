from __future__ import absolute_import

import typing

from selenium.common.exceptions import WebDriverException

from applitools.common import EyesError, Point, logger
from applitools.common.geometry import RectangleSize
from applitools.core import PositionMomento, PositionProvider

from . import eyes_selenium_utils

if typing.TYPE_CHECKING:
    from typing import Optional, Union, Any, Dict
    from applitools.common.utils.custom_types import AnyWebDriver, AnyWebElement
    from . import EyesWebDriver


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

    def __enter__(self):
        # type: () -> SeleniumPositionProvider
        if self._driver.is_mobile_app:
            return self
        return super(SeleniumPositionProvider, self).__enter__()

    def __exit__(
        self,
        exc_type,  # type: Optional[Any]
        exc_val,  # type: Optional[Any]
        exc_tb,  # type: Optional[Any]
    ):
        # type: (...) -> Union[CSSTranslatePositionProvider, ScrollPositionProvider]
        if self._driver.is_mobile_app:
            return self
        return super(SeleniumPositionProvider, self).__exit__(exc_type, exc_val, exc_tb)

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
    _JS_GET_CURRENT_SCROLL_POSITION = """
var doc = document.documentElement;
var x = window.scrollX || ((window.pageXOffset || doc.scrollLeft) - (doc.clientLeft || 0));
var y = window.scrollY || ((window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0));
return [x, y]"""

    def set_position(self, location):
        # type: (Point) -> Point
        logger.debug(
            "setting position of %s to %s" % (location, self._scroll_root_element)
        )
        if self._driver.is_mobile_web:
            scroll_command = "window.scrollTo({0}, {1})".format(location.x, location.y)
            self._driver.execute_script(scroll_command)
            self._last_set_position = location
            return self._last_set_position
        else:
            scroll_command = (
                "arguments[0].scrollLeft=%d; arguments[0].scrollTop=%d; "
                "return (arguments[0].scrollLeft+';'+arguments["
                "0].scrollTop);" % (location.x, location.y)
            )
        self._last_set_position = eyes_selenium_utils.parse_location_string(  # type: ignore
            self._driver.execute_script(scroll_command, self._scroll_root_element)
        )
        self._add_data_attribute_to_element()
        return self._last_set_position

    @staticmethod
    def get_current_position_static(driver, scroll_root_element):
        # type: (EyesWebDriver, AnyWebElement) -> Point
        element = eyes_selenium_utils.get_underlying_webelement(scroll_root_element)
        xy = driver.execute_script(
            "return arguments[0].scrollLeft+';'+arguments[0].scrollTop;", element
        )
        return eyes_selenium_utils.parse_location_string(xy)

    def get_current_position(self):
        # type: () -> Point
        """
        The scroll position of the current frame.
        """
        if self._driver.is_mobile_web:
            x, y = self._driver.execute_script(
                self._JS_GET_CURRENT_SCROLL_POSITION, self._scroll_root_element
            )
            if x is None or y is None:
                raise EyesError("Got None as scroll position! ({},{})".format(x, y))
            return Point(x, y)
        return self.get_current_position_static(self._driver, self._scroll_root_element)


class CSSTranslatePositionProvider(SeleniumPositionProvider):
    def __init__(self, driver, scroll_root_element):
        # type: (EyesWebDriver, AnyWebElement) -> None
        super(CSSTranslatePositionProvider, self).__init__(driver, scroll_root_element)

    def get_current_position(self):
        # type: () -> Optional[Point]
        return self._last_set_position

    def set_position(self, location):
        # type: (Point) -> Point
        logger.info(
            "CssTranslatePositionProvider - Setting position to: {}".format(location)
        )
        self._driver.execute_script(
            (
                "document.documentElement.style.transform='translate(-{:d}px,"
                "-{:d}px';".format(location.x, location.y)
            ),
            self._scroll_root_element,
        )
        self._last_set_position = location.clone()
        self._add_data_attribute_to_element()
        return self._last_set_position

    def push_state(self):
        """
        Adds the transform to the states list.
        """
        transform = self._driver.execute_script(
            "return arguments[0].style.transform;", self._scroll_root_element
        )
        self._states.append(
            PositionMomento(position=self._last_set_position, transform=transform)
        )

    def pop_state(self):
        state = self._states.pop()
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
        self._last_set_position = self._element.scroll_to(location)
        logger.debug("Done scrolling element!")
        self._add_data_attribute_to_element()
        return self._last_set_position

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
