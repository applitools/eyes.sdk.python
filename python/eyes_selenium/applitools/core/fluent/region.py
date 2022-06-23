import typing

import attr

from applitools.common import FloatingBounds
from applitools.common.accessibility import AccessibilityRegionType
from applitools.common.geometry import AccessibilityRegion, Rectangle, Region

if typing.TYPE_CHECKING:
    from typing import List, Optional, Union

    from applitools.common.utils.custom_types import CodedRegionPadding

__all__ = (
    "GetFloatingRegion",
    "GetRegion",
    "RegionByRectangle",
    "FloatingRegionByRectangle",
    "GetAccessibilityRegion",
    "AccessibilityRegionByRectangle",
)


class GetRegion(object):
    @property
    def padding(self):
        # type: () -> Optional[CodedRegionPadding]
        return getattr(self, "_padding", None)


class GetFloatingRegion(GetRegion):
    pass


class GetAccessibilityRegion(GetRegion):
    pass


@attr.s
class RegionByRectangle(GetRegion):
    _region = attr.ib()  # type: Union[Region, Rectangle]


@attr.s
class FloatingRegionByRectangle(GetFloatingRegion):
    _rect = attr.ib()  # type: Union[Region, Rectangle]
    _bounds = attr.ib()  # type: FloatingBounds

    @property
    def floating_bounds(self):
        return self._bounds


@attr.s
class AccessibilityRegionByRectangle(GetAccessibilityRegion):
    _rect = attr.ib()  # type: Union[Region, Rectangle, AccessibilityRegion]
    _type = attr.ib(default=None)  # type: Optional[AccessibilityRegionType]

    @property
    def accessibility_type(self):
        # type: () -> AccessibilityRegionType
        if self._type:
            return self._type
        return self._rect.type
