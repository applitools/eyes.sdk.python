import typing
from abc import abstractmethod

import attr

from applitools.common import CoordinatesType, FloatingMatchSettings, Point, Region
from applitools.core import GetFloatingRegion, GetRegion
from applitools.selenium.capture import EyesWebDriverScreenshot

if typing.TYPE_CHECKING:
    from typing import List
    from applitools.common import FloatingBounds
    from applitools.common.utils.custom_types import AnyWebElement, AnyWebDriver
    from applitools.selenium.selenium_eyes import SeleniumEyes

__all__ = (
    "RegionBySelector",
    "RegionByElement",
    "FloatingRegionBySelector",
    "FloatingRegionByElement",
)


def _region_from_element(element, screenshot):
    location = element.location
    size = element.size
    if screenshot:
        # Element's coordinates are context relative, so we need to convert them first.
        adjusted_location = screenshot.location_in_screenshot(
            Point(location["x"], location["y"]), CoordinatesType.CONTEXT_RELATIVE
        )
    else:
        adjusted_location = Point(location["x"], location["y"])
    region = Region.from_(adjusted_location, size)
    return region


class GetSeleniumRegion(GetRegion):
    def get_regions(self, eyes, screenshot):
        # type: (SeleniumEyes, EyesWebDriverScreenshot) -> List[Region]
        element = self._element(eyes.driver)
        region = _region_from_element(element, screenshot)
        return [region]

    def get_elements(self, driver):
        # type: (AnyWebDriver) -> List[AnyWebElement]
        return [self._element(driver)]

    @abstractmethod
    def _element(self, driver):
        pass


class GetSeleniumFloatingRegion(GetFloatingRegion):
    def get_regions(self, eyes, screenshot):
        # type: (SeleniumEyes, EyesWebDriverScreenshot) ->  List[FloatingMatchSettings]
        element = self._element(eyes.driver)
        region = _region_from_element(element, screenshot)
        return [FloatingMatchSettings(region, self.bounds)]

    def get_elements(self, driver):
        # type: (AnyWebDriver) -> List[AnyWebElement]
        return [self._element(driver)]

    @abstractmethod
    def _element(self, driver):
        pass


@attr.s
class RegionByElement(GetSeleniumRegion):
    element = attr.ib()  # type: AnyWebElement

    def _element(self, driver):
        return self.element


@attr.s
class RegionBySelector(GetSeleniumRegion):
    """
    :param by: The "by" part of a selenium selector for an element which
               represents the ignore region
    :param value: The "value" part of a selenium selector for
                  an element which represents the ignore region.
    """

    by = attr.ib()
    value = attr.ib()

    def _element(self, driver):
        return driver.find_element(self.by, self.value)


@attr.s
class FloatingRegionByElement(GetSeleniumFloatingRegion):
    """
    :ivar element: The element which represents the inner region (the floating part).
    :ivar bounds: The outer rectangle bounding the inner region.
    """

    element = attr.ib()  # type: AnyWebElement
    bounds = attr.ib()  # type: FloatingBounds

    def _element(self, driver):
        return self.element


@attr.s
class FloatingRegionBySelector(GetSeleniumFloatingRegion):
    """
    :ivar by: The selenium By
    :ivar value: The css selector for an element which represents the inner region.
    :ivar bounds: The outer rectangle bounding the inner region.
    """

    by = attr.ib()  # type: str
    value = attr.ib()  # type: str
    bounds = attr.ib()  # type: FloatingBounds

    def _element(self, driver):
        return driver.find_element(self.by, self.value)
