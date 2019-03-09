from __future__ import absolute_import

import typing as tp

from PIL import Image

from applitools.common.geometry import Region
from applitools.common.utils import image_utils
from applitools.core.fluent import CheckTarget

from .images_check_settings import ImagesCheckSettings

__all__ = ("Target",)


class Target(CheckTarget):
    """
    Target for an eyes.check_window/region.
    """

    @staticmethod
    def image(image_or_path):
        # type: (tp.Union[Image.Image, tp.Text]) -> ImagesCheckSettings
        if isinstance(image_or_path, Image.Image):
            return ImagesCheckSettings(image_or_path)
        elif isinstance(image_or_path, str) or isinstance(image_or_path, tp.Text):
            return ImagesCheckSettings(image_utils.image_from_file(image_or_path))
        raise TypeError(
            "Unsupported image type. Should be `PIL.Image` or path to " "image"
        )

    @staticmethod
    def region(image_or_path, rect):
        # type: (tp.Union[Image.Image, tp.Text], Region) -> ImagesCheckSettings
        check_settings = Target.image(image_or_path)
        check_settings.region(rect)
        return check_settings
