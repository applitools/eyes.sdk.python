import abc

from applitools.eyes_core import Region

__all__ = ('RegionProvider', 'NullRegionProvider')


class RegionProvider(abc.ABC):
    """
    Encapsulates a getRegion "callback" and how the region's coordinates should be used.
    """

    def get_region(self) -> Region:
        """
        :return: A region with "as is" viewport coordinates.
        """


class NullRegionProvider(RegionProvider):
    def get_region(self):
        return Region.create_empty_region()
