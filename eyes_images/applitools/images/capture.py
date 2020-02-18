from applitools.common.capture import EyesScreenshot
from applitools.common.errors import CoordinatesTypeConversionError, OutOfBoundsError
from applitools.common.geometry import CoordinatesType, Point, Region
from applitools.common.utils import argument_guard, image_utils


class EyesImagesScreenshot(EyesScreenshot):
    """
    Encapsulates a screenshot taken by the images SDK.
    """

    SCREENSHOT_AS_IS = CoordinatesType.SCREENSHOT_AS_IS
    CONTEXT_RELATIVE = CoordinatesType.CONTEXT_RELATIVE

    def __init__(self, image, location=None):
        super(EyesImagesScreenshot, self).__init__(image)
        if location is None:
            location = Point.ZERO()
        argument_guard.is_a(location, Point)
        self._location = location
        self._bounds = Region.from_(location, self.image)

    def sub_screenshot(self, region, throw_if_clipped=False):
        # type: (Region, bool) -> EyesImagesScreenshot
        argument_guard.not_none(region)

        # We want to get the sub-screenshot in as-is coordinates type.
        sub_screenshot_region = self.intersected_region(region, self.SCREENSHOT_AS_IS)

        if sub_screenshot_region.is_size_empty and (
            throw_if_clipped or not sub_screenshot_region.size == region.size
        ):
            raise OutOfBoundsError(
                "Region [{}] is out of screenshot bounds [{}]".format(
                    region, self._bounds
                )
            )

        sub_screenshot_image = image_utils.get_image_part(
            self._image, sub_screenshot_region
        )

        # Notice that we need the bounds-relative coordinates as parameter
        # for new sub-screenshot.
        relative_sub_screenshot_region = self.convert_region_location(
            sub_screenshot_region, self.SCREENSHOT_AS_IS, self.CONTEXT_RELATIVE
        )
        return EyesImagesScreenshot(
            sub_screenshot_image, relative_sub_screenshot_region.location
        )

    def convert_location(self, location, from_, to):
        # type: (Point, CoordinatesType, CoordinatesType) -> Point
        argument_guard.not_none(location)
        argument_guard.not_none(from_)
        argument_guard.not_none(to)

        argument_guard.is_a(location, Point)

        result = location.clone()
        if from_ == to:
            return result

        if from_ == self.SCREENSHOT_AS_IS:
            if to == self.CONTEXT_RELATIVE:
                result = result.offset(self._bounds.left, self._bounds.top)
            else:
                raise CoordinatesTypeConversionError(from_, to)

        elif from_ == self.SCREENSHOT_AS_IS:
            if to == self.CONTEXT_RELATIVE:
                result = result.offset(-self._bounds.left, -self._bounds.top)
            else:
                raise CoordinatesTypeConversionError(from_, to)
        else:
            raise CoordinatesTypeConversionError(from_, to)

        return result

    def location_in_screenshot(self, location, coordinates_type):
        # type: (Point, CoordinatesType) -> Point
        argument_guard.not_none(location)
        argument_guard.not_none(coordinates_type)
        location = self.convert_location(
            location, coordinates_type, self.CONTEXT_RELATIVE
        )

        if not self._bounds.contains(location):
            raise OutOfBoundsError(
                "Point {} ('{}') is not visible in screenshot!".format(
                    location, coordinates_type
                )
            )

        return self.convert_location(
            location, self.CONTEXT_RELATIVE, self.SCREENSHOT_AS_IS
        )

    def intersected_region(self, region, coordinates_type):
        # type: (Region, CoordinatesType) -> Region
        argument_guard.not_none(region)
        argument_guard.not_none(coordinates_type)

        if region.is_size_empty:
            return Region.from_(region)

        intersected_region = self.convert_region_location(
            region, region.coordinates_type, self.CONTEXT_RELATIVE
        )
        intersected_region = intersected_region.intersect(self._bounds)

        if region.is_size_empty:
            return region

        intersected_region.location = self.convert_location(
            intersected_region.location, self.CONTEXT_RELATIVE, coordinates_type
        )
        return intersected_region
