import typing

import attr
from PIL import Image

from applitools.common.utils import image_utils
from applitools.core import CheckSettings, CheckSettingsValues, CheckTarget

if typing.TYPE_CHECKING:
    from typing import Optional, Text, Union
    from applitools.common import Region


@attr.s
class ImagesCheckSettingsValues(CheckSettingsValues):
    image = attr.ib(default=None)  # type: Optional[Image.Image]


@attr.s
class ImagesCheckSettings(CheckSettings):
    values = attr.ib(default=ImagesCheckSettingsValues())


class Target(CheckTarget):
    """
    Target for an eyes.check_window/region.
    """

    @staticmethod
    def image(image_or_path):
        # type: (Union[Image.Image, Text]) -> ImagesCheckSettings
        check_settings = ImagesCheckSettings()
        if isinstance(image_or_path, Image.Image):
            check_settings.values.image = image_or_path
            return check_settings
        elif isinstance(image_or_path, str) or isinstance(image_or_path, Text):
            check_settings.values.image = image_utils.image_from_file(image_or_path)
            return check_settings
        raise TypeError(
            "Unsupported image type. Should be `PIL.Image` or path to " "image"
        )

    @staticmethod
    def region(image_or_path, rect):  # type: ignore
        # type: (Union[Image.Image, Text], Region) -> ImagesCheckSettings
        check_settings = Target.image(image_or_path)
        check_settings.update_target_region(rect)
        return check_settings
