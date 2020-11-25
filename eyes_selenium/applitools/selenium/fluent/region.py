import typing
from abc import abstractmethod

import attr

from applitools.common import CoordinatesType, FloatingMatchSettings
from applitools.common.accessibility import AccessibilityRegionType
from applitools.common.geometry import AccessibilityRegion, Point, Region
from applitools.common.utils import ABC
from applitools.core import GetFloatingRegion, GetRegion
from applitools.core.fluent.region import GetAccessibilityRegion
from applitools.selenium.capture import EyesWebDriverScreenshot

if typing.TYPE_CHECKING:
    from typing import List, Optional

    from applitools.common import FloatingBounds
    from applitools.common.utils.custom_types import (
        AnyWebDriver,
        AnyWebElement,
        CodedRegionPadding,
    )
    from applitools.selenium.selenium_eyes import SeleniumEyes

__all__ = (
    "RegionBySelector",
    "RegionByElement",
    "FloatingRegionBySelector",
    "FloatingRegionByElement",
    "AccessibilityRegionBySelector",
    "AccessibilityRegionByElement",
)


def _region_from_element(element, screenshot, padding=None):
    # type: (AnyWebElement,EyesWebDriverScreenshot,Optional[CodedRegionPadding])->Region
    location = element.location
    if screenshot:
        # Element's coordinates are context relative, so we need to convert them first.
        adjusted_location = screenshot.location_in_screenshot(
            Point.from_(location), CoordinatesType.CONTEXT_RELATIVE
        )
    else:
        adjusted_location = Point.from_(location)
    region = Region.from_(adjusted_location, element.size)

    if padding:
        region = region.padding(padding)
    return region


class GetSeleniumRegion(GetRegion, ABC):
    def get_regions(self, eyes, screenshot):
        # type: (SeleniumEyes, EyesWebDriverScreenshot) -> List[Region]
        elements = self._fetch_elements(eyes.driver)
        return [_region_from_element(el, screenshot, self._padding) for el in elements]

    def get_elements(self, driver):
        # type: (AnyWebDriver) -> List[AnyWebElement]
        return self._fetch_elements(driver)

    @abstractmethod
    def _fetch_elements(self, driver):
        # type: (AnyWebDriver) -> List[AnyWebElement]
        pass


@attr.s
class RegionByElement(GetSeleniumRegion):
    _element = attr.ib()  # type: AnyWebElement
    _padding = attr.ib(default=None)  # type: Optional[CodedRegionPadding]

    def _fetch_elements(self, driver):
        # type: (AnyWebDriver) -> List[AnyWebElement]
        return [self._element]


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
    _padding = attr.ib(default=None)  # type: Optional[CodedRegionPadding]

    def _fetch_elements(self, driver):
        # type: (AnyWebDriver) -> List[AnyWebElement]
        return driver.find_elements(self._by, self._value)


class GetSeleniumFloatingRegion(GetFloatingRegion, ABC):
    def get_regions(self, eyes, screenshot):
        # type: (SeleniumEyes, EyesWebDriverScreenshot) ->  List[FloatingMatchSettings]
        elements = self._fetch_elements(eyes.driver)
        regions = (_region_from_element(el, screenshot) for el in elements)
        return [
            FloatingMatchSettings(region, self.floating_bounds) for region in regions
        ]

    def get_elements(self, driver):
        # type: (AnyWebDriver) -> List[AnyWebElement]
        return self._fetch_elements(driver)

    @abstractmethod
    def _fetch_elements(self, driver):
        # type: (AnyWebDriver) -> List[AnyWebElement]
        pass


@attr.s
class FloatingRegionByElement(GetSeleniumFloatingRegion):
    """
    :ivar element: The element which represents the inner region (the floating part).
    :ivar bounds: The outer rectangle bounding the inner region.
    """

    _element = attr.ib()  # type: AnyWebElement
    _bounds = attr.ib()  # type: FloatingBounds

    def _fetch_elements(self, driver):
        # type: (AnyWebDriver) -> List[AnyWebElement]
        return [self._element]

    @property
    def floating_bounds(self):
        # type: () -> FloatingBounds
        return self._bounds


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

    def _fetch_elements(self, driver):
        # type: (AnyWebDriver) -> List[AnyWebElement]
        return driver.find_elements(self._by, self._value)

    @property
    def floating_bounds(self):
        # type: () -> FloatingBounds
        return self._bounds


class GetSeleniumAccessibilityRegion(GetAccessibilityRegion, ABC):
    def get_regions(self, eyes, screenshot):
        # type:(SeleniumEyes,EyesWebDriverScreenshot)->List[AccessibilityRegion]
        elements = self._fetch_elements(eyes.driver)
        regions = (_region_from_element(el, screenshot) for el in elements)
        return [
            AccessibilityRegion.from_(region, self.accessibility_type)
            for region in regions
        ]

    def get_elements(self, driver):
        # type: (AnyWebDriver) -> List[AnyWebElement]
        return self._fetch_elements(driver)

    @abstractmethod
    def _fetch_elements(self, driver):
        # type: (AnyWebDriver) -> List[AnyWebElement]
        pass


@attr.s
class AccessibilityRegionBySelector(GetSeleniumAccessibilityRegion):
    _by = attr.ib()  # type: str
    _value = attr.ib()  # type: str
    _type = attr.ib()  # type: AccessibilityRegionType

    def _fetch_elements(self, driver):
        # type: (AnyWebDriver) -> List[AnyWebElement]
        return driver.find_elements(self._by, self._value)

    @property
    def accessibility_type(self):
        # type: () -> AccessibilityRegionType
        return self._type


@attr.s
class AccessibilityRegionByElement(GetSeleniumAccessibilityRegion):
    _element = attr.ib()  # type: AnyWebElement
    _type = attr.ib()  # type: AccessibilityRegionType

    def _fetch_elements(self, driver):
        # type: (AnyWebDriver) -> List[AnyWebElement]
        return [self._element]

    @property
    def accessibility_type(self):
        # type: () -> AccessibilityRegionType
        return self._type
