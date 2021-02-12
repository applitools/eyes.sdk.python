from applitools.common import (
    DeviceName,
    FileLogger,
    MatchLevel,
    RectangleSize,
    Region,
    StdoutLogger,
    TestResultContainer,
    TestResults,
    TestResultsSummary,
    logger,
)
from applitools.common.accessibility import (  # noqa
    AccessibilityGuidelinesVersion,
    AccessibilityLevel,
    AccessibilityRegionType,
    AccessibilitySettings,
)
from applitools.common.config import BatchInfo  # noqa
from applitools.common.geometry import AccessibilityRegion
from applitools.common.selenium import BrowserType, Configuration, StitchMode  # noqa
from applitools.common.server import FailureReports  # noqa
from applitools.common.ultrafastgrid import (  # noqa
    ChromeEmulationInfo,
    DesktopBrowserInfo,
    IosDeviceInfo,
    IosDeviceName,
    IosVersion,
    ScreenOrientation,
)
from applitools.core.batch_close import BatchClose  # noqa
from applitools.core.cut import (  # noqa
    FixedCutProvider,
    NullCutProvider,
    UnscaledFixedCutProvider,
)
from applitools.core.fluent.region import AccessibilityRegionByRectangle  # noqa

from .classic_runner import ClassicRunner  # noqa
from .extract_text import OCRRegion, TextRegionSettings
from .eyes import Eyes  # noqa
from .fluent.target import Target  # noqa
from .visual_grid import RunnerOptions, VisualGridRunner  # noqa
from .webdriver import EyesWebDriver  # noqa
from .webelement import EyesWebElement  # noqa

__all__ = (
    # noqa
    "BatchInfo",
    "Region",
    "MatchLevel",
    "logger",
    "StdoutLogger",
    "FileLogger",
    "Eyes",
    "Target",
    "FailureReports",
    "StitchMode",
    "VisualGridRunner",
    "RunnerOptions",
    "BrowserType",
    "DeviceName",
    "Configuration",
    "ScreenOrientation",
    "FixedCutProvider",
    "NullCutProvider",
    "UnscaledFixedCutProvider",
    "ClassicRunner",
    "RectangleSize",
    "TestResults",
    "TestResultContainer",
    "TestResultsSummary",
    "BatchClose",
    "AccessibilityRegionType",
    "AccessibilityLevel",
    "AccessibilitySettings",
    "AccessibilityGuidelinesVersion",
    "AccessibilityRegionByRectangle",
    "AccessibilityRegion",
    "IosDeviceName",
    "IosDeviceInfo",
    "IosVersion",
    "ChromeEmulationInfo",
    "DesktopBrowserInfo",
    "OCRRegion",
    "TextRegionSettings",
)
