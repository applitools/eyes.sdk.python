from __future__ import absolute_import

import re
import typing

from selenium.common.exceptions import WebDriverException

from applitools.common import EyesError, Point, logger
from applitools.common.geometry import RectangleSize
from applitools.core import PositionProvider

from . import eyes_selenium_utils

if typing.TYPE_CHECKING:
    from typing import Text, Optional, List
    from applitools.common.utils.custom_types import AnyWebDriver, AnyWebElement
    from . import EyesWebDriver


class StitchMode(object):
    """
    The type of methods for stitching full-page screenshots.
    """

    Scroll = "Scroll"
    CSS = "CSS"


class SeleniumPositionProvider(PositionProvider):
    """ Encapsulates page/element positioning """

    _JS_GET_ENTIRE_PAGE_SIZE = """
    var width = Math.max(arguments[0].clientWidth, arguments[0].scrollWidth);
    var height = Math.max(arguments[0].clientHeight, arguments[0].scrollHeight);
    return [width, height];
    """

    def __init__(self, driver, scroll_root_element):
        # type: (EyesWebDriver, AnyWebElement) -> None
        super(SeleniumPositionProvider, self).__init__()
        self._driver = driver
        self._scroll_root_element = eyes_selenium_utils.get_underlying_webelement(
            scroll_root_element
        )
        logger.info("Creating {}".format(self.__class__.__name__))

    def _execute_script(self, script):
        # type: (Text) -> List[int]
        return self._driver.execute_script(script, self._scroll_root_element)

    def get_entire_size(self):
        # type: () -> RectangleSize
        """
        :return: The entire size of the container which the position is relative to.
        """
        try:
            width, height = self._execute_script(self._JS_GET_ENTIRE_PAGE_SIZE)
        except WebDriverException as e:
            raise EyesError("Failed to extract entire size! \n{}".format(e))
        return RectangleSize(width=width, height=height)


class ScrollPositionProvider(SeleniumPositionProvider):
    def set_position(self, location):
        logger.debug(
            "setting position of %s to %s" % (location, self._scroll_root_element)
        )
        scroll_command = (
            "arguments[0].scrollLeft=%d; arguments[0].scrollTop=%d; "
            "return (arguments[0].scrollLeft+';'+arguments["
            "0].scrollTop);" % (location.x, location.y)
        )
        return eyes_selenium_utils.parse_location_string(
            self._execute_script(scroll_command)
        )

    @staticmethod
    def get_current_position_static(driver, scroll_root_element):
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
        return self.get_current_position_static(self._driver, self._scroll_root_element)


class CSSTranslatePositionProvider(SeleniumPositionProvider):
    _JS_TRANSFORM_KEYS = ["transform", "-webkit-transform"]

    _last_set_position = None  # cache

    def __init__(self, driver, scroll_root_element):
        super(CSSTranslatePositionProvider, self).__init__(driver, scroll_root_element)

    def _set_transform(self, transform_list):
        script = ""
        for key, value in transform_list.items():
            script += "document.documentElement.style['{}'] = '{}';".format(key, value)
        self._execute_script(script)

    def _get_current_transform(self):
        script = "return {"
        for key in self._JS_TRANSFORM_KEYS:
            script += "'{0}': document.documentElement.style['{0}'],".format(key)
        script += " }"
        return self._execute_script(script)

    def get_current_position(self):
        return self._last_set_position

    def _get_position_from_transform(self, transform):
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
        translate_command = "translate(-{}px, -{}px)".format(location.x, location.y)
        logger.debug(translate_command)
        transform_list = dict(
            (key, translate_command) for key in self._JS_TRANSFORM_KEYS
        )
        self._set_transform(transform_list)
        self._last_set_position = location.clone()
        return self._last_set_position

    def push_state(self):
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
        logger.info("Current position: {}".format(position))
        return position

    def set_position(self, location):
        # type: (Point) -> Point
        logger.info("Scrolling element to {}".format(location))
        result = self._element.scroll_to(location)
        logger.info("Done scrolling element!")
        return result

    def get_entire_size(self):
        try:
            size = {
                "width": self._element.get_scroll_width(),
                "height": self._element.get_scroll_height(),
            }
        except WebDriverException as e:
            raise EyesError("Failed to extract entire size! \n {}".format(e))
        logger.info("ElementPositionProvider - Entire size: {}".format(size))
        return RectangleSize(**size)
