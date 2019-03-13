import typing

import attr
from selenium.webdriver.common.by import By

from applitools.common import CoordinatesType, FloatingMatchSettings, Point, Region
from applitools.core import GetFloatingRegion, GetRegion
from applitools.selenium.capture import EyesWebDriverScreenshot

if typing.TYPE_CHECKING:
    from typing import List
    from applitools.core import EyesBase
    from applitools.common import FloatingBounds
    from applitools.common.utils.custom_types import AnyWebElement

__all__ = (
    "IgnoreRegionBy",
    "IgnoreRegionByElement",
    "IgnoreRegionByCssSelector",
    "FloatingRegionBy",
    "FloatingRegionByElement",
    "FloatingRegionByCssSelector",
)


def get_region_from_element(element, screenshot):
    location = element.location
    size = element.size
    if screenshot:
        # Element's coordinates are context relative, so we need to convert them first.
        adjusted_location = screenshot.location_in_screenshot(
            Point(location["x"], location["y"]), CoordinatesType.CONTEXT_RELATIVE
        )
    else:
        adjusted_location = Point(location["x"], location["y"])
    region = Region.from_location_size(adjusted_location, size)
    return region


@attr.s
class IgnoreRegionByElement(GetRegion):
    element = attr.ib()  # type: AnyWebElement

    def get_regions(self, eyes, screenshot):
        # type: (EyesBase, EyesWebDriverScreenshot) -> List[Region]
        region = get_region_from_element(self.element, screenshot)
        return [region]


@attr.s
class IgnoreRegionBy(GetRegion):
    """
    :param by: The "by" part of a selenium selector for an element which
               represents the ignore region
    :param value: The "value" part of a selenium selector for
                  an element which represents the ignore region.
    """

    by = attr.ib()
    value = attr.ib()

    def get_regions(self, eyes, screenshot):
        # type: (EyesBase, EyesWebDriverScreenshot) -> List[Region]
        element = eyes.driver.find_element(self.by, self.value)
        return IgnoreRegionByElement(element).get_regions(eyes, screenshot)


@attr.s
class IgnoreRegionByCssSelector(GetRegion):
    """
    :ivar selector: The css selector for an element which represents the inner region.
    :ivar bounds: The outer rectangle bounding the inner region.
    """

    selector = attr.ib()

    def get_regions(self, eyes, screenshot):
        # type: (EyesBase, EyesWebDriverScreenshot) -> List[Region]
        ir = IgnoreRegionBy(by=By.CSS_SELECTOR, value=self.selector)
        return ir.get_regions(eyes, screenshot)


@attr.s
class FloatingRegionByElement(GetFloatingRegion):
    """
    :ivar element: The element which represents the inner region (the floating part).
    :ivar bounds: The outer rectangle bounding the inner region.
    """

    element = attr.ib()  # type: AnyWebElement
    bounds = attr.ib()  # type: FloatingBounds

    def get_regions(self, eyes, screenshot):
        # type: (EyesBase, EyesWebDriverScreenshot) -> List[FloatingMatchSettings]
        region = get_region_from_element(self.element, screenshot)
        return [FloatingMatchSettings(region, self.bounds)]


@attr.s
class FloatingRegionBy(GetFloatingRegion):
    """
    :ivar by: The selenium By
    :ivar value: The css selector for an element which represents the inner region.
    :ivar bounds: The outer rectangle bounding the inner region.
    """

    by = attr.ib()  # type: str
    value = attr.ib()  # type: str
    bounds = attr.ib()  # type: FloatingBounds

    def get_regions(self, eyes, screenshot):
        # type: (EyesBase, EyesWebDriverScreenshot) -> List[FloatingMatchSettings]
        element = eyes.driver.find_element(self.by, self.value)
        fr = FloatingRegionByElement(element, self.bounds)
        return fr.get_regions(eyes, screenshot)


@attr.s
class FloatingRegionByCssSelector(GetFloatingRegion):
    """
    :ivar selector: The css selector for an element which represents the inner region.
    :ivar bounds: The outer rectangle bounding the inner region.
    """

    selector = attr.ib()  # type: str
    bounds = attr.ib()  # type: FloatingBounds

    def get_regions(self, eyes, screenshot):
        # type: (EyesBase, EyesWebDriverScreenshot) -> List[FloatingMatchSettings]
        fr = FloatingRegionBy(By.CSS_SELECTOR, self.selector, self.bounds)
        return fr.get_regions(eyes, screenshot)
