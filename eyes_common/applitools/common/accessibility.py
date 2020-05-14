from enum import Enum

import attr

from applitools.common.utils.json_utils import JsonInclude


class AccessibilityGuidelinesVersion(Enum):
    WCAG_2_0 = "WCAG_2_0"
    WCAG_2_1 = "WCAG_2_1"


class AccessibilityLevel(Enum):
    AA = "AA"
    AAA = "AAA"


@attr.s
class AccessibilitySettings(object):
    level = attr.ib(
        type=AccessibilityLevel, metadata={JsonInclude.THIS: True}
    )  # type: AccessibilityLevel
    version = attr.ib(
        type=AccessibilityGuidelinesVersion, metadata={JsonInclude.THIS: True}
    )  # type: AccessibilityGuidelinesVersion


class AccessibilityRegionType(Enum):
    IgnoreContrast = "IgnoreContrast"
    RegularText = "RegularText"
    LargeText = "LargeText"
    BoldText = "BoldText"
    GraphicalObject = "GraphicalObject"


class TestAccessibilityStatus(Enum):
    """
    Accessibility status.
    """

    # Session has passed accessibility validation.
    Passed = "Passed"
    # Session hasn't passed accessibility validation.
    Failed = "Failed"
