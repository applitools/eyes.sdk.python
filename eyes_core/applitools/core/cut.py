import math
from abc import abstractmethod
from typing import Dict, Union

import attr
from PIL.Image import Image

from applitools.common import RectangleSize, Region
from applitools.common.utils import ABC, image_utils

__all__ = ("FixedCutProvider", "UnscaledFixedCutProvider", "NullCutProvider")


@attr.s
class CutProvider(ABC):
    header = attr.ib()  # type: int
    footer = attr.ib()  # type: int
    left = attr.ib()  # type: int
    right = attr.ib()  # type: int

    def cut(self, image):
        # type: (Image) -> Image
        if self.header == 0 and self.footer == 0 and self.right == 0 and self.left == 0:
            return image

        target_region = Region(
            self.left,
            self.header,
            image.width - self.left - self.right,
            image.height - self.header - self.footer,
        )
        return image_utils.crop_image(image, target_region)

    @abstractmethod
    def scale(self, scale_ratio):
        # type: (float) -> CutProvider
        """Get a scaled version of the cut provider"""

    def to_region(self, size):
        # type: (Union[RectangleSize, Dict]) -> Region
        return Region(
            left=self.left,
            top=self.header,
            width=size["width"] - self.left - self.right,
            height=size["height"] - self.header - self.footer,
        )


class FixedCutProvider(CutProvider):
    def scale(self, scale_ratio):
        # type: (float) -> FixedCutProvider
        cut_provider = FixedCutProvider(
            math.ceil(self.header * scale_ratio),
            math.ceil(self.footer * scale_ratio),
            math.ceil(self.left * scale_ratio),
            math.ceil(self.right * scale_ratio),
        )
        return cut_provider


class UnscaledFixedCutProvider(CutProvider):
    def scale(self, scale_ratio):
        # type: (float) -> UnscaledFixedCutProvider
        if isinstance(self, NullCutProvider):
            return self

        cut_provider = UnscaledFixedCutProvider(
            self.header, self.footer, self.left, self.right
        )
        return cut_provider


class NullCutProvider(UnscaledFixedCutProvider):
    def __init__(self):
        super(NullCutProvider, self).__init__(0, 0, 0, 0)
