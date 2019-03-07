import typing

from applitools.common import EyesError, Region
from applitools.selenium.capture import EyesWebDriverScreenshot

if typing.TYPE_CHECKING:
    from typing import Any
    from applitools.common.utils.custom_types import AnyWebElement

__all__ = (
    "IgnoreRegionByElement",
    "IgnoreRegionBySelector",
    "FloatingBounds",
    "FloatingRegion",
    "FloatingRegionByElement",
    "FloatingRegionBySelector",
)


class IgnoreRegionByElement(object):
    def __init__(self, element):
        # type: (AnyWebElement) -> None
        self.element = element

    def get_region(self, eyes_screenshot):
        # type: (EyesWebDriverScreenshot) -> Region
        return eyes_screenshot.get_element_region_in_frame_viewport(self.element)

    def _str_(self):
        return "{0} Element: {1}".format(self.__class__.__name__, self.element)


class IgnoreRegionBySelector(object):
    def __init__(self, by, value):
        # type: (str, str) -> None
        """
        :param by: The "by" part of a selenium selector for an element which
                   represents the ignore region
        :param value: The "value" part of a selenium selector for
                      an element which represents the ignore region.
        """
        self.by = by
        self.value = value

    def get_region(self, eyes_screenshot):
        # type: (EyesWebDriverScreenshot) -> Region
        driver = eyes_screenshot._driver
        element = driver.find_element(self.by, self.value)
        return eyes_screenshot.get_element_region_in_frame_viewport(element)

    def _str_(self):
        return "{0} {{by: {1}, value: {2}}}".format(
            self.__class__.__name__, self.by, self.value
        )


class _NopRegionWrapper(object):
    def __init__(self, region):
        # type: (Region) -> None
        self.region = region

    def get_region(self, eyes_screenshot):
        # type: (EyesWebDriverScreenshot) -> Any
        return self.region

    def __str__(self):
        return str(self.region)


class FloatingBounds(object):
    def __init__(
        self, max_left_offset=0, max_up_offset=0, max_right_offset=0, max_down_offset=0
    ):
        # type: (int, int, int, int) -> None
        self.max_left_offset = max_left_offset
        self.max_up_offset = max_up_offset
        self.max_right_offset = max_right_offset
        self.max_down_offset = max_down_offset


class FloatingRegion(object):
    def __init__(self, region, bounds):
        # type: (Region, FloatingBounds) -> None
        """
        :param region: The inner region (the floating part).
        :param bounds: The outer rectangle bounding the inner region.
        """
        self.region = region
        self.bounds = bounds

    def get_region(self, eyes_screenshot):
        # type: (EyesWebDriverScreenshot) -> FloatingRegion
        """Used for compatibility when iterating over regions"""
        return self

    def __getstate__(self):
        return dict(
            top=self.region.top,
            left=self.region.left,
            width=self.region.width,
            height=self.region.height,
            maxLeftOffset=self.bounds.max_left_offset,
            maxUpOffset=self.bounds.max_up_offset,
            maxRightOffset=self.bounds.max_right_offset,
            maxDownOffset=self.bounds.max_down_offset,
        )

    # This is required in order for jsonpickle to work on this object.
    # noinspection PyMethodMayBeStatic
    def __setstate__(self, state):
        raise EyesError("Cannot create FloatingRegion instance from dict!")

    def _str_(self):
        return "{0} {{region: {1}, bounds: {2}}}".format(
            self.__class__.__name__, self.region, self.bounds
        )


class FloatingRegionByElement(object):
    def __init__(self, element, bounds):
        # type: (AnyWebElement, FloatingBounds) -> None
        """
        :param element: The element which represents the inner region (the floating part).
        :param bounds: The outer rectangle bounding the inner region.
        """
        self.element = element
        self.bounds = bounds

    def get_region(self, eyes_screenshot):
        # type: (EyesWebDriverScreenshot) -> FloatingRegion
        region = eyes_screenshot.get_element_region_in_frame_viewport(self.element)
        return FloatingRegion(region, self.bounds)

    def _str_(self):
        return "{0} {{element: {1}, bounds: {2}}}".format(
            self.__class__.__name__, self.element, self.bounds
        )


class FloatingRegionBySelector(object):
    def __init__(self, by, value, bounds):
        # type: (str, str, FloatingBounds) -> None
        """
        :param by: The "by" part of a selenium selector for an element which
            represents the inner region
        :param value: The "value" part of a selenium selector for an
                      element which represents the inner region.
        :param bounds: The outer rectangle bounding the inner region.
        """
        self.by = by
        self.value = value
        self.bounds = bounds

    def get_region(self, eyes_screenshot):
        # type: (EyesWebDriverScreenshot) -> FloatingRegion
        driver = eyes_screenshot._driver
        element = driver.find_element(self.by, self.value)
        region = eyes_screenshot.get_element_region_in_frame_viewport(element)
        return FloatingRegion(region, self.bounds)

    def _str_(self):
        return "{0} {{element: {{ by: {1}, value: {2}}}, bounds: {3} }}".format(
            self.__class__.__name__, self.by, self.value, self.bounds
        )
