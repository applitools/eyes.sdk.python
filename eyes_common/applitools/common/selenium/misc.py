from enum import Enum


class BrowserType(Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    IE_10 = "ie10"
    IE_11 = "ie"
    EDGE = "edge"


class StitchMode(Enum):
    """
    The type of methods for stitching full-page screenshots.
    """

    Scroll = "Scroll"
    CSS = "CSS"
