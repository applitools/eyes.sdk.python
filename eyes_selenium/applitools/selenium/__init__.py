from applitools.common import BatchInfo, Region, StdoutLogger, logger
from applitools.core import (  # noqa
    ExactMatchSettings,
    FailureReports,
    ImageMatchSettings,
    MatchLevel,
    TestResults,
    TestResultsStatus,
)

from .capture import EyesWebDriverScreenshot, dom_capture  # noqa
from .eyes import Eyes  # noqa
from .frames import Frame  # noqa
from .positioning import StitchMode  # noqa
from .target import (  # noqa
    FloatingBounds,
    FloatingRegion,
    FloatingRegionByElement,
    FloatingRegionBySelector,
    IgnoreRegionByElement,
    IgnoreRegionBySelector,
    Target,
)
from .webdriver import EyesWebDriver  # noqa
from .webelement import EyesWebElement  # noqa

__all__ = (
    # noqa
    "BatchInfo",
    "ExactMatchSettings",
    "ImageMatchSettings",
    "Region",
    "TestResults",
    "MatchLevel",
    "FailureReports",
    "TestResultsStatus",
    "TestResults",
    "logger",
    "StdoutLogger",
    "Eyes",
    "EyesWebElement",
    "EyesWebDriver",
    "Frame",
    "EyesWebDriverScreenshot",
    "StitchMode",
    "dom_capture",
    "IgnoreRegionByElement",
    "IgnoreRegionBySelector",
    "FloatingBounds",
    "FloatingRegionByElement",
    "FloatingRegionBySelector",
    "Target",
)
