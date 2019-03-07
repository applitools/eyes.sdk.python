import abc
import typing

import attr

from applitools.common.geometry import Region

if typing.TYPE_CHECKING:
    from typing import List

    from applitools.core.eyes_base import EyesBase
    from applitools.common.capture import EyesScreenshot
    from applitools.common.match import FloatingMatchSettings

__all__ = (
    "GetFloatingRegion",
    "GetRegion",
    "IgnoreRegionByRectangle",
    "FloatingRegionByRectangle",
)


class GetFloatingRegion(abc.ABC):
    @abc.abstractmethod
    def get_region(self, eyes, screenshot):
        # type: (EyesBase, EyesScreenshot) -> List[FloatingMatchSettings]
        pass


class GetRegion(abc.ABC):
    @abc.abstractmethod
    def get_region(self, eyes, screenshot):
        # type: (EyesBase, EyesScreenshot) -> Region
        pass


@attr.s
class IgnoreRegionByRectangle(GetRegion):
    _region = attr.ib()  # type: Region

    def get_region(self, eyes, screenshot):
        # type: (EyesBase, EyesScreenshot) -> FloatingMatchSettings
        return [self._region]


@attr.s
class FloatingRegionByRectangle(GetFloatingRegion):
    _rect = attr.ib()  # type: Region
    _max_up_offset = attr.ib()
    _max_down_offset = attr.ib()
    _max_left_offset = attr.ib()
    _max_right_offset = attr.ib()

    def get_region(self, eyes, screenshot):
        # type: (EyesBase, EyesScreenshot) -> FloatingMatchSettings
        return FloatingMatchSettings(
            self._rect.left,
            self._rect.top,
            self._rect.width,
            self._rect.height,
            self._max_up_offset,
            self._max_down_offset,
            self._max_left_offset,
            self._max_right_offset,
        )
