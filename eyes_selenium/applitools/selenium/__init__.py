from applitools.common import (
    DeviceName,
    MatchLevel,
    Region,
    StdoutLogger,
    FileLogger,
    logger,
    RectangleSize,
    TestResults,
    TestResultContainer,
    TestResultsSummary,
)
from applitools.common.ultrafastgrid import (
    IosDeviceInfo,
    ScreenOrientation,
    IosDeviceName,
    ChromeEmulationInfo,
    DesktopBrowserInfo,
)  # noqa
from applitools.common.geometry import AccessibilityRegion
from applitools.common.config import BatchInfo  # noqa
from applitools.common.selenium import BrowserType, Configuration, StitchMode  # noqa
from applitools.common.server import FailureReports  # noqa
from applitools.core.cut import (  # noqa
    FixedCutProvider,
    NullCutProvider,
    UnscaledFixedCutProvider,
)
from applitools.common.accessibility import (  # noqa
    AccessibilityRegionType,
    AccessibilitySettings,
    AccessibilityLevel,
    AccessibilityGuidelinesVersion,
)
from applitools.core.fluent.region import AccessibilityRegionByRectangle  # noqa
from applitools.core.batch_close import BatchClose  # noqa

from .classic_runner import ClassicRunner  # noqa
from .eyes import Eyes  # noqa
from .fluent.target import Target  # noqa
from .visual_grid import VisualGridRunner  # noqa
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
    "ChromeEmulationInfo",
    "DesktopBrowserInfo",
)
