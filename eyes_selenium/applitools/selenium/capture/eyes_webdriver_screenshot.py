from __future__ import absolute_import

import typing
from enum import Enum

import attr
from selenium.common.exceptions import WebDriverException

from applitools.common import (
    CoordinatesType,
    CoordinatesTypeConversionError,
    EyesError,
    OutOfBoundsError,
    Point,
    RectangleSize,
    Region,
    logger,
)
from applitools.common.utils import argument_guard, image_utils
from applitools.core.capture import EyesScreenshot, EyesScreenshotFactory
from applitools.selenium.positioning import ScrollPositionProvider

if typing.TYPE_CHECKING:
    from typing import Optional
    from PIL import Image
    from applitools.selenium.webdriver import EyesWebDriver


class ScreenshotType(Enum):
    VIEWPORT = "VIEWPORT"
    ENTIRE_FRAME = "ENTIRE_FRAME"


class EyesWebDriverScreenshot(EyesScreenshot):
    @classmethod
    def create_viewport(cls, driver, image):
        # type: (EyesWebDriver, Image.Image) -> EyesWebDriverScreenshot
        instance = cls(driver, image, ScreenshotType.VIEWPORT, Point.zero())
        instance._validate_frame_window()
        return instance

    @classmethod
    def create_full_page(cls, driver, image, frame_location_in_screenshot):
        # type: (EyesWebDriver, Image.Image, Point) -> EyesWebDriverScreenshot
        return cls(driver, image, None, frame_location_in_screenshot)

    @classmethod
    def create_entire_frame(cls, driver, image, entire_frame_size):
        # type: (EyesWebDriver, Image.Image, RectangleSize) -> EyesWebDriverScreenshot
        instance = cls(driver, image, ScreenshotType.ENTIRE_FRAME, Point.zero())
        instance._current_frame_scroll_position = Point(0, 0)  # type: ignore
        instance._frame_location_in_screenshot = Point(0, 0)  # type: ignore
        instance.frame_window = Region.from_location_size(  # type: ignore
            Point(0, 0), entire_frame_size
        )
        return instance

    @classmethod
    def from_screenshot(cls, driver, image, screenshot_region):
        # type: (EyesWebDriver, Image.Image, Region) -> EyesWebDriverScreenshot
        instance = cls(driver, image, ScreenshotType.ENTIRE_FRAME, Point.zero())
        # The frame comprises the entire screenshot.
        instance._screenshot_type = ScreenshotType.ENTIRE_FRAME
        instance.frame_window = Region.from_location_size(  # type: ignore
            Point.zero(), screenshot_region.size
        )
        instance.region_window = Region.from_region(screenshot_region)  # type: ignore
        return instance

    def __init__(self, driver, image, screenshot_type, frame_location_in_screenshot):
        # type: (EyesWebDriver, Image.Image, Optional[ScreenshotType], Optional[Point]) -> None
        """
        Initializes a Screenshot instance. Either screenshot or screenshot64 must NOT be None.
        Should not be used directly. Use create_from_image/create_from_base64 instead.

        :param driver: EyesWebDriver instance which handles the session from
         which the screenshot was retrieved.
        :param image: image instance. If screenshot64 is None,
         this variable must NOT be none.
        :param screenshot_type: possible VIEWPORT OR ENTIRE_FRAME
        :param frame_location_in_screenshot: The location of the frame relative
         to the top,left of the screenshot.
        :raise EyesError: If the screenshots are None.
        """
        # initializing of screenshot
        super(EyesWebDriverScreenshot, self).__init__(image=image)
        # For future adaptation
        # TODO: Refactor initialization!
        self._driver = driver

        self._screenshot_type = self.update_screenshot_type(screenshot_type, image)
        cur_frame_position_provider = driver.eyes.current_frame_position_provider
        if cur_frame_position_provider:
            position_provider = cur_frame_position_provider
        else:
            position_provider = driver.eyes.position_provider

        self._frame_chain = driver.frame_chain.clone()
        # breakpoint()
        frame_size = self.get_frame_size(position_provider)
        self._current_frame_scroll_position = self.get_updated_scroll_position(
            position_provider
        )
        self._frame_location_in_screenshot = self.get_updated_frame_location_in_screenshot(
            frame_location_in_screenshot
        )
        logger.debug("Calculating frame window...")
        self.frame_window = Region.from_location_size(
            self._frame_location_in_screenshot, frame_size
        )
        self.frame_window.intersect(
            Region(0, 0, width=image.width, height=image.height)
        )
        self.region_window = Region(0, 0, 0, 0)

        # self._validate_frame_window()

    def _validate_frame_window(self):
        if self.frame_window.width <= 0 or self.frame_window.height <= 0:
            raise EyesError("Got empty frame window for screenshot!")

    def get_updated_frame_location_in_screenshot(self, frame_location_in_screenshot):
        if self.frame_chain.size > 0:
            frame_location_in_screenshot = self.calc_frame_location_in_screenshot(
                self._driver, self._frame_chain, self._screenshot_type
            )
        elif not frame_location_in_screenshot:
            frame_location_in_screenshot = Point.zero()
        return frame_location_in_screenshot

    def get_updated_scroll_position(self, position_provider):
        try:
            sp = position_provider.get_current_position()
            if not sp:
                sp = Point.zero()
        except WebDriverException:
            sp = Point.zero()

        return sp

    def update_screenshot_type(self, screenshot_type, image):
        if screenshot_type is None:
            viewport_size = self._driver.eyes.viewport_size
            scale_viewport = self._driver.eyes._stitch_content

            if scale_viewport:
                pixel_ratio = self._driver.eyes._device_pixel_ratio
                viewport_size = viewport_size.scale(pixel_ratio)
            if (
                image.width <= viewport_size["width"]
                and image <= viewport_size["height"]
            ):
                screenshot_type = ScreenshotType.VIEWPORT
            else:
                screenshot_type = ScreenshotType.ENTIRE_FRAME
        return screenshot_type

    @property
    def image(self):
        return self._image

    def get_frame_size(self, position_provider):
        if self._frame_chain:
            frame_size = self._frame_chain.peek.outer_size
        else:
            # get entire page size might throw an exception for applications
            # which don't support Javascript (e.g., Appium). In that case
            # we'll use the viewport size as the frame's size.
            try:
                frame_size = position_provider.get_entire_size()
            except WebDriverException:
                # For Appium, we can't get the "entire page size",
                # so we use the viewport size.
                frame_size = self._driver.get_default_content_viewport_size()
        return frame_size

    @staticmethod
    def _get_default_content_scroll_position(driver):
        # type: (EyesWebDriver) -> Point
        scroll_root_element = driver.eyes.get_current_frame_scroll_root_element()
        return ScrollPositionProvider.get_current_position_static(
            driver, scroll_root_element
        )

    @staticmethod
    def get_default_content_scroll_position(current_frames, driver):
        if current_frames.size == 0:
            scroll_position = EyesWebDriverScreenshot._get_default_content_scroll_position(
                driver
            )
        else:
            current_fc = driver.eyes._original_frame_chain
            with driver.switch_to.frames_and_back(current_fc):
                scroll_position = EyesWebDriverScreenshot._get_default_content_scroll_position(
                    driver
                )
        return scroll_position

    @staticmethod
    def calc_frame_location_in_screenshot(driver, frame_chain, screenshot_type):
        window_scroll = EyesWebDriverScreenshot.get_default_content_scroll_position(
            frame_chain, driver
        )
        logger.info("Getting first frame...")
        first_frame = frame_chain[0]
        location_in_screenshot = Point(first_frame.location.x, first_frame.location.y)
        # We only need to consider the scroll of the default content if the screenshot is a
        # viewport screenshot. If this is a full page screenshot, the frame location will not
        # change anyway.
        if screenshot_type == ScreenshotType.VIEWPORT:
            location_in_screenshot = location_in_screenshot.offset(
                -window_scroll.x, -window_scroll.y
            )

        # For inner frames we must calculate the scroll
        inner_frames = frame_chain[1:]
        for frame in inner_frames:
            location_in_screenshot = location_in_screenshot.offset(
                frame.location.x - frame.parent_scroll_position.x,
                frame.location.y - frame.parent_scroll_position.y,
            )
        return location_in_screenshot

    @property
    def frame_chain(self):
        return self._frame_chain

    def location_in_screenshot(self, location, coordinates_type):
        location = self.convert_location(
            location, coordinates_type, self.SCREENSHOT_AS_IS
        )
        # Making sure it's within the screenshot bounds
        if not self.frame_window.contains(location):
            raise OutOfBoundsError(
                "Location %s ('%s') is not visible in screenshot!"
                % (location, coordinates_type)
            )
        return location

    def sub_screenshot(self, region, throw_if_clipped=False):
        # We calculate intersection based on as-is coordinates.
        as_is_sub_screenshot_region = self.intersected_region(
            region, self.SCREENSHOT_AS_IS
        )
        if as_is_sub_screenshot_region.is_size_empty or (
            throw_if_clipped and not as_is_sub_screenshot_region.size == region.size
        ):
            raise OutOfBoundsError(
                "Region [%s] is out of screenshot bounds [%s]"
                % (region, self.frame_window)
            )
        sub_image = image_utils.get_image_part(self.image, as_is_sub_screenshot_region)
        result = EyesWebDriverScreenshot.from_screenshot(
            self._driver,
            sub_image,
            Region(region.left, region.top, sub_image.width, sub_image.height),
        )
        return result

    CONTEXT_RELATIVE = CoordinatesType.CONTEXT_RELATIVE
    SCREENSHOT_AS_IS = CoordinatesType.SCREENSHOT_AS_IS
    CONTEXT_AS_IS = CoordinatesType.CONTEXT_AS_IS

    def convert_location(self, location, from_, to):  # noqa: C901
        # type: (Point, CoordinatesType, CoordinatesType) -> Point
        argument_guard.not_none(location)
        argument_guard.not_none(from_)
        argument_guard.not_none(to)

        result = Point.from_location(location)
        if from_ == to:
            return result

        # If we're not inside a frame, and the screenshot is the entire
        # page, then the context as-is/relative are the same (notice
        # screenshot as-is might be different, e.g.,
        # if it is actually a sub-screenshot of a region).
        if (
            len(self.frame_chain) == 0
            and self._screenshot_type == ScreenshotType.ENTIRE_FRAME
        ):
            if (
                from_ == self.CONTEXT_RELATIVE or from_ == self.CONTEXT_AS_IS
            ) and to == self.SCREENSHOT_AS_IS:
                # If this is not a sub-screenshot, this will have no effect.
                result = result.offset(
                    self._frame_location_in_screenshot.x,
                    self._frame_location_in_screenshot.y,
                )
                # If this is not a region subscreenshot, this will have no effect.
                result = result.offset(
                    -self.region_window.left, -self.region_window.top
                )
            elif from_ == self.SCREENSHOT_AS_IS and (
                to == self.CONTEXT_RELATIVE or to == self.CONTEXT_AS_IS
            ):
                result = result.offset(
                    -self._frame_location_in_screenshot.x,
                    -self._frame_location_in_screenshot.y,
                )
            return result

        if from_ == self.CONTEXT_AS_IS:
            if to == self.CONTEXT_RELATIVE:
                result = result.offset(
                    self._current_frame_scroll_position.x,
                    self._current_frame_scroll_position.y,
                )
            elif to == self.SCREENSHOT_AS_IS:
                result = result.offset(
                    self._frame_location_in_screenshot.x,
                    self._frame_location_in_screenshot.y,
                )
            else:
                raise CoordinatesTypeConversionError(from_, to)
        elif from_ == self.CONTEXT_RELATIVE:
            if to == self.SCREENSHOT_AS_IS:
                # First, convert context-relative to context-as-is.
                result = result.offset(
                    -self._current_frame_scroll_position.x,
                    -self._current_frame_scroll_position.y,
                )
                # Now convert context-as-is to screenshot-as-is
                result = result.offset(
                    self._frame_location_in_screenshot.x,
                    self._frame_location_in_screenshot.y,
                )
            elif to == self.CONTEXT_AS_IS:
                result = result.offset(
                    -self._current_frame_scroll_position.x,
                    -self._current_frame_scroll_position.y,
                )
            else:
                raise CoordinatesTypeConversionError(from_, to)
        elif from_ == self.SCREENSHOT_AS_IS:
            if to == self.CONTEXT_RELATIVE:
                # First, convert context-relative to context-as-is.
                result = result.offset(
                    -self._frame_location_in_screenshot.x,
                    -self._frame_location_in_screenshot.y,
                )
                # Now convert context-as-is to screenshot-as-is
                result = result.offset(
                    self._current_frame_scroll_position.x,
                    self._current_frame_scroll_position.y,
                )
            elif to == self.CONTEXT_AS_IS:
                result = result.offset(
                    -self._frame_location_in_screenshot.x,
                    -self._frame_location_in_screenshot.y,
                )
            else:
                raise CoordinatesTypeConversionError(from_, to)
        else:
            raise CoordinatesTypeConversionError(from_, to)
        return result

    def intersected_region(self, region, coordinates_type):
        # type: (Region, CoordinatesType) -> Region
        argument_guard.not_none(region)
        argument_guard.not_none(coordinates_type)

        if region.is_size_empty:
            return Region.from_region(region)

        original_coordinates_type = region.coordinates_type

        intersected_region = self.convert_region_location(
            region, original_coordinates_type, self.SCREENSHOT_AS_IS
        )
        #  If the request was context based, we intersect with the frame window.
        if (
            original_coordinates_type == self.CONTEXT_AS_IS
            or original_coordinates_type == self.CONTEXT_RELATIVE
        ):
            intersected_region.intersect(self.frame_window)
        # If the request is screenshot based, we intersect with the image
        elif original_coordinates_type == self.SCREENSHOT_AS_IS:
            intersected_region.intersect(
                Region(0, 0, self.image.width, self.image.height)
            )
        else:
            raise ValueError(
                "Unknown coordinates type: '%s'" % original_coordinates_type
            )
        #  If the intersection is empty we don't want to convert the coordinates.
        if intersected_region.is_size_empty:
            return intersected_region

        #  Converting the result to the required coordinates type
        intersected_region = self.convert_region_location(
            intersected_region, self.SCREENSHOT_AS_IS, coordinates_type
        )
        return intersected_region


@attr.s
class EyesWebDriverScreenshotFactory(EyesScreenshotFactory):
    """
    Encapsulates the instantiation of an `EyesWebDriverScreenshot`
    """

    _driver = attr.ib()

    def make_screenshot(self, image):
        return EyesWebDriverScreenshot.create_viewport(self._driver, image)
