import warnings
from enum import Enum

from applitools.common.utils.general_utils import DynamicEnumGetter


class BrowserType(Enum):
    CHROME = "chrome"
    CHROME_ONE_VERSION_BACK = "chrome-one-version-back"
    CHROME_TWO_VERSIONS_BACK = "chrome-two-versions-back"
    FIREFOX = "firefox"
    FIREFOX_ONE_VERSION_BACK = "firefox-one-version-back"
    FIREFOX_TWO_VERSIONS_BACK = "firefox-two-versions-back"
    SAFARI = "safari"
    SAFARI_ONE_VERSION_BACK = "safari-one-version-back"
    SAFARI_TWO_VERSIONS_BACK = "safari-two-versions-back"
    SAFARI_EARLY_ACCESS = "safari-earlyaccess"
    IE_10 = "ie10"
    IE_11 = "ie11"
    EDGE_LEGACY = "edgelegacy"
    EDGE_CHROMIUM = "edgechromium"
    EDGE_CHROMIUM_ONE_VERSION_BACK = "edgechromium-one-version-back"
    EDGE_CHROMIUM_TWO_VERSIONS_BACK = "edgechromium-two-versions-back"

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
