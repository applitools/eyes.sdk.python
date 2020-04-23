import warnings
from enum import Enum, EnumMeta
import enum

from applitools.common.utils.compat import with_metaclass, DynamicClassAttributeGetter


class _EDGEDeprecationMeta(EnumMeta):
    class Dict(dict):
        def __getitem__(self, item):
            if item == "EDGE":
                warnings.warn(
                    "The `EDGE` option that is being used in your browsers configuration"
                    " will soon be deprecated. Please change it to either `EDGE_LEGACY`"
                    " for the legacy version or to `EDGE_CHROMIUM` for the"
                    " new Chromium-based version.",
                    DeprecationWarning,
                    stacklevel=3,
                )
                return BrowserType.EDGE_LEGACY
            return super(_EDGEDeprecationMeta.Dict, self).__getitem__(item)

    def __new__(metacls, cls, bases, classdict):
        enum_class = enum.EnumMeta.__new__(metacls, cls, bases, classdict)
        enum_class._member_map_ = _EDGEDeprecationMeta.Dict(**enum_class._member_map_)
        return enum_class


class BrowserType(with_metaclass(_EDGEDeprecationMeta, Enum)):
    CHROME = "chrome-0"
    CHROME_ONE_VERSION_BACK = "chrome-1"
    CHROME_TWO_VERSIONS_BACK = "chrome-2"
    FIREFOX = "firefox-0"
    FIREFOX_ONE_VERSION_BACK = "firefox-1"
    FIREFOX_TWO_VERSIONS_BACK = "firefox-2"
    SAFARI = "safari-0"
    SAFARI_ONE_VERSION_BACK = "safari-1"
    SAFARI_TWO_VERSIONS_BACK = "safari-2"
    IE_10 = "ie10"
    IE_11 = "ie"
    EDGE_LEGACY = "edgelegacy"
    EDGE_CHROMIUM = "edgechromium"
    EDGE_CHROMIUM_ONE_VERSION_BACK = "edgechromium-1"
    EDGE_CHROMIUM_TWO_VERSIONS_BACK = "edgechromium-2"

    @DynamicClassAttributeGetter
    def EDGE(self):
        # display msg in IDE, cannot be hidden to separate variable
        warnings.warn(
            "The `EDGE` option that is being used in your browsers configuration"
            " will soon be deprecated. Please change it to either `EDGE_LEGACY`"
            " for the legacy version or to `EDGE_CHROMIUM` for the"
            " new Chromium-based version.",
            DeprecationWarning,
        )


class StitchMode(Enum):
    """
    The type of methods for stitching full-page screenshots.
    """

    Scroll = "Scroll"
    CSS = "CSS"
