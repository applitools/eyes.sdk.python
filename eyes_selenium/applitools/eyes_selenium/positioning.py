from __future__ import absolute_import

import abc
import re
import typing as tp

from selenium.common.exceptions import WebDriverException

from applitools.eyes_core import logger, EyesError, Point
from applitools.eyes_core.utils import ABC

if tp.TYPE_CHECKING:
    from applitools.eyes_core.utils.custom_types import AnyWebDriver, ViewPort, AnyWebElement


class StitchMode(object):
    """
    The type of methods for stitching full-page screenshots.
    """
    Scroll = "Scroll"
    CSS = "CSS"


class PositionProvider(ABC):
    """ Encapsulates page/element positioning """
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

    def __init__(self, driver):
        # type: (AnyWebDriver) -> None
        self._driver = driver
        self._states = []  # type: tp.List[Point]

    def _execute_script(self, script):
        # type: (tp.Text) -> tp.List[int]
        return self._driver.execute_script(script)

    @abc.abstractmethod
    def get_current_position(self):
        # type: () -> tp.Optional[Point]
        """
        :return: The current position, or `None` if position is not available.
        """

    @abc.abstractmethod
    def set_position(self, location):
        # type: (Point) -> None
        """
        Go to the specified location.

        :param location: The position to set
        :return:
        """

    def get_entire_size(self):
        # type: () -> ViewPort
        """
        :return: The entire size of the container which the position is relative to.
        """
        try:
            width, height = self._driver.execute_script(self._JS_GET_CONTENT_ENTIRE_SIZE)
        except WebDriverException:
            raise EyesError('Failed to extract entire size!')
        return dict(width=width, height=height)

    def push_state(self):
        """
        Adds the current position to the states list.
        """
        self._states.append(self.get_current_position())

    def pop_state(self):
        """
        Sets the position to be the last position added to the states list.
        """
        self.set_position(self._states.pop())


class ScrollPositionProvider(PositionProvider):
    _JS_GET_CURRENT_SCROLL_POSITION = """
        var doc = document.documentElement;
        var x = window.scrollX || ((window.pageXOffset || doc.scrollLeft) - (doc.clientLeft || 0));
        var y = window.scrollY || ((window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0));
        return [x, y]"""

    def set_position(self, location):
        scroll_command = "window.scrollTo({0}, {1})".format(location.x, location.y)
        logger.debug(scroll_command)
        self._execute_script(scroll_command)

    def get_current_position(self):
        try:
            x, y = self._execute_script(self._JS_GET_CURRENT_SCROLL_POSITION)
            if x is None or y is None:
                raise EyesError("Got None as scroll position! ({},{})".format(x, y))
        except WebDriverException:
            raise EyesError("Failed to extract current scroll position!")
        return Point(x, y)


class CSSTranslatePositionProvider(PositionProvider):
    _JS_TRANSFORM_KEYS = ["transform", "-webkit-transform"]

    def __init__(self, driver):
        super(CSSTranslatePositionProvider, self).__init__(driver)
        self._current_position = Point(0, 0)

    def _set_transform(self, transform_list):
        script = ''
        for key, value in transform_list.items():
            script += "document.documentElement.style['{}'] = '{}';".format(key, value)
        self._execute_script(script)

    def _get_current_transform(self):
        script = 'return {'
        for key in self._JS_TRANSFORM_KEYS:
            script += "'{0}': document.documentElement.style['{0}'],".format(key)
        script += ' }'
        return self._execute_script(script)

    def get_current_position(self):
        return self._current_position.clone()

    def _get_position_from_transform(self, transform):
        data = re.match(r"^translate\(\s*(\-?)([\d, \.]+)px,\s*(\-?)([\d, \.]+)px\s*\)", transform)
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
        transform_list = dict((key, translate_command) for key in self._JS_TRANSFORM_KEYS)
        self._set_transform(transform_list)
        self._current_position = location.clone()

    def push_state(self):
        """
        Adds the transform to the states list.
        """
        transforms = self._get_current_transform()
        if not all(transforms.values()):
            self._current_position = Point.create_top_left()
        else:
            point = Point(0, 0)
            for transform in transforms.values():
                point += self._get_position_from_transform(transform)
            self._current_position = point
        self._states.append(self._current_position)


class ElementPositionProvider(PositionProvider):

    def __init__(self, driver, element):
        # type: (AnyWebDriver, tp.Optional[AnyWebElement]) -> None
        super(ElementPositionProvider, self).__init__(driver)
        self._element = element

    def get_current_position(self):
        position = Point(self._element.get_scroll_left(), self._element.get_scroll_top())
        logger.info("Current position: {}".format(position))
        return position

    def set_position(self, location):
        logger.info("Scrolling element to {}".format(location))
        self._element.scroll_to(location)
        logger.info("Done scrolling element!")

    def get_entire_size(self):
        try:
            size = {'width': self._element.get_scroll_width(), 'height': self._element.get_scroll_height()}
        except WebDriverException:
            raise EyesError('Failed to extract entire size!')
        logger.info("ElementPositionProvider - Entire size: {}".format(size))
        return size


def build_position_provider_for(stitch_mode,  # type: tp.Text
                                driver,  # type: AnyWebDriver
                                ):
    # type: (...) -> PositionProvider
    if stitch_mode == StitchMode.Scroll:
        return ScrollPositionProvider(driver)
    elif stitch_mode == StitchMode.CSS:
        return CSSTranslatePositionProvider(driver)
    raise ValueError("Invalid stitch mode: {}".format(stitch_mode))
