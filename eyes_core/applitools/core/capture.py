import abc
import typing as tp

from .geometry import Point, Region
from .metadata import CoordinatesType
from .utils import ABC, image_utils, argument_guard

if tp.TYPE_CHECKING:
    from PIL import Image

__all__ = ('EyesScreenshot',)


class EyesScreenshot(ABC):
    """
     Base class for handling screenshots.
     """

    def __init__(self, image):
        # type: (Image.Image) -> None
        self._image = image  # type: Image.Image

    @abc.abstractmethod
    def sub_screenshot(self, region, throw_if_clipped=False):
        # type: (Region, bool) -> Region
        """
        Returns a part of the screenshot based on the given region.

        :param region:           The region for which we should get the sub screenshot.
        :param throw_if_clipped: Throw an EyesException if the region is not
                                 fully contained in the screenshot.
        :return: A screenshot instance containing the given region.
        """

    @abc.abstractmethod
    def convert_location(self, location, from_, to):
        # type: (Point, CoordinatesType, CoordinatesType) -> Point
        """
        Converts a location's coordinates with the `from_` coordinates type
        to the `to` coordinates type.

        :param location:  The location which coordinates needs to be converted.
        :param from_:     The current coordinates type for `location`.
        :param to:        The target coordinates type for `location`.
        :return A new location which is the transformation of `location` to
                the `to` coordinates type.
        """

    @abc.abstractmethod
    def location_in_screenshot(self, location, coordinates_type):
        # type: (Point, CoordinatesType) -> Point
        """
        Calculates the location in the screenshot of the location given as
        parameter.

        :param location:         The location as coordinates inside the current frame.
        :param coordinates_type: The coordinates type of `location`.
        :return: The corresponding location inside the screenshot,
                 in screenshot as-is coordinates type.
        :raise: `OutOfBoundsException` If the location is
                not inside the frame's region in the screenshot.
        """

    @abc.abstractmethod
    def intersected_region(self, region, coordinates_type):
        # type: (Region, CoordinatesType) -> Region
        """
        Get the intersection of the given region with the screenshot.

        :param region:          The region to intersect.
        :param coordinates_type: The coordinates type of `region`.
        :return The intersected region, in `coordinates_type` coordinates.
        """

    def convert_region_location(self, region, from_, to):
        # type: (Region, CoordinatesType, CoordinatesType) -> Region
        """
        Converts a region's location coordinates with the `from_`
        coordinates type to the `to` coordinates type.

        :param region: The region which location's coordinates needs to be converted.
        :param from_:  The current coordinates type for `region`.
        :param to:     The target coordinates type for `region`.
        :return:       A new region which is the transformation of `region` to
                       the `to` coordinates type.
        """
        argument_guard.not_none(region)
        argument_guard.is_a(region, Region)
        if region.is_size_empty:
            return Region.create_empty_region()

        argument_guard.not_none(from_)
        argument_guard.not_none(to)

        updated_location = self.convert_location(region.location, from_, to)
        return Region(updated_location.x, updated_location.y, region.width, region.height)

    @property
    def image_region(self):
        # type: () -> Region
        return Region(0, 0, self._image.width, self._image.height, CoordinatesType.SCREENSHOT_AS_IS)

    @property
    def bytes(self):
        # type: () -> bytes
        """
        Returns the bytes of the screenshot.

        :return: The bytes representation of the png.
        """
        return image_utils.get_bytes(self._image)
