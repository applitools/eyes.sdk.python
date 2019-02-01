from applitools.core import (  # noqa
    BatchInfo,
    ExactMatchSettings,
    ImageMatchSettings,
    Region,
    TestResults,
    MatchLevel,
    FailureReports,
    TestResultsStatus,
    TestResults,
    logger,
)
from .capture import EyesWebDriverScreenshot, dom_capture  # noqa
from .positioning import StitchMode  # noqa
from .eyes import Eyes  # noqa
from .webdriver import EyesWebDriver  # noqa
from .webelement import EyesWebElement  # noqa
from .target import (  # noqa
    IgnoreRegionByElement,
    IgnoreRegionBySelector,
    FloatingBounds,
    FloatingRegion,
    FloatingRegionByElement,
    FloatingRegionBySelector,
    Target,
)
from .frames import Frame  # noqa

__all__ = (
    "Frame"
    + target.__all__  # noqa
    + (  # noqa
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
    )
    + (  # noqa
        "Eyes",
        "EyesWebElement",
        "EyesWebDriver",
        "Frame",
        "EyesWebDriverScreenshot",
        "StitchMode",
        "dom_capture",
    )
)
