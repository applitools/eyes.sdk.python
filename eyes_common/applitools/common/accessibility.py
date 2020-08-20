from enum import Enum
from typing import Union, Text

import attr

from applitools.common.utils.compat import basestring
from applitools.common.utils.json_utils import JsonInclude


class AccessibilityGuidelinesVersion(Enum):
    WCAG_2_0 = "WCAG_2_0"
    WCAG_2_1 = "WCAG_2_1"


class AccessibilityLevel(Enum):
    AA = "AA"
    AAA = "AAA"


@attr.s(init=False)
class AccessibilitySettings(object):
    level = attr.ib(
        type=AccessibilityLevel, metadata={JsonInclude.THIS: True},
    )  # type: AccessibilityLevel
    guidelines_version = attr.ib(
        type=AccessibilityGuidelinesVersion, metadata={JsonInclude.NAME: "version"},
    )  # type: AccessibilityGuidelinesVersion

    def __init__(
        self,
        level,  # type: AccessibilityLevel
        guidelines_version,  # type: AccessibilityGuidelinesVersion
    ):
        # type: (...) -> None
        self.level = AccessibilityLevel(level)
        self.guidelines_version = AccessibilityGuidelinesVersion(guidelines_version)


class AccessibilityRegionType(Enum):
    IgnoreContrast = "IgnoreContrast"
    RegularText = "RegularText"
    LargeText = "LargeText"
    BoldText = "BoldText"
    GraphicalObject = "GraphicalObject"


class AccessibilityStatus(Enum):
    """
    Accessibility status.
    """

    # Session has passed accessibility validation.
    Passed = "Passed"
    # Session hasn't passed accessibility validation.
    Failed = "Failed"


@attr.s(init=False)
class SessionAccessibilityStatus(AccessibilitySettings):
    status = attr.ib(
        type=AccessibilityStatus, metadata={JsonInclude.THIS: True},
    )  # type: AccessibilityStatus

    def __init__(
        self,
        status,  # type: AccessibilityStatus
        level,  # type: AccessibilityLevel
        guidelines_version,  # type: AccessibilityGuidelinesVersion
    ):
        super(SessionAccessibilityStatus, self).__init__(level, guidelines_version)
        self.status = AccessibilityStatus(status)
