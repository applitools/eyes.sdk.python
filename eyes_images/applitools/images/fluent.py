from typing import TYPE_CHECKING, Optional, Text, Union, overload

import attr
from PIL import Image

from applitools.common.utils import image_utils
from applitools.core import CheckSettings, CheckSettingsValues, CheckTarget

if TYPE_CHECKING:
    from applitools.common import Region


@attr.s
class ImagesCheckSettingsValues(CheckSettingsValues):
    image = attr.ib(default=None)  # type: Optional[Image.Image]


@attr.s
class ImagesCheckSettings(CheckSettings):
    values = attr.ib(
        factory=ImagesCheckSettingsValues
    )  # type: ImagesCheckSettingsValues


class Target(object):
    """
    Target for an eyes.check_window/region.
    """

    @staticmethod  # noqa
    @overload
    def image(image):
        # type: (Image.Image) -> ImagesCheckSettings
        pass

    @staticmethod  # noqa
    @overload
    def image(path):
        # type: (Text) -> ImagesCheckSettings
        pass

    @staticmethod  # noqa
    def image(image_or_path):
        check_settings = ImagesCheckSettings()
        check_settings.values.image = image_utils.image_from_path(image_or_path)
        return check_settings

    @staticmethod  # noqa
    @overload
    def region(image, rect):
        # type: (Image.Image, Region) -> ImagesCheckSettings
        pass

    @staticmethod  # noqa
    @overload
    def region(path, rect):
        # type: (Text, Region) -> ImagesCheckSettings
        pass

    @staticmethod  # noqa
    def region(image_or_path, rect):
        # image_or_path, rect = args
        check_settings = Target.image(image_or_path)
        check_settings.values.target_region = rect
        return check_settings
