from applitools.core.utils import image_utils
from applitools.core import EyesScreenshot, Region, Point, OutOfBoundsError
from applitools.core.errors import CoordinatesTypeConversionError
from applitools.core.metadata import CoordinatesType


class EyesImagesScreenshot(EyesScreenshot):
    """
    Encapsulates a screenshot taken by the images SDK.
    """

    def __init__(self, image, location=None):
        super(EyesImagesScreenshot, self).__init__(image)
        if location is None:
            location = Point.create_top_left()
        self._location = location
        self._bounds = Region.from_location_size(location, dict(width=self._image.width,
                                                                height=self._image.height))

    def sub_screenshot(self, region, throw_if_clipped=False):
        # type: (Region, bool) -> Region
        assert region is not None

        sub_screenshot_region = self.intersected_region(region, CoordinatesType.SCREENSHOT_AS_IS)

        if (sub_screenshot_region.is_size_empty
                and (throw_if_clipped or not sub_screenshot_region.size == region.size)):
            raise OutOfBoundsError("Region [{}] is out of screenshot bounds [{}]".format(region, self._bounds))

        sub_screenshot_image = image_utils.get_image_part(self._image, sub_screenshot_region)

        # Notice that we need the bounds-relative coordinates as parameter for new sub-screenshot.
        relative_sub_screenshot_region = self.convert_region_location(sub_screenshot_region,
                                                                      CoordinatesType.SCREENSHOT_AS_IS,
                                                                      CoordinatesType.CONTEXT_RELATIVE)
        return EyesImagesScreenshot(sub_screenshot_image,
                                    relative_sub_screenshot_region.location)

    def convert_location(self, location, from_, to):
        # type: (Point, CoordinatesType, CoordinatesType) -> Point

        result = location.clone()
        if from_ == to:
            return result

        if from_ == CoordinatesType.SCREENSHOT_AS_IS:
            if to == CoordinatesType.CONTEXT_RELATIVE:
                result.offset(self._bounds.left, self._bounds.top)
            else:
                raise CoordinatesTypeConversionError(from_, to)

        elif from_ == CoordinatesType.SCREENSHOT_AS_IS:
            if to == CoordinatesType.CONTEXT_RELATIVE:
                result.offset(-self._bounds.left, -self._bounds.top)
            else:
                raise CoordinatesTypeConversionError(from_, to)
        else:
            raise CoordinatesTypeConversionError(from_, to)

        return result

    def location_in_screenshot(self, location, coordinates_type):
        # type: (Point, CoordinatesType) -> Point

        location = self.convert_location(location, coordinates_type,
                                         CoordinatesType.CONTEXT_RELATIVE)
        if not self._bounds.contains(location):
            raise OutOfBoundsError(
                "Point {} ('{}') is not visible in screenshot!".format(location, coordinates_type))

        return self.convert_location(location,
                                     CoordinatesType.CONTEXT_RELATIVE,
                                     CoordinatesType.SCREENSHOT_AS_IS)

    def intersected_region(self, region, result_coordinate_types):
        # type: (Region, CoordinatesType) -> Region
        assert region is not None
        if region.is_size_empty:
            return Region.from_region(region)

        intersected_region = self.convert_region_location(region, region.coordinates_type,
                                                          CoordinatesType.CONTEXT_RELATIVE)
        intersected_region.intersect(self._bounds)

        if region.is_size_empty:
            return region

        intersected_region.location = self.convert_location(intersected_region.location,
                                                            CoordinatesType.CONTEXT_RELATIVE, result_coordinate_types)
        return intersected_region
