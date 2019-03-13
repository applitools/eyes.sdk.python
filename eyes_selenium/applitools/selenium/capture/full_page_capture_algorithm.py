import typing

import attr
from PIL import Image
from selenium.common.exceptions import WebDriverException

from applitools.common import CoordinatesType, Point, RectangleSize, Region, logger
from applitools.common.utils import argument_guard, image_utils
from applitools.core import PositionProvider
from applitools.core.cut import NullCutProvider
from applitools.selenium.capture import EyesWebDriverScreenshot

if typing.TYPE_CHECKING:
    from typing import Optional
    from applitools.core.scaling import ScaleProvider
    from applitools.core.debug import DebugScreenshotProvider
    from applitools.selenium.region_compensation import RegionPositionCompensation
    from applitools.core.capture import EyesScreenshotFactory, ImageProvider
    from applitools.core.cut import CutProvider


@attr.s
class FullPageCaptureAlgorithm(object):
    MIN_SCREENSHOT_PART_HEIGHT = 10

    wait_before_screenshots = attr.ib()  # type: int
    debug_screenshots_provider = attr.ib()  # type: DebugScreenshotProvider
    screenshot_factory = attr.ib()  # type: EyesScreenshotFactory
    origin_provider = attr.ib()  # type: PositionProvider
    scale_provider = attr.ib()  # type: ScaleProvider
    cut_provider = attr.ib()  # type: CutProvider
    stitching_overlap = attr.ib()  # type: int
    image_provider = attr.ib()  # type: ImageProvider
    region_position_compensation = attr.ib()  # type: RegionPositionCompensation
    position_provider = attr.ib()  # type: PositionProvider

    def get_stitched_region(self, region, full_area, position_provider):
        # type: (Region, Optional[Region], Optional[PositionProvider]) -> Image.Image
        argument_guard.not_none(region)
        argument_guard.not_none(position_provider)
        if position_provider is None:
            position_provider = self.position_provider

        logger.info("get_stitched_region()")
        logger.info("PositionProvider: %s ; Region: %s" % (position_provider, region))

        self.origin_provider.push_state()
        self.origin_provider.set_position(
            Point.zero()
        )  # first scroll to 0,0 so CSS stitching works.

        # Saving the original position (in case we were already in the outermost frame).
        position_provider.push_state()
        logger.info("Getting top/left image...")
        image = self.image_provider.get_image()
        self.debug_screenshots_provider.save(image, "original")
        pixel_ratio = self._get_pixel_ratio(image)
        scaled_cut_provider = self.cut_provider.scale(pixel_ratio)
        # breakpoint()
        image = self._cut_if_needed(image, scaled_cut_provider)
        region_in_screenshot = self._get_region_in_screenshot(
            region, image, pixel_ratio
        )
        image = self._crop_if_needed(image, region_in_screenshot)
        image = self._scale_if_needed(image, pixel_ratio)
        if full_area is None or full_area.is_empty:
            entire_size = self._get_entire_size(image, position_provider)
            # Notice that this might still happen even if we used
            # "getImagePart", since "entirePageSize" might be that of a frame
            if image.width >= entire_size.width and image.height >= entire_size.height:
                self.origin_provider.pop_state()
                return image

            full_area = Region.from_location_size(Point.zero(), entire_size)

        image_parts = self._get_image_parts(full_area, image)

        stitched_image = self._create_stitched_image(full_area, image)

        # These will be used for storing the actual stitched size (it is
        # sometimes less than the size extracted via "getEntireSize").
        last_successful_location = Point.zero()
        last_successful_part_size = RectangleSize.from_image(image)

        # Take screenshot and stitch for each screenshot part
        logger.debug("Getting the rest of the image parts...")
        part_image = None
        for part_region in image_parts:
            logger.debug("Taking screenshot for %s" % part_region)

            # Scroll to the part's top/left
            origin_position = position_provider.set_position(part_region.location)
            target_position = origin_position.offset(-full_area.left, -full_area.top)
            logger.debug("Origin Position is set to %s" % origin_position)
            logger.debug("Target Position is %s" % target_position)

            # Actually taking the screenshot.
            logger.debug("Getting image...")
            part_image = self.image_provider.get_image()
            self.debug_screenshots_provider.save(
                part_image,
                "original-scrolled-{}".format(position_provider.get_current_position()),
            )
            part_image = self._cut_if_needed(part_image, scaled_cut_provider)
            part_image = self._crop_if_needed(part_image, region_in_screenshot)
            part_image = self._scale_if_needed(part_image, pixel_ratio)

            # Stitching the current part.
            stitched_image.paste(part_image, box=(target_position.x, target_position.y))
            last_successful_location = origin_position

        if part_image:
            last_successful_part_size = RectangleSize.from_image(part_image)
        logger.info("Stitching done!")
        position_provider.pop_state()
        self.origin_provider.pop_state()

        # If the actual image size is smaller than the extracted size, we crop the image.
        stitched_image = self._crop_if_smaller(
            full_area,
            last_successful_location,
            last_successful_part_size,
            stitched_image,
        )

        self.debug_screenshots_provider.save(stitched_image, "stitched")
        return stitched_image

    def _crop_if_smaller(
        self,
        full_area,
        last_successful_location,
        last_successful_part_size,
        stitched_image,
    ):
        act_image_width = last_successful_location.x + last_successful_part_size.width
        act_image_height = last_successful_location.y + last_successful_part_size.height
        logger.info("Extracted entire size: {}".format(full_area.size))
        logger.info(
            "Actual stitched size: {} x {}".format(act_image_width, act_image_height)
        )
        self.debug_screenshots_provider.save(stitched_image, "_stitched_before_trim")
        if (
            act_image_width < stitched_image.width
            or act_image_height < stitched_image.height
        ):
            logger.info("Trimming unnecessary margins...")
            stitched_image = image_utils.get_image_part(
                stitched_image,
                Region(
                    0,
                    0,
                    min([act_image_width, stitched_image.width]),
                    min([act_image_height, stitched_image.height]),
                ),
            )
            logger.info("Done")
        return stitched_image

    def _create_stitched_image(self, full_area, image):
        logger.debug("Creating stitchedImage container.")
        # Starting with element region size part of the screenshot. Use it as a size template.
        stitched_image = Image.new("RGBA", (full_area.width, full_area.height))
        # Starting with the screenshot we already captured at (0,0).
        stitched_image.paste(image, box=(0, 0))
        return stitched_image

    def _get_entire_size(self, image, position_provider):
        try:
            entire_size = position_provider.get_entire_size()
            logger.info("Entire size of region context: {}".format(entire_size))
        except WebDriverException as e:
            logger.warning(
                "Failed to extract entire size of region context {}".format(e)
            )
            logger.debug(
                "Using image size instead: {} x()".format(image.width, image.height)
            )
            entire_size = RectangleSize(image.width, image.height)
        return entire_size

    def _scale_if_needed(self, image, pixel_ratio):
        if pixel_ratio != 1.0:
            image = image_utils.scale_image(image, 1.0 / pixel_ratio)
            self.debug_screenshots_provider.save(image, "scalled")
        return image

    def _crop_if_needed(self, image, region_in_screenshot):
        if not region_in_screenshot.is_size_empty:
            image = image_utils.get_image_part(image, region_in_screenshot)
            self.debug_screenshots_provider.save(image, "cropper")
        return image

    def _cut_if_needed(self, image, scaled_cut_provider):
        if not isinstance(scaled_cut_provider, NullCutProvider):
            image = scaled_cut_provider.cut(image)
            self.debug_screenshots_provider.save(image, "original-cut")
        return image

    def _get_pixel_ratio(self, image):
        self.scale_provider.update_scale_ratio(image.width)
        pixel_ratio = 1 / self.scale_provider.scale_ratio
        return pixel_ratio

    def _get_image_parts(self, full_area, image):
        # The screenshot part is a bit smaller than the screenshot size,
        # in order to eliminate duplicate bottom scroll bars, as well as fixed
        # position footers.
        part_image_size = RectangleSize(
            image.width,
            max(
                [image.height - self.stitching_overlap, self.MIN_SCREENSHOT_PART_HEIGHT]
            ),
        )
        logger.info(
            "entire page region: %s, image part size: %s" % (full_area, part_image_size)
        )
        # Getting the list of sub-regions composing the whole region (we'll take
        # screenshot for each one).
        image_parts = full_area.get_sub_regions(part_image_size)  # type: Region
        return image_parts

    def _get_region_in_screenshot(self, region, image, pixel_ratio):
        if region.is_size_empty:
            return region
        logger.info("Creating screenshot object...")
        #  We need the screenshot to be able to convert the region to screenshot coordinates.

        screenshot = self.screenshot_factory.make_screenshot(
            image
        )  # type: EyesWebDriverScreenshot
        logger.info("Getting region in screenshot...")

        region_in_screenshot = screenshot.intersected_region(
            region, CoordinatesType.SCREENSHOT_AS_IS
        )
        logger.info("Region in screenshot: {}".format(region_in_screenshot))

        region_in_screenshot = region_in_screenshot.scale(pixel_ratio)
        logger.info("Scaled region: {}".format(region_in_screenshot))

        region_in_screenshot = self.region_position_compensation.compensate_region_position(
            region_in_screenshot, pixel_ratio
        )
        # Handling a specific case where the region is actually larger than
        # the screenshot (e.g., when body width/height are set to 100%, and
        # an internal div is set to value which is larger than the viewport).
        region_in_screenshot.intersect(Region(0, 0, image.width, image.height))
        logger.info("Region after intersect: {}".format(region_in_screenshot))
        return region_in_screenshot
