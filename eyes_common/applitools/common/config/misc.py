from enum import Enum


class BrowserType(Enum):
    CHROME = "CHROME"
    FIREFOX = "FIREFOX"
    IE = "IE"
    EDGE = "EDGE"


class StitchMode(Enum):
    """
    The type of methods for stitching full-page screenshots.
    """

    Scroll = "Scroll"
    CSS = "CSS"
