import abc
import typing
from abc import ABC

import attr

from applitools.common.geometry import Region
from applitools.common.match import FloatingMatchSettings
from applitools.common.accessibility import AccessibilityRegionType
from applitools.common.utils import ABC
from applitools.common.utils.json_utils import JsonInclude

if typing.TYPE_CHECKING:
    from typing import List

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
    @abc.abstractmethod
    def get_regions(self, eyes, screenshot):
        # type: (EyesBase, EyesScreenshot) -> List
        pass


class GetAccessibilityRegion(GetRegion):
    @abc.abstractmethod
    def get_regions(self, eyes, screenshot):
        # type: (EyesBase, EyesScreenshot) -> List
        pass


@attr.s
class RegionByRectangle(GetRegion):
    _region = attr.ib()  # type: Region

    def get_regions(self, eyes, screenshot):
        # type: (EyesBase, EyesScreenshot) -> List[Region]
        return [self._region]


@attr.s
class FloatingRegionByRectangle(GetFloatingRegion):
    _rect = attr.ib()  # type: Region
    _bounds = attr.ib()

    def get_regions(self, eyes, screenshot):
        # type: (EyesBase, EyesScreenshot) -> List[FloatingMatchSettings]
        return [FloatingMatchSettings(self._rect, self._bounds)]


@attr.s
class AccessibilityRegionByRectangle(GetAccessibilityRegion):
    left = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    top = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    width = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    height = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    type = attr.ib(
        converter=AccessibilityRegionType,
        type=AccessibilityRegionType,
        metadata={JsonInclude.THIS: True},
    )  # type: AccessibilityRegionType

    @classmethod
    def from_(cls, region, type):
        return cls(
            left=region.left,
            top=region.top,
            width=region.width,
            height=region.height,
            type=type,
        )

    def get_regions(self, eyes, screenshot):
        # type: (EyesBase, EyesScreenshot) -> List[AccessibilityRegionByRectangle]
        return [self]
