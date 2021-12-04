import typing
from abc import abstractmethod

import attr

from applitools.common.accessibility import AccessibilityRegionType
from applitools.common.utils import ABC
from applitools.core import GetFloatingRegion, GetRegion
from applitools.core.fluent.region import GetAccessibilityRegion

if typing.TYPE_CHECKING:
    from typing import List, Optional

    from applitools.common import FloatingBounds
    from applitools.common.utils.custom_types import (
        AnyWebElement,
        CodedRegionPadding,
        WebDriver,
    )

__all__ = (
    "RegionBySelector",
    "RegionByElement",
    "FloatingRegionBySelector",
    "FloatingRegionByElement",
    "AccessibilityRegionBySelector",
    "AccessibilityRegionByElement",
)


class GetSeleniumRegion(GetRegion, ABC):
    def get_elements(self, driver):
        # type: (WebDriver) -> List[AnyWebElement]
        return self._fetch_elements(driver)

    @abstractmethod
    def _fetch_elements(self, driver):
        # type: (WebDriver) -> List[AnyWebElement]
        pass


@attr.s
class RegionByElement(GetSeleniumRegion):
    _element = attr.ib()  # type: AnyWebElement
    _padding = attr.ib(default=None)  # type: Optional[CodedRegionPadding]

    def _fetch_elements(self, driver):
        # type: (WebDriver) -> List[AnyWebElement]
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
        # type: (WebDriver) -> List[AnyWebElement]
        return driver.find_elements(self._by, self._value)


class GetSeleniumFloatingRegion(GetFloatingRegion, ABC):
    def get_elements(self, driver):
        # type: (WebDriver) -> List[AnyWebElement]
        return self._fetch_elements(driver)

    @abstractmethod
    def _fetch_elements(self, driver):
        # type: (WebDriver) -> List[AnyWebElement]
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
        # type: (WebDriver) -> List[AnyWebElement]
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
        # type: (WebDriver) -> List[AnyWebElement]
        return driver.find_elements(self._by, self._value)

    @property
    def floating_bounds(self):
        # type: () -> FloatingBounds
        return self._bounds


class GetSeleniumAccessibilityRegion(GetAccessibilityRegion, ABC):
    def get_elements(self, driver):
        # type: (WebDriver) -> List[AnyWebElement]
        return self._fetch_elements(driver)

    @abstractmethod
    def _fetch_elements(self, driver):
        # type: (WebDriver) -> List[AnyWebElement]
        pass


@attr.s
class AccessibilityRegionBySelector(GetSeleniumAccessibilityRegion):
    _by = attr.ib()  # type: str
    _value = attr.ib()  # type: str
    _type = attr.ib()  # type: AccessibilityRegionType

    def _fetch_elements(self, driver):
        # type: (WebDriver) -> List[AnyWebElement]
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
        # type: (WebDriver) -> List[AnyWebElement]
        return [self._element]

    @property
    def accessibility_type(self):
        # type: () -> AccessibilityRegionType
        return self._type
