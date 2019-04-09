from __future__ import absolute_import

import re
import typing

from selenium.common.exceptions import WebDriverException

from applitools.common import EyesError, Point, logger
from applitools.common.geometry import RectangleSize
from applitools.common.utils import iteritems
from applitools.core import PositionProvider

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
        if self._driver.is_mobile_device():
            return self
        return super(SeleniumPositionProvider, self).__enter__()

    def __exit__(
        self,
        exc_type,  # type: Optional[Any]
        exc_val,  # type: Optional[Any]
        exc_tb,  # type: Optional[Any]
    ):
        # type: (...) -> Union[CSSTranslatePositionProvider, ScrollPositionProvider]
        if self._driver.is_mobile_device():
            return self
        return super(SeleniumPositionProvider, self).__exit__(exc_type, exc_val, exc_tb)

    def _execute_script(self, script):
        return self._driver.execute_script(script, self._scroll_root_element)

    def get_entire_size(self):
        # type: () -> RectangleSize
        """
        :return: The entire size of the container which the position is relative to.
        """
        try:
            if self._driver.is_mobile_device():
                width, height = self._driver.execute_script(
                    self._JS_GET_CONTENT_ENTIRE_SIZE
                )
            else:
                width, height = self._execute_script(self._JS_GET_ENTIRE_PAGE_SIZE)
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
        if self._driver.is_mobile_device():
            scroll_command = "window.scrollTo({0}, {1})".format(location.x, location.y)
            self._driver.execute_script(scroll_command)
            return location
        else:
            scroll_command = (
                "arguments[0].scrollLeft=%d; arguments[0].scrollTop=%d; "
                "return (arguments[0].scrollLeft+';'+arguments["
                "0].scrollTop);" % (location.x, location.y)
            )
        position = eyes_selenium_utils.parse_location_string(  # type: ignore
            self._execute_script(scroll_command)
        )
        self._add_data_attribute_to_element()
        return position

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
        if self._driver.is_mobile_device():
            x, y = self._execute_script(self._JS_GET_CURRENT_SCROLL_POSITION)
            if x is None or y is None:
                raise EyesError("Got None as scroll position! ({},{})".format(x, y))
            return Point(x, y)
        return self.get_current_position_static(self._driver, self._scroll_root_element)


class CSSTranslatePositionProvider(SeleniumPositionProvider):
    _JS_TRANSFORM_KEYS = ["transform", "-webkit-transform"]

    _last_set_position = None  # cache

    def __init__(self, driver, scroll_root_element):
        # type: (EyesWebDriver, AnyWebElement) -> None
        super(CSSTranslatePositionProvider, self).__init__(driver, scroll_root_element)

    def _set_transform(self, transform_list):
        # type: (Dict[str, str]) -> None
        script = ""
        for key, value in iteritems(transform_list):
            script += "document.documentElement.style['{}'] = '{}';".format(key, value)
        self._execute_script(script)

    def _get_current_transform(self):
        # type: () -> Dict[str, str]
        script = "return {"
        for key in self._JS_TRANSFORM_KEYS:
            script += "'{0}': document.documentElement.style['{0}'],".format(key)
        script += " }"
        return self._execute_script(script)

    def get_current_position(self):
        # type: () -> Optional[Point]
        return self._last_set_position

    def _get_position_from_transform(self, transform):
        # type: (str) -> Point
        data = re.match(
            r"^translate\(\s*(\-?)([\d, \.]+)px,\s*(\-?)([\d, \.]+)px\s*\)", transform
        )
        if not data:
            raise EyesError("Can't parse CSS transition")

        x = float(data.group(2))
        y = float(data.group(4))
        minus_x, minus_y = data.group(1), data.group(3)
        if minus_x:
            x *= -1
        if minus_y:
            y *= -1

        return Point(float(x), float(y))

    def set_position(self, location):
        # type: (Point) -> Point
        translate_command = "translate(-{}px, -{}px)".format(location.x, location.y)
        logger.debug(translate_command)
        transform_list = dict(
            (key, translate_command) for key in self._JS_TRANSFORM_KEYS
        )
        self._set_transform(transform_list)
        self._last_set_position = location.clone()
        self._add_data_attribute_to_element()
        return self._last_set_position

    def push_state(self):
        # type: () -> None
        """
        Adds the transform to the states list.
        """
        transforms = self._get_current_transform()
        if not all(transforms.values()):
            self._last_set_position = Point.zero()
        else:
            point = Point(0, 0)
            for transform in transforms.values():
                point += self._get_position_from_transform(transform)
            self._last_set_position = point
        self._states.append(self._last_set_position)


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
        result = self._element.scroll_to(location)
        logger.debug("Done scrolling element!")
        self._add_data_attribute_to_element()
        return result

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
