import math
import typing

import attr
from PIL import Image
from selenium.common.exceptions import WebDriverException

from applitools.common import CoordinatesType, Point, RectangleSize, Region, logger
from applitools.common.utils import argument_guard, datetime_utils, image_utils
from applitools.core import PositionMemento, PositionProvider
from applitools.core.cut import NullCutProvider
from applitools.selenium.capture import EyesWebDriverScreenshot

if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional

    from applitools.common import ScaleProvider
    from applitools.common.geometry import SubregionForStitching
    from applitools.core.capture import EyesScreenshotFactory, ImageProvider
    from applitools.core.cut import CutProvider
    from applitools.core.debug import DebugScreenshotsProvider
    from applitools.selenium.region_compensation import RegionPositionCompensation


@attr.s
class FullPageCaptureAlgorithm(object):
    MIN_SCREENSHOT_PART_SIZE = 10

    wait_before_screenshots = attr.ib()  # type: int
    debug_screenshots_provider = attr.ib()  # type: DebugScreenshotsProvider
    screenshot_factory = attr.ib()  # type: EyesScreenshotFactory
    origin_provider = attr.ib()  # type: PositionProvider
    scale_provider = attr.ib()  # type: ScaleProvider
    cut_provider = attr.ib()  # type: CutProvider
    stitch_overlap = attr.ib()  # type: int
    image_provider = attr.ib()  # type: ImageProvider
    region_position_compensation = attr.ib()  # type: RegionPositionCompensation

    def _debug_msg(self, msg):
        return "{}_{}".format(
            self.region_position_compensation._useragent.browser.name, msg
        )

    def get_stitched_region(self, region, full_area, position_provider):
        # type: (Region, Optional[Region], Optional[PositionProvider]) -> Image.Image
        argument_guard.not_none(region)
        argument_guard.not_none(position_provider)

        logger.debug(
            "region: %s ; full_area: %s ; position_provider: %s"
            % (region, full_area, position_provider.__class__.__name__)
        )

        origin_state = self.origin_provider.get_state()

        if self.origin_provider != position_provider:
            self.origin_provider.set_position(
                Point.ZERO()
            )  # first scroll to 0,0 so CSS stitching works.

        # Saving the original position (in case we were already in the outermost frame).
        original_stitched_state = position_provider.get_state()

        datetime_utils.sleep(self.wait_before_screenshots)
        initial_screenshot = self.image_provider.get_image()
        initial_size = RectangleSize.from_(initial_screenshot)

        pixel_ratio = self._get_pixel_ratio(initial_screenshot)
        scaled_cut_provider = self.cut_provider.scale(pixel_ratio)
        cutted_initial_screenshot = self._cut_if_needed(
            initial_screenshot, scaled_cut_provider
        )
        self.debug_screenshots_provider.save(
            cutted_initial_screenshot, self._debug_msg("cutted_initial_screenshot")
        )

        region_in_initial_screenshot = self._get_region_in_screenshot(
            region, cutted_initial_screenshot, pixel_ratio
        )
        cropped_initial_screenshot = self._crop_if_needed(
            cutted_initial_screenshot, region_in_initial_screenshot
        )
        self.debug_screenshots_provider.save(
            cropped_initial_screenshot, self._debug_msg("cropped_initial_screenshot")
        )

        scaled_initial_screenshot = image_utils.scale_image(
            cropped_initial_screenshot, self.scale_provider
        )
        self.debug_screenshots_provider.save(
            scaled_initial_screenshot, self._debug_msg("scaled_initial_screenshot")
        )
        if full_area is None or full_area.is_empty:
            entire_size = self._get_entire_size(initial_screenshot, position_provider)
            # Notice that this might still happen even if we used
            # "get_image_part", since "entire_page_size" might be that of a
            # frame
            if (
                scaled_initial_screenshot.width >= entire_size.width
                and scaled_initial_screenshot.height >= entire_size.height
            ):
                self.origin_provider.restore_state(origin_state)
                return scaled_initial_screenshot

            full_area = Region.from_(Point.ZERO(), entire_size)

        scaled_cropped_location = full_area.location
        physical_crop_location = Point.from_(scaled_cropped_location).scale(pixel_ratio)

        if region_in_initial_screenshot.is_empty:
            physical_crop_size = RectangleSize(
                initial_size.width - physical_crop_location.x,
                initial_size.height - physical_crop_location.y,
            )
            source_region = Region.from_(physical_crop_location, physical_crop_size)
        else:
            # Starting with the screenshot we already captured at (0,0).
            source_region = region_in_initial_screenshot

        scaled_cropped_source_rect = self.cut_provider.to_region(source_region.size)
        scaled_cropped_source_rect = scaled_cropped_source_rect.offset(
            source_region.left, source_region.top
        )
        scaled_cropped_source_region = dict(
            x=int(math.ceil(scaled_cropped_source_rect.left / pixel_ratio)),
            y=int(math.ceil(scaled_cropped_source_rect.top / pixel_ratio)),
            width=int(math.ceil(scaled_cropped_source_rect.width / pixel_ratio)),
            height=int(math.ceil(scaled_cropped_source_rect.height / pixel_ratio)),
        )
        scaled_cropped_size = dict(
            width=scaled_cropped_source_region["width"],
            height=scaled_cropped_source_region["height"],
        )

        # Getting the list of viewport regions composing the page
        # (we'll take screenshot for each one).
        if region_in_initial_screenshot.is_empty:
            x = max(0, full_area.left)
            y = max(0, full_area.top)
            w = min(full_area.width, scaled_cropped_size["width"])
            h = min(full_area.height, scaled_cropped_size["height"])
            rect_in_initial_screenshot = Region(
                round(x * pixel_ratio),
                round(y * pixel_ratio),
                round(w * pixel_ratio),
                round(h * pixel_ratio),
            )
        else:
            rect_in_initial_screenshot = region_in_initial_screenshot

        screenshot_parts = self._get_image_parts(
            full_area, scaled_cropped_size, pixel_ratio, rect_in_initial_screenshot
        )

        # Starting with element region size part of the screenshot. Use it as a size
        # template.
        stitched_image = Image.new("RGBA", (full_area.width, full_area.height))
        # Take screenshot and stitch for each screenshot part.
        stitched_image = self._stitch_screenshot(
            original_stitched_state,
            position_provider,
            screenshot_parts,
            stitched_image,
            self.scale_provider.scale_ratio,
            scaled_cut_provider,
        )
        position_provider.restore_state(original_stitched_state)
        self.origin_provider.restore_state(origin_state)
        return stitched_image

    def _stitch_screenshot(
        self,
        original_stitch_state,  # type: PositionMemento
        stitch_provider,  # type: PositionProvider
        screenshot_parts,  # type: List[SubregionForStitching]
        stitched_image,  # type: Image.Image
        scale_ratio,  # type: float
        scaled_cut_provider,  # type: CutProvider
    ):
        # type: (...) -> Image
        logger.debug("Enter: scale_ratio {}".format(scale_ratio))
        for part_region in screenshot_parts:
            logger.debug("Part: {}".format(part_region))
            # Scroll to the part's top/left
            part_region_location = part_region.scroll_to.offset(
                original_stitch_state.position
            )
            origin_position = stitch_provider.set_position(part_region_location)

            target_position = part_region.paste_physical_location.offset(
                part_region_location - origin_position
            )

            # Actually taking the screenshot.
            datetime_utils.sleep(self.wait_before_screenshots)
            part_image = self.image_provider.get_image()
            self.debug_screenshots_provider.save(
                part_image, self._debug_msg("part_image")
            )

            cut_part = scaled_cut_provider.cut(part_image)
            self.debug_screenshots_provider.save(cut_part, self._debug_msg("cut_part"))

            r = part_region.physical_crop_area
            if not r.is_size_empty:
                cropped_part = image_utils.crop_image(cut_part, r)
            else:
                cropped_part = cut_part
            self.debug_screenshots_provider.save(
                cropped_part, self._debug_msg("cropped_part")
            )
            scaled_part_image = image_utils.scale_image(cropped_part, scale_ratio)
            self.debug_screenshots_provider.save(
                scaled_part_image, self._debug_msg("scaled_part_image")
            )

            r2 = part_region.logical_crop_area
            scaled_cropped_part_image = image_utils.crop_image(scaled_part_image, r2)
            self.debug_screenshots_provider.save(
                scaled_cropped_part_image, self._debug_msg("scaled_cropped_part_image")
            )

            logger.debug("pasting part at {}".format(target_position))
            image_utils.paste_image(
                stitched_image, scaled_cropped_part_image, target_position
            )
            self.debug_screenshots_provider.save(
                stitched_image, self._debug_msg("stitched_image")
            )
        return stitched_image

    def _crop_if_smaller(
        self,
        full_area,
        last_successful_location,
        last_successful_part_size,
        stitched_image,
    ):
        # type: (Region, Point, RectangleSize, Image) -> Image
        act_image_width = last_successful_location.x + last_successful_part_size.width
        act_image_height = last_successful_location.y + last_successful_part_size.height
        logger.info("Extracted entire size: {}".format(full_area.size))
        logger.info(
            "Actual stitched size: {} x {}".format(act_image_width, act_image_height)
        )
        self.debug_screenshots_provider.save(
            stitched_image, self._debug_msg("_stitched_before_trim")
        )
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
            logger.info("Done trimming unnecessary margins..")
        return stitched_image

    def _get_entire_size(self, image, position_provider):
        # type: (Image, PositionProvider) -> RectangleSize
        try:
            entire_size = position_provider.get_entire_size()
            logger.info("Entire size of region context: {}".format(entire_size))
        except WebDriverException as e:
            logger.warning(
                "Failed to extract entire size of region context {}".format(e)
            )
            logger.debug(
                "Using image size instead: {} x {}".format(image.width, image.height)
            )
            entire_size = RectangleSize(image.width, image.height)
        return entire_size

    def _crop_if_needed(self, image, region_in_screenshot):
        # type: (Image, Region) -> Image
        if not region_in_screenshot.is_size_empty:
            image = image_utils.get_image_part(image, region_in_screenshot)
        return image

    def _cut_if_needed(self, image, scaled_cut_provider):
        # type: (Image, NullCutProvider) -> Image
        if not isinstance(scaled_cut_provider, NullCutProvider):
            image = scaled_cut_provider.cut(image)
        return image

    def _get_pixel_ratio(self, image):
        # type: (Image) -> float
        self.scale_provider.update_scale_ratio(image.width)
        return 1.0 / self.scale_provider.scale_ratio

    def _get_image_parts(
        self, full_area, scaled_cropped_size, pixel_ratio, rect_in__initial_screenshot
    ):
        # type: (Region, Dict, float, Region) -> List[SubregionForStitching]
        # The screenshot part is a bit smaller than the screenshot size,
        # in order to eliminate duplicate bottom scroll bars, as well as fixed
        # position footers.
        part_image_size = RectangleSize(
            max(scaled_cropped_size["width"], self.MIN_SCREENSHOT_PART_SIZE),
            max(scaled_cropped_size["height"], self.MIN_SCREENSHOT_PART_SIZE),
        )
        logger.info(
            "Entire page region: %s, image part size: %s" % (full_area, part_image_size)
        )
        # Getting the list of sub-regions composing the whole region (we'll take
        # screenshot for each one).
        image_parts = full_area.get_sub_regions(
            part_image_size,
            self.stitch_overlap,
            pixel_ratio,
            rect_in__initial_screenshot,
        )
        return image_parts

    def _get_region_in_screenshot(self, region, image, pixel_ratio):
        # type: (Region, Image, float) -> Region
        if region.is_size_empty:
            return region
        logger.debug("Creating screenshot object...")
        #  We need the screenshot to be able to convert the region to screenshot coordinates.
        screenshot = self.screenshot_factory.make_screenshot(
            image
        )  # type: EyesWebDriverScreenshot
        logger.info("Getting region in screenshot...")

        region_in_screenshot = screenshot.intersected_region(
            region, CoordinatesType.SCREENSHOT_AS_IS
        )
        logger.debug("Region in screenshot: {}".format(region_in_screenshot))
        region_in_screenshot = region_in_screenshot.scale(pixel_ratio)
        logger.debug("Scaled region: {}".format(region_in_screenshot))

        region_in_screenshot = (
            self.region_position_compensation.compensate_region_position(
                region_in_screenshot, pixel_ratio
            )
        )
        # Handling a specific case where the region is actually larger than
        # the screenshot (e.g., when body width/height are set to 100%, and
        # an internal div is set to value which is larger than the viewport).
        region_in_screenshot = region_in_screenshot.intersect(Region.from_(image))
        logger.info("Scaled and intersected region: {}".format(region_in_screenshot))
        return region_in_screenshot
