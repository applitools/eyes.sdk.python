from __future__ import absolute_import

import typing

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
from applitools.selenium import eyes_selenium_utils
from applitools.selenium.capture.screenshot_utils import (
    ScreenshotType,
    calc_frame_location_in_screenshot,
    update_screenshot_type,
)
from applitools.selenium.frames import FrameChain

if typing.TYPE_CHECKING:
    from typing import Optional, Union

    from PIL import Image

    from applitools.selenium.positioning import SeleniumPositionProvider
    from applitools.selenium.webdriver import EyesWebDriver


@attr.s(hash=False)
class EyesWebDriverScreenshot(EyesScreenshot):

    _driver = attr.ib()  # type: EyesWebDriver
    _image = attr.ib()  # type: Image.Image
    _screenshot_type = attr.ib()  # type: ScreenshotType
    # The top/left coordinates of the frame window(!) relative to the top/left
    # of the screenshot. Used for calculations, so can also be outside(!)
    # the screenshot.
    _frame_location_in_screenshot = attr.ib()  # type: Point
    _current_frame_scroll_position = attr.ib(default=None)  # type: Optional[Point]
    frame_window = attr.ib(default=None)  # type: Region
    _frame_chain = attr.ib(init=False)  # type: FrameChain

    @classmethod
    def create_viewport(cls, driver, image):
        # type: (EyesWebDriver, Image.Image) -> EyesWebDriverScreenshot
        instance = cls(driver, image, ScreenshotType.VIEWPORT, None)
        instance._validate_frame_window()
        return instance

    @classmethod
    def create_full_page(cls, driver, image, frame_location_in_screenshot):
        # type: (EyesWebDriver, Image.Image, Point) -> EyesWebDriverScreenshot
        return cls(driver, image, None, frame_location_in_screenshot)

    @classmethod
    def create_entire_element(
        cls,
        driver,  # type: EyesWebDriver
        image,  # type: Image.Image
        entire_element_size,  # type: RectangleSize
        frame_location_in_screenshot,  # type: Point
    ):
        # type: (...) -> EyesWebDriverScreenshot
        return cls(
            driver,
            image,
            ScreenshotType.ENTIRE_FRAME,
            frame_location_in_screenshot,
            current_frame_scroll_position=Point(0, 0),
            frame_window=Region.from_(Point(0, 0), entire_element_size),
        )

    @classmethod
    def from_screenshot(
        cls, driver, image, screenshot_region, frame_location_in_parent_screenshot
    ):
        # type: (EyesWebDriver, Image.Image, Region, Point) -> EyesWebDriverScreenshot
        return cls(
            driver,
            image,
            ScreenshotType.ENTIRE_FRAME,
            frame_location_in_parent_screenshot - screenshot_region.location,
            frame_window=Region.from_(Point.ZERO(), screenshot_region.size),
        )

    def __attrs_post_init__(self):
        # type: () -> None
        self._screenshot_type = update_screenshot_type(
            self._screenshot_type, self._image, self._driver
        )
        position_provider = self._driver.eyes.current_frame_position_provider

        if not self._driver.is_mobile_app:
            self._frame_chain = self._driver.frame_chain.clone()
            frame_size = self.get_frame_size(position_provider)
            self._current_frame_scroll_position = (
                eyes_selenium_utils.get_updated_scroll_position(  # noqa
                    position_provider
                )
            )
            self.updated_frame_location_in_screenshot(
                self._frame_location_in_screenshot
            )
            logger.debug("Calculating frame window...")
            self.frame_window = Region.from_(
                self._frame_location_in_screenshot, frame_size
            )
        else:
            self._frame_chain = FrameChain()
            self._current_frame_scroll_position = Point.ZERO()
            self._frame_location_in_screenshot = Point.ZERO()
            self.frame_window = Region.from_(
                self._frame_location_in_screenshot, self.image
            )
        self.frame_window = self.frame_window.intersect(Region.from_(self.image))

    def _validate_frame_window(self):
        # type: () -> None
        if self.frame_window.width <= 0 or self.frame_window.height <= 0:
            raise EyesError("Got empty frame window for screenshot!")

    def updated_frame_location_in_screenshot(self, location):
        # type: (Point) -> None
        if location is None:
            if self.frame_chain.size > 0:
                self._frame_location_in_screenshot = calc_frame_location_in_screenshot(
                    self._driver, self._frame_chain, self._screenshot_type
                )
            else:
                self._frame_location_in_screenshot = Point.ZERO()
        else:
            self._frame_location_in_screenshot = location

    @property
    def image(self):
        # type: () -> Union[Image, Image]
        return self._image

    def get_frame_size(self, position_provider):
        # type: (SeleniumPositionProvider) -> RectangleSize
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

    @property
    def frame_chain(self):
        # type: () -> FrameChain
        return self._frame_chain

    def location_in_screenshot(self, location, coordinates_type):
        # type: (Point, CoordinatesType) -> Point
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
        # type: (Region, bool) -> EyesWebDriverScreenshot
        # We calculate intersection based on as-is coordinates.
        as_is_sub_screenshot_region = self.intersected_region(
            region, self.SCREENSHOT_AS_IS
        )
        if (
            as_is_sub_screenshot_region.is_size_empty
            or throw_if_clipped
            and as_is_sub_screenshot_region.size != region.size
        ):
            raise OutOfBoundsError(
                "Region [%s] is out of screenshot bounds [%s]"
                % (region, self.frame_window)
            )
        sub_image = image_utils.get_image_part(self.image, as_is_sub_screenshot_region)
        return EyesWebDriverScreenshot.from_screenshot(
            self._driver,
            sub_image,
            Region(region.left, region.top, sub_image.width, sub_image.height),
            self._frame_location_in_screenshot,
        )

    CONTEXT_RELATIVE = CoordinatesType.CONTEXT_RELATIVE
    SCREENSHOT_AS_IS = CoordinatesType.SCREENSHOT_AS_IS
    CONTEXT_AS_IS = CoordinatesType.CONTEXT_AS_IS

    def convert_location(self, location, from_, to):  # noqa: C901
        # type: (Point, CoordinatesType, CoordinatesType) -> Point
        argument_guard.not_none(location)
        argument_guard.not_none(from_)
        argument_guard.not_none(to)

        result = Point.from_(location)
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
                from_ in [self.CONTEXT_RELATIVE, self.CONTEXT_AS_IS]
                and to == self.SCREENSHOT_AS_IS
            ):
                # If this is not a sub-screenshot, this will have no effect.
                result = result.offset(self._frame_location_in_screenshot)
            elif from_ == self.SCREENSHOT_AS_IS and to in [
                self.CONTEXT_RELATIVE,
                self.CONTEXT_AS_IS,
            ]:
                result = result.offset(-self._frame_location_in_screenshot)
            return result

        if from_ == self.CONTEXT_AS_IS:
            if to == self.CONTEXT_RELATIVE:
                result = result.offset(self._current_frame_scroll_position)
            elif to == self.SCREENSHOT_AS_IS:
                result = result.offset(self._frame_location_in_screenshot)
            else:
                raise CoordinatesTypeConversionError(from_, to)
        elif from_ == self.CONTEXT_RELATIVE:
            if to == self.SCREENSHOT_AS_IS:
                # First, convert context-relative to context-as-is.
                result = result.offset(-self._current_frame_scroll_position)
                # Now convert context-as-is to screenshot-as-is
                result = result.offset(self._frame_location_in_screenshot)
            elif to == self.CONTEXT_AS_IS:
                result = result.offset(-self._current_frame_scroll_position)
            else:
                raise CoordinatesTypeConversionError(from_, to)
        elif from_ == self.SCREENSHOT_AS_IS:
            if to == self.CONTEXT_RELATIVE:
                # First, convert context-relative to context-as-is.
                result = result.offset(-self._frame_location_in_screenshot)
                # Now convert context-as-is to screenshot-as-is
                result = result.offset(self._current_frame_scroll_position)
            elif to == self.CONTEXT_AS_IS:
                result = result.offset(-self._frame_location_in_screenshot)
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
            return Region.from_(region)

        original_coordinates_type = region.coordinates_type

        intersected_region = self.convert_region_location(
            region, original_coordinates_type, self.SCREENSHOT_AS_IS
        )
        #  If the request was context based, we intersect with the frame window.
        if original_coordinates_type in [self.CONTEXT_AS_IS, self.CONTEXT_RELATIVE]:
            intersected_region = intersected_region.intersect(self.frame_window)
        # If the request is screenshot based, we intersect with the image
        elif original_coordinates_type == self.SCREENSHOT_AS_IS:
            intersected_region = intersected_region.intersect(
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
        # type: (Image) -> EyesWebDriverScreenshot
        return EyesWebDriverScreenshot.create_viewport(self._driver, image)
