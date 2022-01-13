import warnings
from enum import Enum

from applitools.common.utils.general_utils import DynamicEnumGetter


class BrowserType(Enum):
    CHROME = "chrome"
    CHROME_ONE_VERSION_BACK = "chrome-1"
    CHROME_TWO_VERSIONS_BACK = "chrome-2"
    FIREFOX = "firefox"
    FIREFOX_ONE_VERSION_BACK = "firefox-1"
    FIREFOX_TWO_VERSIONS_BACK = "firefox-2"
    SAFARI = "safari"
    SAFARI_ONE_VERSION_BACK = "safari-1"
    SAFARI_TWO_VERSIONS_BACK = "safari-2"
    SAFARI_EARLY_ACCESS = "safari-earlyaccess"
    IE_10 = "ie10"
    IE_11 = "ie"
    EDGE_LEGACY = "edgelegacy"
    EDGE_CHROMIUM = "edgechromium"
    EDGE_CHROMIUM_ONE_VERSION_BACK = "edgechromium-1"
    EDGE_CHROMIUM_TWO_VERSIONS_BACK = "edgechromium-2"

    @DynamicEnumGetter
    def EDGE(self):
        # type: () -> BrowserType
        warnings.warn(
            "The `EDGE` option that is being used in your browsers configuration"
            " will soon be deprecated. Please change it to either `EDGE_LEGACY`"
            " for the legacy version or to `EDGE_CHROMIUM` for the"
            " new Chromium-based version.",
            DeprecationWarning,
            stacklevel=3,
        )
        return self.EDGE_LEGACY


class StitchMode(Enum):
    """
    The type of methods for stitching full-page screenshots.
    """

    Scroll = "Scroll"
    CSS = "CSS"
