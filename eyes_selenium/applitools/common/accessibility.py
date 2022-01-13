from enum import Enum

import attr

from applitools.common import deprecated
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
        type=AccessibilityLevel, metadata={JsonInclude.THIS: True}
    )  # type: AccessibilityLevel
    guidelines_version = attr.ib(
        type=AccessibilityGuidelinesVersion, metadata={JsonInclude.NAME: "version"}
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
class SessionAccessibilityStatus(object):
    level = attr.ib(
        type=AccessibilityLevel, metadata={JsonInclude.THIS: True}
    )  # type: AccessibilityLevel
    version = attr.ib(
        type=AccessibilityGuidelinesVersion, metadata={JsonInclude.THIS: True}
    )  # type: AccessibilityGuidelinesVersion
    status = attr.ib(
        type=AccessibilityStatus, metadata={JsonInclude.THIS: True}
    )  # type: AccessibilityStatus

    def __init__(
        self,
        status,  # type: AccessibilityStatus
        level,  # type: AccessibilityLevel
        version,  # type: AccessibilityGuidelinesVersion
    ):
        self.level = AccessibilityLevel(level)
        self.version = AccessibilityGuidelinesVersion(version)
        self.status = AccessibilityStatus(status)

    @property
    @deprecated.attribute("use `version` instead")
    def guidelines_version(self):
        # type: () -> AccessibilityGuidelinesVersion
        return self.version
