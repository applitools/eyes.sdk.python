from __future__ import absolute_import

from applitools.common import logger
from applitools.core.fluent import CheckTarget

from .selenium_check_settings import SeleniumCheckSettings

__all__ = ("Target",)


class BackwardTarget(object):
    """
    Use for emulate behavior of old Target class
    """

    @staticmethod
    def ignore(*regions):
        logger.deprecation(
            "Use new interface e.g. Target.window(), Target.region(), Target.frame()"
        )
        return Target.window().ignore_regions(*regions)

    @staticmethod
    def floating(*regions):
        logger.deprecation(
            "Use new interface e.g. Target.window(), Target.region(), Target.frame()"
        )
        return Target.window().floating_region(*regions)


class Target(BackwardTarget, CheckTarget):
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
