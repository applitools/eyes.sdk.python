import typing as tp
from typing import Callable, Union

import attr

from applitools.common.geometry import Region
from applitools.common.utils import ABC

if tp.TYPE_CHECKING:
    from applitools.common.capture import EyesScreenshot


@attr.s
class RegionProvider(ABC):
    """
    Encapsulates a get_region "callback" and how the region's coordinates should be
    used.
    """

    _region = attr.ib()  # type: Union[Region, Callable]

    def get_region(self, eyes_screenshot=None):
        # type: (tp.Optional[EyesScreenshot]) -> Region
        """
        :return: A region with "as is" viewport coordinates.
        """
        if callable(self._region):
            return self._region()
        else:
            return self._region

    def __str__(self):
        return str(self._region)


@attr.s
class NullRegionProvider(RegionProvider):
    _region = attr.ib(init=False, factory=Region.EMPTY)  # type: Region


NULL_REGION_PROVIDER = NullRegionProvider()
