from applitools.core import (
    BatchInfo, ExactMatchSettings, ImageMatchSettings, Region, TestResults, MatchLevel, FailureReports,
    TestResultsStatus, TestResults, logger,
)

from .capture import EyesWebDriverScreenshot, dom_capture
from .positioning import StitchMode
from .eyes import Eyes
from .webdriver import EyesWebDriver
from .webelement import EyesWebElement
from .target import (
    IgnoreRegionByElement, IgnoreRegionBySelector, FloatingBounds, FloatingRegion, FloatingRegionByElement,
    FloatingRegionBySelector, Target,
)
from .frames import Frame

__all__ = (target.__all__ +  # noqa
           ('BatchInfo', 'ExactMatchSettings', 'ImageMatchSettings', 'Region', 'TestResults', 'MatchLevel',
            'FailureReports', 'TestResultsStatus', 'TestResults', 'logger') +  # noqa
           ('Eyes', 'EyesWebElement', 'EyesWebDriver', 'Frame', 'EyesWebDriverScreenshot', 'StitchMode', 'dom_capture'))
