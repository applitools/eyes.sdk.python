import typing

import attr

from applitools.common import Region
from applitools.core import GetFloatingRegion, GetRegion
from applitools.selenium.capture import EyesWebDriverScreenshot

if typing.TYPE_CHECKING:
    from typing import Any, Text
    from applitools.core import EyesBase
    from applitools.common.utils.custom_types import AnyWebElement

__all__ = (
    "IgnoreRegionByElement",
    "IgnoreRegionBySelector",
    "FloatingBounds",
    "FloatingRegion",
    "FloatingRegionByElement",
    "FloatingRegionBySelector",
)


@attr.s
class IgnoreRegionByElement(GetRegion):
    element = attr.ib()  # type: AnyWebElement

    def get_region(self, eyes, screenshot):
        # type: (EyesBase, EyesWebDriverScreenshot) -> Region
        return screenshot.get_element_region_in_frame_viewport(self.element)


@attr.s
class IgnoreRegionBySelector(GetRegion):
    """
    :param by: The "by" part of a selenium selector for an element which
               represents the ignore region
    :param value: The "value" part of a selenium selector for
                  an element which represents the ignore region.
    """

    by = attr.ib()
    value = attr.ib()

    def get_region(self, eyes, screenshot):
        # type: (EyesBase, EyesWebDriverScreenshot) -> Region
        element = eyes.driver.find_element(self.by, self.value)
        return screenshot.get_element_region_in_frame_viewport(element)


@attr.s
class _NopRegionWrapper(GetRegion):
    _region = attr.ib()  # type: Region

    def get_region(self, eyes, screenshot):
        # type: (EyesBase, EyesWebDriverScreenshot) -> Any
        return self._region


@attr.s
class FloatingBounds(object):
    max_left_offset = attr.ib(default=0)  # type: int
    max_up_offset = attr.ib(default=0)  # type: int
    max_right_offset = attr.ib(default=0)  # type: int
    max_down_offset = attr.ib(default=0)  # type: int


@attr.s
class FloatingRegion(GetFloatingRegion):
    """
    :ivar region: The inner region (the floating part).
    :ivar bounds: The outer rectangle bounding the inner region.
    """

    _region = attr.ib(repr=False)  # type: Region
    _bounds = attr.ib(repr=False)  # type: FloatingBounds

    left = attr.ib(init=False)  # type: int
    top = attr.ib(init=False)  # type: int
    width = attr.ib(init=False)  # type: int
    height = attr.ib(init=False)  # type: int
    coordinates_type = attr.ib(init=False)  # type: Text
    max_left_offset = attr.ib(init=False)  # type: int
    max_up_offset = attr.ib(init=False)  # type: int
    max_right_offset = attr.ib(init=False)  # type: int
    max_down_offset = attr.ib(init=False)  # type: int

    def __attrs_post_init__(self):
        self.left = self._region.left
        self.top = self._region.top
        self.width = self._region.width
        self.height = self._region.height
        self.coordinates_type = self._region.coordinates_type
        self.max_left_offset = self._bounds.max_left_offset
        self.max_up_offset = self._bounds.max_up_offset
        self.max_right_offset = self._bounds.max_right_offset
        self.max_down_offset = self._bounds.max_down_offset

    def get_region(self, eyes, screenshot):
        # type: (EyesBase, EyesWebDriverScreenshot) -> FloatingRegion
        """Used for compatibility when iterating over regions"""
        return self


class FloatingRegionByElement(GetFloatingRegion):
    """
    :ivar element: The element which represents the inner region (the floating part).
    :ivar bounds: The outer rectangle bounding the inner region.
    """

    element = attr.ib()  # type: AnyWebElement
    bounds = attr.ib()  # type: FloatingBounds

    def get_region(self, eyes, screenshot):
        # type: (EyesBase, EyesWebDriverScreenshot) -> FloatingRegion
        region = screenshot.get_element_region_in_frame_viewport(self.element)
        return FloatingRegion(region, self.bounds)


class FloatingRegionBySelector(GetFloatingRegion):
    """
    :ival by: The "by" part of a selenium selector for an element which
        represents the inner region
    :ivar value: The "value" part of a selenium selector for an
                  element which represents the inner region.
    :ivar bounds: The outer rectangle bounding the inner region.
    """

    by = attr.ib()  # type: str
    value = attr.ib()  # type: str
    bounds = attr.ib()  # type: FloatingBounds

    def get_region(self, eyes, screenshot):
        # type: (EyesBase, EyesWebDriverScreenshot) -> FloatingRegion
        driver = eyes.driver
        element = driver.find_element(self.by, self.value)
        region = screenshot.get_element_region_in_frame_viewport(element)
        return FloatingRegion(region, self.bounds)
