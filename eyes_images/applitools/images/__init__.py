from applitools.common import (
    BatchInfo,
    Configuration,
    FileLogger,
    MatchLevel,
    StdoutLogger,
    TestResultContainer,
    TestResults,
    TestResultsSummary,
    logger,
)
from applitools.common.accessibility import (
    AccessibilityGuidelinesVersion,
    AccessibilityLevel,
    AccessibilityRegionType,
    AccessibilitySettings,
)
from applitools.common.geometry import AccessibilityRegion, RectangleSize, Region
from applitools.core.batch_close import BatchClose
from applitools.core.cut import (
    FixedCutProvider,
    NullCutProvider,
    UnscaledFixedCutProvider,
)
from applitools.core.fluent.region import AccessibilityRegionByRectangle

from .extract_text import OCRRegion, TextRegionSettings
from .eyes import Eyes
from .fluent import Target

__all__ = (
    "Eyes",
    "BatchInfo",
    "Region",
    "MatchLevel",
    "logger",
    "StdoutLogger",
    "FileLogger",
    "Target",
    "FixedCutProvider",
    "UnscaledFixedCutProvider",
    "NullCutProvider",
    "RectangleSize",
    "TestResults",
    "TestResultContainer",
    "TestResultsSummary",
    "BatchClose",
    "Configuration",
    "AccessibilityRegionType",
    "AccessibilityLevel",
    "AccessibilitySettings",
    "AccessibilityGuidelinesVersion",
    "AccessibilityRegionByRectangle",
    "AccessibilityRegion",
    "OCRRegion",
    "TextRegionSettings",
)
