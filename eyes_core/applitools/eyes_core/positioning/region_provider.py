import typing as tp

import attr

from applitools.eyes_core import Region
from applitools.eyes_core.utils import ABC

if tp.TYPE_CHECKING:
    from applitools.eyes_core import EyesScreenshot

__all__ = ('RegionProvider', 'NullRegionProvider', 'NULL_REGION_INSTANCE')


@attr.s
class RegionProvider(ABC):
    """
    Encapsulates a getRegion "callback" and how the region's coordinates should be used.
    """
    _region = attr.ib()

    def get_region(self, eyes_screenshot=None):
        # type: (tp.Optional[EyesScreenshot]) -> Region
        """
        :return: A region with "as is" viewport coordinates.
        """
        return self._region

    def __str__(self):
        return str(self._region)


@attr.s
class NullRegionProvider(RegionProvider):
    _region = attr.ib(init=False, factory=Region.create_empty_region)


NULL_REGION_INSTANCE = NullRegionProvider()
