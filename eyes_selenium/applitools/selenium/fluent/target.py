from __future__ import absolute_import

import typing

from applitools.core.fluent import CheckTarget

from .selenium_check_settings import SeleniumCheckSettings

if typing.TYPE_CHECKING:
    from typing import Union

    FloatingType = Union[
        "FloatingRegion", "FloatingRegionByElement", "FloatingRegionBySelector"
    ]
    IgnoreType = Union["Region", "IgnoreRegionByElement", "IgnoreRegionBySelector"]

__all__ = ("Target",)


class Target(CheckTarget):
    """
    Target for an eyes.check_window/region.
    """

    @staticmethod
    def window():
        return SeleniumCheckSettings()

    @staticmethod
    def region(region, frame=None):
        return SeleniumCheckSettings(region=region, frame=frame)

    @staticmethod
    def frame(frame):
        return SeleniumCheckSettings(frame=frame)
