from applitools.common import (
    BatchInfo,
    ExactMatchSettings,
    ImageMatchSettings,
    MatchLevel,
    Region,
    StdoutLogger,
    logger,
)
from applitools.common.metadata import FailureReports
from applitools.common.test_results import TestResults, TestResultsStatus  # noqa
from applitools.selenium.fluent.region import (
    FloatingBounds,
    FloatingRegion,
    FloatingRegionByElement,
    FloatingRegionBySelector,
    IgnoreRegionByElement,
    IgnoreRegionBySelector,
)
from applitools.selenium.fluent.target import Target  # noqa

from .capture import EyesWebDriverScreenshot, dom_capture  # noqa
from .configuration import SeleniumConfiguration  # noqa
from .eyes import Eyes  # noqa
from .frames import Frame  # noqa
from .positioning import StitchMode  # noqa
from .webdriver import EyesWebDriver  # noqa
from .webelement import EyesWebElement  # noqa

__all__ = (
    # noqa
    "ExactMatchSettings",
    "BatchInfo",
    "ImageMatchSettings",
    "FailureReports",
    "Region",
    "TestResults",
    "MatchLevel",
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
    "Target",
    "SeleniumConfiguration",
    "IgnoreRegionByElement",
    "IgnoreRegionBySelector",
    "FloatingBounds",
    "FloatingRegion",
    "FloatingRegionByElement",
    "FloatingRegionBySelector",
)
