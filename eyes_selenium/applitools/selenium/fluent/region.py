import typing

import attr

from applitools.common.accessibility import AccessibilityRegionType
from applitools.core.fluent.region import (
    GetAccessibilityRegion,
    GetFloatingRegion,
    GetRegion,
)

if typing.TYPE_CHECKING:
    from typing import Optional

    from applitools.common import FloatingBounds
    from applitools.common.utils.custom_types import AnyWebElement, CodedRegionPadding
    from applitools.selenium.fluent.target_path import Locator

__all__ = (
    "RegionBySelector",
    "RegionByElement",
    "FloatingRegionBySelector",
    "FloatingRegionByElement",
    "AccessibilityRegionBySelector",
    "AccessibilityRegionByElement",
)


class GetSeleniumRegion(GetRegion):
    pass


@attr.s
class RegionByElement(GetSeleniumRegion):
    _element = attr.ib()  # type: AnyWebElement
    _padding = attr.ib(default=None)  # type: Optional[CodedRegionPadding]


@attr.s
class RegionBySelector(GetSeleniumRegion):
    """
    :param by: The "by" part of a selenium selector for an element which
               represents the ignore region
    :param value: The "value" part of a selenium selector for
                  an element which represents the ignore region.
    """

    _target_path = attr.ib()  # type: Locator
    _padding = attr.ib(default=None)  # type: Optional[CodedRegionPadding]


class GetSeleniumFloatingRegion(GetFloatingRegion):
    pass


@attr.s
class FloatingRegionByElement(GetSeleniumFloatingRegion):
    """
    :ivar element: The element which represents the inner region (the floating part).
    :ivar bounds: The outer rectangle bounding the inner region.
    """

    _element = attr.ib()  # type: AnyWebElement
    _bounds = attr.ib()  # type: FloatingBounds


@attr.s
class FloatingRegionBySelector(GetSeleniumFloatingRegion):
    """
    :ivar by: The selenium By
    :ivar value: The css selector for an element which represents the inner region.
    :ivar bounds: The outer rectangle bounding the inner region.
    """

    _target_path = attr.ib()  # type: Locator
    _bounds = attr.ib()  # type: FloatingBounds


class GetSeleniumAccessibilityRegion(GetAccessibilityRegion):
    pass


@attr.s
class AccessibilityRegionBySelector(GetSeleniumAccessibilityRegion):
    _target_path = attr.ib()  # type: Locator
    _type = attr.ib()  # type: AccessibilityRegionType


@attr.s
class AccessibilityRegionByElement(GetSeleniumAccessibilityRegion):
    _element = attr.ib()  # type: AnyWebElement
    _type = attr.ib()  # type: AccessibilityRegionType
