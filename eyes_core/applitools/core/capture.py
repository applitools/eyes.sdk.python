import typing
from abc import abstractmethod

import attr

from applitools.common import AppOutput, EyesScreenshot, Region
from applitools.common.utils import ABC

if typing.TYPE_CHECKING:
    from applitools.core import EyesBase
    from applitools.core.fluent import CheckSettings

    T = typing.TypeVar("T", bound=CheckSettings)


@attr.s
class AppOutputWithScreenshot(object):
    app_output = attr.ib(type=AppOutput)  # type: AppOutput
    screenshot = attr.ib()  # type: EyesScreenshot


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
        # type: (EyesBase) -> None
        self._eyes = eyes

    @abstractmethod
    def get_image(self):
        pass
