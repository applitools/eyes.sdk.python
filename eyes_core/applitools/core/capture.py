import typing
from abc import abstractmethod

import attr

from applitools.common import AppOutput, EyesScreenshot, Point, Region
from applitools.common.utils import ABC

if typing.TYPE_CHECKING:
    from typing import Optional
    from applitools.core import CheckSettings

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
    method = attr.ib()

    def get_app_output(self, region, last_screenshot, check_settings):
        # type: (Region, EyesScreenshot, T) -> AppOutputWithScreenshot
        return self.method(region, last_screenshot, check_settings)


class EyesScreenshotFactory(ABC):
    """
    Encapsulates the instantiation of an EyesScreenshot object.
    """

    @abstractmethod
    def make_screenshot(self, image):
        pass


class ImageProvider(ABC):
    """
    Encapsulates image retrieval.
    """

    def __init__(self, eyes):
        self._eyes = eyes

    @abstractmethod
    def get_image(self):
        pass
