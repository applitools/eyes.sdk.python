from __future__ import absolute_import

from typing import TYPE_CHECKING, overload

from .selenium_check_settings import SeleniumCheckSettings

if TYPE_CHECKING:
    from applitools.common import Region
    from applitools.common.utils.custom_types import (
        AnyWebElement,
        BySelector,
        CssSelector,
        FrameIndex,
        FrameNameOrId,
    )

    from .target_path import RegionLocator

__all__ = ("Target",)


class Target(object):
    """
    Target for an eyes.check_window/region.
    """

    @staticmethod
    def window():
        # type: () -> SeleniumCheckSettings
        return SeleniumCheckSettings()

    @staticmethod  # noqa
    @overload
    def region(region):
        # type: (Region) -> SeleniumCheckSettings
        pass

    @staticmethod  # noqa
    @overload
    def region(css_selector):
        # type: (CssSelector) -> SeleniumCheckSettings
        pass

    @staticmethod  # noqa
    @overload
    def region(element):
        # type: (AnyWebElement) -> SeleniumCheckSettings
        pass

    @staticmethod  # noqa
    @overload
    def region(by_selector):
        # type: (BySelector) -> SeleniumCheckSettings
        pass

    @staticmethod  # noqa
    @overload
    def region(target_path):
        # type: (RegionLocator) -> SeleniumCheckSettings
        pass

    @staticmethod  # noqa
    def region(region):
        return SeleniumCheckSettings().region(region)

    @staticmethod  # noqa
    @overload
    def frame(frame_name_or_id):
        # type: (FrameNameOrId) -> SeleniumCheckSettings
        pass

    @staticmethod  # noqa
    @overload
    def frame(frame_element):
        # type: (AnyWebElement) -> SeleniumCheckSettings
        pass

    @staticmethod  # noqa
    @overload
    def frame(frame_index):
        # type: (FrameIndex) -> SeleniumCheckSettings
        pass

    @staticmethod  # noqa
    @overload
    def frame(frame_by_selector):
        # type: (BySelector) -> SeleniumCheckSettings
        pass

    @staticmethod  # noqa
    @overload
    def frame(target_path):
        # type: (RegionLocator) -> SeleniumCheckSettings
        pass

    @staticmethod  # noqa
    def frame(frame):
        return SeleniumCheckSettings().frame(frame)
