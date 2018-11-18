import abc
import typing as tp

import attr

from .geometry import Point, Region
from .metadata import CoordinatesType
from .utils import ABC, image_utils

if tp.TYPE_CHECKING:
    from PIL import Image

__all__ = ('EyesScreenshot',)


@attr.s
class EyesScreenshot(ABC):
    """
     Base class for handling screenshots.
     """

    _image = attr.ib()  # type: Image.Image

    @abc.abstractmethod
    def sub_screenshot(self, region, throw_if_clipped=False):
        # type: (Region, bool) -> Region
        pass

    @abc.abstractmethod
    def convert_location(self, location, from_, to):
        # type: (Point, CoordinatesType, CoordinatesType) -> Point
        pass

    @abc.abstractmethod
    def location_in_screenshot(self, location, coordinates_type):
        # type: (Point, CoordinatesType) -> Point
        pass

    @abc.abstractmethod
    def intersected_region(self, region, original_coordinate_types, result_coordinate_types):
        # type: (Region, CoordinatesType, CoordinatesType) -> Region
        pass

    def convert_region_location(self, region, from_, to):
        # type: (Region, CoordinatesType, CoordinatesType) -> Region
        assert region is not None
        assert isinstance(region, Region)
        assert from_ is not None
        assert to is not None

        if region.is_empty:
            return Region.create_empty_region()

        updated_location = self.convert_location(region.location, from_, to)
        return Region(updated_location.x, updated_location.y, region.width, region.height)

    @property
    def image_region(self):
        # type: () -> Region
        return Region(0, 0, self.image.width, self.image.height, CoordinatesType.SCREENSHOT_AS_IS)

    @staticmethod
    def from_region(region):
        # type: (Region) -> Image.Image
        return Image.new('RGBA', (region.width, region.height))

    def get_bytes(self):
        # type: () -> bytes
        """
        Returns the bytes of the screenshot.

        :return: The bytes representation of the png.
        """
        return image_utils.get_bytes(self._image)
