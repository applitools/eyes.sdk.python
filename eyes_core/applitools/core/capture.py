from __future__ import absolute_import

import abc
import typing as tp

from PIL import Image

from applitools.core.utils import ABC, argument_guard
from applitools.core.utils import image_utils

if tp.TYPE_CHECKING:
    from applitools.core.utils.custom_types import AnyWebElement, Num
    from ..selenium.webdriver import EyesFrame
    from ..selenium.webelement import EyesWebElement
    from .geometry import Point, Region

    T = tp.TypeVar('T', bound='EyesScreenshot')

__all__ = ('EyesScreenshot',)


class EyesScreenshot(ABC):
    """
    Base class for handling screenshots.
    """

    def __init__(self, image):
        # type: (Image.Image) -> None
        argument_guard.is_a(image, Image.Image)
        self._screenshot = image

    @staticmethod
    @abc.abstractmethod
    def calc_frame_location_in_screenshot(frame_chain, is_viewport_screenshot):
        # type: (tp.List[EyesFrame], tp.Optional[bool]) -> Point
        """
        :param frame_chain: List of the frames.
        :param is_viewport_screenshot: Whether the viewport is a screenshot or not.
        :return: The frame location as it would be on the screenshot. Notice that this value
            might actually be OUTSIDE the screenshot (e.g, if this is a viewport screenshot and
            the frame is located outside the viewport). This is not an error. The value can also
            be negative.
        """

    @abc.abstractmethod
    def get_base64(self):
        # type: () -> tp.Text
        """
        Returns a base64 screenshot.

        :return: The base64 representation of the png.
        """

    @abc.abstractmethod
    def get_intersected_region(self, region):
        # type: (Region) -> Region
        """
        Gets the intersection of the region with the screenshot image.

        :param region: The region in the frame.
        :return: The part of the region which intersects with
            the screenshot image.
        """

    @abc.abstractmethod
    def get_location_relative_to_frame_viewport(self, location):
        # type: (tp.Dict[tp.Text, Num]) -> tp.Dict[tp.Text, Num]
        """
        Gets the relative location from a given location to the viewport.

        :param location: A dict with 'x' and 'y' keys representing the location we want
            to adjust.
        :return: A location (keys are 'x' and 'y') adjusted to the current frame/viewport.
        """

    @abc.abstractmethod
    def get_element_region_in_frame_viewport(self, element):
        # type: (AnyWebElement) -> Region
        """
        Gets The element region in the frame.

        :param element: The element to get the region in the frame.
        :return: The element's region in the frame with scroll considered if necessary
        """

    @abc.abstractmethod
    def get_viewport_screenshot(self):
        # type: () -> T
        """
        Always return viewport size screenshot
        """

    @abc.abstractmethod
    def get_sub_screenshot_by_region(self, region):
        # type: (Region) -> T
        """
        Gets the region part of the screenshot image.

        :param region: The region in the frame.
        :return: A screenshot object representing the given region part of the image.
        """

    @abc.abstractmethod
    def get_frame_chain(self):
        # type: () -> tp.List[EyesFrame]
        """
        Returns a copy of the fram chain.

        :return: A copy of the frame chain, as received by the driver when the screenshot was
            created.
        """

    def get_bytes(self):
        # type: () -> bytes
        """
        Returns the bytes of the screenshot.

        :return: The bytes representation of the png.
        """
        return image_utils.get_bytes(self._screenshot)

    def get_intersected_region_by_element(self, element):
        # type: (EyesWebElement) -> Region
        """
        Gets the intersection of the element's region with the screenshot image.

        :param element: The element in the frame.
        :return: The part of the element's region which intersects with
            the screenshot image.
        """
        element_region = self.get_element_region_in_frame_viewport(element)
        return self.get_intersected_region(element_region)

    def get_sub_screenshot_by_element(self, element):
        # type: (EyesWebElement) -> T
        """
        Gets the element's region part of the screenshot image.

        :param element: The element in the frame.
        :return: A screenshot object representing the element's region part of the
            image.
        """
        element_region = self.get_element_region_in_frame_viewport(element)
        return self.get_sub_screenshot_by_region(element_region)
