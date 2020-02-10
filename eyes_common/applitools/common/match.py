import typing
from enum import Enum

import attr

from .geometry import Region
from .utils.json_utils import JsonInclude

if typing.TYPE_CHECKING:
    from typing import Optional, List, Text
    from applitools.common import EyesScreenshot

__all__ = (
    "MatchLevel",
    "MatchResult",
    "FloatingMatchSettings",
    "ExactMatchSettings",
    "ImageMatchSettings",
    "FloatingBounds",
)


class MatchLevel(Enum):
    """
    The extent in which two images match (or are expected to match).
    """

    # Images do not necessarily match.
    NONE = "None"
    # Images have the same layout.
    LAYOUT = "Layout"
    # Images have the same layout.
    LAYOUT2 = "Layout2"
    # Images have the same content.
    CONTENT = "Content"
    # Images are nearly identical.
    STRICT = "Strict"
    # Images are identical.
    EXACT = "Exact"


class AccessibilityLevel(Enum):
    NONE = "None"
    AA = "AA"
    AAA = "AAA"


@attr.s
class MatchResult(object):
    as_expected = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[bool]
    window_id = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Text]
    screenshot = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[EyesScreenshot]


@attr.s
class FloatingMatchSettings(object):
    _region = attr.ib()  # type: Region
    _bounds = attr.ib()  # type: FloatingBounds
    left = attr.ib(init=False, metadata={JsonInclude.THIS: True})  # type: int
    top = attr.ib(init=False, metadata={JsonInclude.THIS: True})  # type: int
    width = attr.ib(init=False, metadata={JsonInclude.THIS: True})  # type: int
    height = attr.ib(init=False, metadata={JsonInclude.THIS: True})  # type: int
    max_up_offset = attr.ib(init=False, metadata={JsonInclude.THIS: True})  # type: int
    max_down_offset = attr.ib(
        init=False, metadata={JsonInclude.THIS: True}
    )  # type: int
    max_left_offset = attr.ib(
        init=False, metadata={JsonInclude.THIS: True}
    )  # type: int
    max_right_offset = attr.ib(
        init=False, metadata={JsonInclude.THIS: True}
    )  # type: int

    def __attrs_post_init__(self):
        self.left = self._region.left
        self.top = self._region.top
        self.width = self._region.width
        self.height = self._region.height
        self.max_up_offset = self._bounds.max_up_offset
        self.max_down_offset = self._bounds.max_down_offset
        self.max_left_offset = self._bounds.max_left_offset
        self.max_right_offset = self._bounds.max_right_offset


@attr.s
class ExactMatchSettings(object):
    """
    Encapsulates settings for the :py:class:`MatchLevel.EXACT`.
    """

    min_diff_intensity = attr.ib(
        default=0, metadata={JsonInclude.NON_NONE: True}
    )  # type: int
    min_diff_width = attr.ib(
        default=0, metadata={JsonInclude.NON_NONE: True}
    )  # type: int
    min_diff_height = attr.ib(
        default=0, metadata={JsonInclude.NON_NONE: True}
    )  # type: int
    match_threshold = attr.ib(
        default=0, metadata={JsonInclude.NON_NONE: True}
    )  # type: float

    @classmethod
    def create_from(cls, other):
        # type: (ExactMatchSettings) -> ExactMatchSettings
        return ExactMatchSettings(
            min_diff_intensity=other.min_diff_intensity,
            min_diff_width=other.min_diff_width,
            min_diff_height=other.min_diff_height,
            match_threshold=other.match_threshold,
        )


@attr.s
class ImageMatchSettings(object):
    """
    Encapsulates match settings for the a session.
    """

    match_level = attr.ib(
        default=MatchLevel.STRICT, metadata={JsonInclude.THIS: True}
    )  # type: MatchLevel
    exact = attr.ib(
        default=None, type=ExactMatchSettings, metadata={JsonInclude.THIS: True}
    )  # type: Optional[ExactMatchSettings]
    ignore_caret = attr.ib(
        default=False, metadata={JsonInclude.THIS: True}
    )  # type:bool
    use_dom = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[bool]
    enable_patterns = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[bool]
    ignore_displacements = attr.ib(
        default=False, metadata={JsonInclude.THIS: True}
    )  # type:Optional[bool]
    ignore_regions = attr.ib(
        factory=list, metadata={JsonInclude.NAME: "Ignore"}
    )  # type: Optional[List[Region]]
    layout_regions = attr.ib(
        factory=list, metadata={JsonInclude.NAME: "Layout"}
    )  # type: Optional[List[Region]]
    strict_regions = attr.ib(
        factory=list, metadata={JsonInclude.NAME: "Strict"}
    )  # type: Optional[List[Region]]
    content_regions = attr.ib(
        factory=list, metadata={JsonInclude.NAME: "Content"}
    )  # type: Optional[List[Region]]
    floating_match_settings = attr.ib(
        factory=list, metadata={JsonInclude.NAME: "Floating"}
    )  # type: Optional[List[FloatingMatchSettings]]
    # TODO: implement accessibility region
    # accessibility = attr.ib(metadata={JsonInclude.THIS: True})  # type: Optional[List]
    # accessibility_level = attr.ib(
    #     metadata={JsonInclude.THIS: True}
    # )  # type: AccessibilityLevel

    @classmethod
    def create_from(cls, other):
        # type: (ImageMatchSettings) -> ImageMatchSettings
        img = ImageMatchSettings(
            match_level=other.match_level,
            exact=ExactMatchSettings.create_from(other.exact) if other.exact else None,
            use_dom=other.use_dom,
        )
        img.ignore_caret = other.ignore_caret
        img.ignore_regions = other.ignore_regions
        img.layout_regions = other.layout_regions
        img.strict_regions = other.strict_regions
        img.content_regions = other.content_regions
        img.floating_match_settings = other.floating_match_settings
        img.enable_patterns = other.enable_patterns
        img.ignore_displacements = other.ignore_displacements

        return img


@attr.s(slots=True)
class FloatingBounds(object):
    """A floating bounds defined by max_left_offset, max_up_offset, max_right_offset
    and max_down_offset"""

    max_left_offset = attr.ib(default=0)  # type: int
    max_up_offset = attr.ib(default=0)  # type: int
    max_right_offset = attr.ib(default=0)  # type: int
    max_down_offset = attr.ib(default=0)  # type: int
