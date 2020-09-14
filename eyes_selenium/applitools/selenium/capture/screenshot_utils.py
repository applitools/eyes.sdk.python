from enum import Enum
from typing import TYPE_CHECKING, Optional

from applitools.common import Point, Region, logger
from applitools.common.utils import image_utils
from applitools.selenium import eyes_selenium_utils

if TYPE_CHECKING:
    from PIL import Image

    from applitools.selenium.webdriver import EyesWebDriver


class ScreenshotType(Enum):
    VIEWPORT = "VIEWPORT"
    ENTIRE_FRAME = "ENTIRE_FRAME"


def update_screenshot_type(screenshot_type, image, driver):
    # type: ( Optional[ScreenshotType], Image, EyesWebDriver) -> ScreenshotType
    if screenshot_type is None:
        viewport_size = driver.eyes.configure.viewport_size
        scale_viewport = driver.eyes.should_stitch_content

        if scale_viewport:
            pixel_ratio = driver.eyes.device_pixel_ratio
            viewport_size = viewport_size.scale(pixel_ratio)
        if (
            image.width <= viewport_size["width"]
            and image.height <= viewport_size["height"]
        ):
            screenshot_type = ScreenshotType.VIEWPORT
        else:
            screenshot_type = ScreenshotType.ENTIRE_FRAME
    return screenshot_type


def cut_to_viewport_size_if_required(driver, image):
    # type: (EyesWebDriver, Image) -> Image
    # Some browsers return always full page screenshot (IE).
    # So we cut such images to viewport size

    cur_position = driver.eyes._original_scroll_position
    if cur_position:
        top = cur_position.y
    else:
        top = 0

    screenshot_type = update_screenshot_type(None, image, driver)
    if screenshot_type != ScreenshotType.VIEWPORT:
        viewport_size = driver.eyes.configure.viewport_size
        image = image_utils.crop_image(
            image,
            region_to_crop=Region(
                top=top,
                left=0,
                height=viewport_size["height"],
                width=viewport_size["width"],
            ),
        )
    return image


def calc_frame_location_in_screenshot(driver, frame_chain, screenshot_type):
    window_scroll = eyes_selenium_utils.get_default_content_scroll_position(
        frame_chain, driver
    )
    logger.info("Getting first frame...")
    first_frame = frame_chain[0]
    location_in_screenshot = Point.from_(first_frame.location)

    # We only need to consider the scroll of the default content if the screenshot is a
    # viewport screenshot. If this is a full page screenshot, the frame location will
    # not change anyway.
    if screenshot_type == ScreenshotType.VIEWPORT:
        location_in_screenshot = location_in_screenshot.offset(
            Point(-window_scroll.x, 0)
        )

    # For inner frames we must calculate the scroll
    inner_frames = frame_chain[1:]
    for frame in inner_frames:
        location_in_screenshot = location_in_screenshot.offset(
            frame.location - frame.parent_scroll_position
        )
    return location_in_screenshot
