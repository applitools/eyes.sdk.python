from __future__ import absolute_import

from applitools.common import logger
from applitools.core.fluent import CheckTarget

from .selenium_check_settings import SeleniumCheckSettings

__all__ = ("Target",)


class Target(CheckTarget):
    """
    Target for an eyes.check_window/region.
    """

    @staticmethod
    def window():
        # type: () -> SeleniumCheckSettings
        return SeleniumCheckSettings()

    @staticmethod
    def region(region, frame=None):
        return SeleniumCheckSettings(region=region, frame=frame)

    @staticmethod
    def frame(frame):
        return SeleniumCheckSettings(frame=frame)
