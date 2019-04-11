from enum import Enum


class BrowserType(Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    IE10 = "ie10"
    IE11 = "ie"
    EDGE = "edge"


class StitchMode(Enum):
    """
    The type of methods for stitching full-page screenshots.
    """

    Scroll = "Scroll"
    CSS = "CSS"
