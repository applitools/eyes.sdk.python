import abc
import typing

import attr

from applitools.common.geometry import Region
from applitools.common.match import FloatingMatchSettings
from applitools.common.utils import ABC

if typing.TYPE_CHECKING:
    from typing import List

    from applitools.core.eyes_base import EyesBase
    from applitools.common.capture import EyesScreenshot

__all__ = (
    "GetFloatingRegion",
    "GetRegion",
    "RegionByRectangle",
    "FloatingRegionByRectangle",
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
