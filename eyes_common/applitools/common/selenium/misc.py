from enum import Enum


class BrowserType(Enum):
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
    EDGE = "edge"


class StitchMode(Enum):
    """
    The type of methods for stitching full-page screenshots.
    """

    Scroll = "Scroll"
    CSS = "CSS"
