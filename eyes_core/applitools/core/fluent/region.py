import abc
import typing

import attr

from applitools.common import FloatingBounds
from applitools.common.geometry import Region, AccessibilityRegion, Rectangle
from applitools.common.match import FloatingMatchSettings
from applitools.common.accessibility import AccessibilityRegionType
from applitools.common.utils import ABC

if typing.TYPE_CHECKING:
    from typing import List, Union, Optional

    from applitools.core.eyes_base import EyesBase
    from applitools.common.capture import EyesScreenshot

__all__ = (
    "GetFloatingRegion",
    "GetRegion",
    "RegionByRectangle",
    "FloatingRegionByRectangle",
    "GetAccessibilityRegion",
    "AccessibilityRegionByRectangle",
)


class GetRegion(ABC):
    @abc.abstractmethod
    def get_regions(self, eyes, screenshot):
        # type: (EyesBase, EyesScreenshot) -> List
        pass


class GetFloatingRegion(GetRegion):
    @property
    def floating_bounds(self):
        return self._bounds

    @abc.abstractmethod
    def get_regions(self, eyes, screenshot):
        # type: (EyesBase, EyesScreenshot) -> List
        pass


class GetAccessibilityRegion(GetRegion):
    @property
    def accessibility_type(self):
        if self._type:
            return self._type
        return self._rect.type

    @abc.abstractmethod
    def get_regions(self, eyes, screenshot):
        # type: (EyesBase, EyesScreenshot) -> List
        pass


@attr.s
class RegionByRectangle(GetRegion):
    _region = attr.ib()  # type: Union[Region, Rectangle]

    def get_regions(self, eyes, screenshot):
        # type: (EyesBase, EyesScreenshot) -> List[Region]
        return [Region.from_(self._region)]


@attr.s
class FloatingRegionByRectangle(GetFloatingRegion):
    _rect = attr.ib()  # type: Union[Region, Rectangle]
    _bounds = attr.ib()  # type: FloatingBounds

    def get_regions(self, eyes, screenshot):
        # type: (EyesBase, EyesScreenshot) -> List[FloatingMatchSettings]
        return [FloatingMatchSettings(self._rect, self._bounds)]


@attr.s
class AccessibilityRegionByRectangle(GetAccessibilityRegion):
    _rect = attr.ib()  # type: Union[Region, Rectangle, AccessibilityRegion]
    _type = attr.ib(default=None)  # type: Optional[AccessibilityRegionType]

    def get_regions(self, eyes, screenshot):
        # type: (EyesBase, EyesScreenshot) -> List[AccessibilityRegion]
        return [AccessibilityRegion.from_(self._rect, self._type)]
