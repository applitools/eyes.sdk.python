from applitools.core import (
    BatchInfo,
    ExactMatchSettings,
    ImageMatchSettings,
    Region,
    TestResults,
    MatchLevel,
    FailureReports,
    TestResultsStatus,
    logger,
)
from .eyes import Eyes
from .target import Target, FloatingBounds, FloatingRegion

__all__ = (
    "Eyes",
    "Target",
    "BatchInfo",
    "ExactMatchSettings",
    "ImageMatchSettings",
    "FloatingBounds",
    "FloatingRegion",
    "Region",
    "TestResults",
    "MatchLevel",
    "FailureReports",
    "TestResultsStatus",
    "logger",
)
