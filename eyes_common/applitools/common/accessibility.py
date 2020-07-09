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
        level,  # type: Union[Text,AccessibilityLevel]
        guidelines_version,  # type: Union[Text,AccessibilityGuidelinesVersion]
    ):
        # type: (...) -> None
        if isinstance(level, basestring):
            level = AccessibilityLevel(level)
        if isinstance(guidelines_version, basestring):
            guidelines_version = AccessibilityGuidelinesVersion(guidelines_version)
        self.level = level
        self.guidelines_version = guidelines_version


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
    )  # type: Union[Text,AccessibilityStatus]

    def __init__(
        self,
        status,  # type: Union[Text,AccessibilityStatus]
        level,  # type: Union[Text,AccessibilityLevel]
        guidelines_version,  # type: Union[Text,AccessibilityGuidelinesVersion]
    ):
        super(SessionAccessibilityStatus, self).__init__(level, guidelines_version)
        if isinstance(status, basestring):
            status = AccessibilityStatus(status)
        self.status = status
