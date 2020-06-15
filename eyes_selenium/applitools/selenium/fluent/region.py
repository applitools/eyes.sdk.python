import typing
from abc import abstractmethod

import attr

from applitools.common import (
    CoordinatesType,
    FloatingMatchSettings,
)
from applitools.common.geometry import AccessibilityRegion, Point, Region
from applitools.common.accessibility import AccessibilityRegionType
from applitools.core import GetFloatingRegion, GetRegion
from applitools.core.fluent.region import GetAccessibilityRegion
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
    "AccessibilityRegionBySelector",
    "AccessibilityRegionByElement",
)


def _region_from_element(element, screenshot):
    # type: (AnyWebElement, EyesWebDriverScreenshot) -> Region
    location = element.location
    if screenshot:
        # Element's coordinates are context relative, so we need to convert them first.
        adjusted_location = screenshot.location_in_screenshot(
            Point.from_(location), CoordinatesType.CONTEXT_RELATIVE
        )
    else:
        adjusted_location = Point.from_(location)
    region = Region.from_(adjusted_location, element.size)
    return region


class GetSeleniumRegion(GetRegion):
    def get_regions(self, eyes, screenshot):
        # type: (SeleniumEyes, EyesWebDriverScreenshot) -> List[Region]
        element = self._fetch_element(eyes.driver)
        region = _region_from_element(element, screenshot)
        return [region]

    def get_elements(self, driver):
        # type: (AnyWebDriver) -> List[AnyWebElement]
        return [self._fetch_element(driver)]

    @abstractmethod
    def _fetch_element(self, driver):
        pass


class GetSeleniumFloatingRegion(GetFloatingRegion):
    def get_regions(self, eyes, screenshot):
        # type: (SeleniumEyes, EyesWebDriverScreenshot) ->  List[FloatingMatchSettings]
        element = self._fetch_element(eyes.driver)
        region = _region_from_element(element, screenshot)
        return [FloatingMatchSettings(region, self._bounds)]

    def get_elements(self, driver):
        # type: (AnyWebDriver) -> List[AnyWebElement]
        return [self._fetch_element(driver)]

    @abstractmethod
    def _fetch_element(self, driver):
        pass


@attr.s
class RegionByElement(GetSeleniumRegion):
    _element = attr.ib()  # type: AnyWebElement

    def _fetch_element(self, driver):
        return self._element


@attr.s
class RegionBySelector(GetSeleniumRegion):
    """
    :param by: The "by" part of a selenium selector for an element which
               represents the ignore region
    :param value: The "value" part of a selenium selector for
                  an element which represents the ignore region.
    """

    _by = attr.ib()
    _value = attr.ib()

    def _fetch_element(self, driver):
        return driver.find_element(self._by, self._value)


@attr.s
class FloatingRegionByElement(GetSeleniumFloatingRegion):
    """
    :ivar element: The element which represents the inner region (the floating part).
    :ivar bounds: The outer rectangle bounding the inner region.
    """

    _element = attr.ib()  # type: AnyWebElement
    _bounds = attr.ib()  # type: FloatingBounds

    def _fetch_element(self, driver):
        return self._element


@attr.s
class FloatingRegionBySelector(GetSeleniumFloatingRegion):
    """
    :ivar by: The selenium By
    :ivar value: The css selector for an element which represents the inner region.
    :ivar bounds: The outer rectangle bounding the inner region.
    """

    _by = attr.ib()  # type: str
    _value = attr.ib()  # type: str
    _bounds = attr.ib()  # type: FloatingBounds

    def _fetch_element(self, driver):
        return driver.find_element(self._by, self._value)


class GetSeleniumAccessibilityRegion(GetAccessibilityRegion):
    def get_regions(self, eyes, screenshot):
        # type:(SeleniumEyes,EyesWebDriverScreenshot)->List[AccessibilityRegion]
        element = self._fetch_element(eyes.driver)
        region = _region_from_element(element, screenshot)
        return [AccessibilityRegion.from_(region, self._type)]

    def get_elements(self, driver):
        # type: (AnyWebDriver) -> List[AnyWebElement]
        return [self._fetch_element(driver)]

    @abstractmethod
    def _fetch_element(self, driver):
        pass


@attr.s
class AccessibilityRegionBySelector(GetSeleniumAccessibilityRegion):
    _by = attr.ib()  # type: str
    _value = attr.ib()  # type: str
    _type = attr.ib()  # type: AccessibilityRegionType

    def _fetch_element(self, driver):
        return driver.find_element(self._by, self._value)


@attr.s
class AccessibilityRegionByElement(GetSeleniumAccessibilityRegion):
    _element = attr.ib()  # type: AnyWebElement
    _type = attr.ib()  # type: AccessibilityRegionType

    def _fetch_element(self, driver):
        return self._element
