from .batch_close import BatchClose
from .cut import FixedCutProvider, NullCutProvider, UnscaledFixedCutProvider
from .extract_text import BaseOCRRegion, ExtractTextProvider, TextRegionSettings
from .feature import Feature
from .fluent import (
    CheckSettings,
    CheckSettingsValues,
    FloatingRegionByRectangle,
    GetFloatingRegion,
    GetRegion,
    RegionByRectangle,
)
from .locators import VisualLocator, VisualLocatorSettings
from .scaling import (
    ContextBasedScaleProvider,
    FixedScaleProvider,
    NullScaleProvider,
    ScaleProvider,
)
from .triggers import MouseTrigger, TextTrigger

__all__ = (
    "TextTrigger",
    "MouseTrigger",
    "ContextBasedScaleProvider",
    "FixedScaleProvider",
    "Feature",
    "NullScaleProvider",
    "ScaleProvider",
    "FixedCutProvider",
    "NullCutProvider",
    "UnscaledFixedCutProvider",
    "CheckSettings",
    "CheckSettingsValues",
    "GetRegion",
    "GetFloatingRegion",
    "FloatingRegionByRectangle",
    "RegionByRectangle",
    "BatchClose",
    "VisualLocator",
    "VisualLocatorSettings",
    "TextRegionSettings",
    "ExtractTextProvider",
    "BaseOCRRegion",
)
