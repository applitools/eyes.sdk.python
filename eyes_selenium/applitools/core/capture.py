import typing
from abc import abstractmethod

import attr

from applitools.common import AppOutput, EyesScreenshot, Point, Region
from applitools.common.utils import ABC

if typing.TYPE_CHECKING:
    from typing import Callable, Optional

    from PIL.Image import Image

    from applitools.core import CheckSettings, EyesBase

    T = typing.TypeVar("T", bound=CheckSettings)

__all__ = (
    "AppOutputWithScreenshot",
    "AppOutputProvider",
    "EyesScreenshotFactory",
    "ImageProvider",
)


@attr.s
class AppOutputWithScreenshot(object):
    app_output = attr.ib(type=AppOutput)  # type: AppOutput
    screenshot = attr.ib()  # type: Optional[EyesScreenshot]
    location = attr.ib(default=None)  # type: Optional[Point]


@attr.s
class AppOutputProvider(object):
    method = attr.ib()  # type: Callable

    def get_app_output(self, region, last_screenshot, check_settings):
        # type: (Region, EyesScreenshot, T) -> AppOutputWithScreenshot
        return self.method(region, last_screenshot, check_settings)


class EyesScreenshotFactory(ABC):
    """
    Encapsulates the instantiation of an EyesScreenshot object.
    """

    @abstractmethod
    def make_screenshot(self, image):
        # type: (Image) -> EyesScreenshot
        pass


@attr.s
class ImageProvider(ABC):
    """
    Encapsulates image retrieval.
    """

    _eyes = attr.ib()  # type: EyesBase

    @abstractmethod
    def get_image(self):
        # type: () -> Image
        pass
