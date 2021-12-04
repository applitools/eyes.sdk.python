import typing

import attr

from applitools.common.accessibility import AccessibilityRegionType
from applitools.common.utils import ABC
from applitools.core import GetFloatingRegion, GetRegion
from applitools.core.fluent.region import GetAccessibilityRegion

if typing.TYPE_CHECKING:
    from typing import Optional

    from applitools.common import FloatingBounds
    from applitools.common.utils.custom_types import AnyWebElement, CodedRegionPadding

__all__ = (
    "RegionBySelector",
    "RegionByElement",
    "FloatingRegionBySelector",
    "FloatingRegionByElement",
    "AccessibilityRegionBySelector",
    "AccessibilityRegionByElement",
)


class GetSeleniumRegion(GetRegion, ABC):
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

    _by = attr.ib()
    _value = attr.ib()
    _padding = attr.ib(default=None)  # type: Optional[CodedRegionPadding]


class GetSeleniumFloatingRegion(GetFloatingRegion, ABC):
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

    _by = attr.ib()  # type: str
    _value = attr.ib()  # type: str
    _bounds = attr.ib()  # type: FloatingBounds


class GetSeleniumAccessibilityRegion(GetAccessibilityRegion, ABC):
    pass


@attr.s
class AccessibilityRegionBySelector(GetSeleniumAccessibilityRegion):
    _by = attr.ib()  # type: str
    _value = attr.ib()  # type: str
    _type = attr.ib()  # type: AccessibilityRegionType


@attr.s
class AccessibilityRegionByElement(GetSeleniumAccessibilityRegion):
    _element = attr.ib()  # type: AnyWebElement
    _type = attr.ib()  # type: AccessibilityRegionType
