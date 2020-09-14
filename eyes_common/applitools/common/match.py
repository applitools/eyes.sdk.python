import typing
from enum import Enum

import attr

from .accessibility import AccessibilitySettings
from .geometry import AccessibilityRegion, Rectangle, Region
from .utils.json_utils import JsonInclude

if typing.TYPE_CHECKING:
    from typing import List, Optional, Text, Union

    from applitools.common import EyesScreenshot, Point

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


@attr.s(eq=False)
class FloatingMatchSettings(Rectangle):
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

    def __str__(self):
        return (
            "FloatingMatchSettings({left}, {top}, {width} x {height} "
            "{max_up_offset}, {max_down_offset}, {max_left_offset}, "
            "{max_right_offset}".format(
                left=self.left,
                top=self.top,
                width=self.width,
                height=self.height,
                max_up_offset=self.max_up_offset,
                max_down_offset=self.max_down_offset,
                max_left_offset=self.max_left_offset,
                max_right_offset=self.max_right_offset,
            )
        )

    def __eq__(self, other):
        # type: (FloatingMatchSettings) -> bool
        return (
            self.left == other.left
            and self.top == other.top
            and self.width == other.width
            and self.height == other.height
            and self.max_up_offset == self.max_up_offset
            and self.max_down_offset == self.max_down_offset
            and self.max_left_offset == self.max_left_offset
            and self.max_right_offset == self.max_right_offset
        )

    def __attrs_post_init__(self):
        self.left = self._region.left
        self.top = self._region.top
        self.width = self._region.width
        self.height = self._region.height
        self.max_up_offset = self._bounds.max_up_offset
        self.max_down_offset = self._bounds.max_down_offset
        self.max_left_offset = self._bounds.max_left_offset
        self.max_right_offset = self._bounds.max_right_offset

    def offset(self, location_or_dx, dy=None):  # noqa
        # type: (Union[Point, int], Optional[int]) -> FloatingMatchSettings
        r = super(FloatingMatchSettings, self).offset(location_or_dx, dy)
        return FloatingMatchSettings(r, self._bounds)


@attr.s
class ExactMatchSettings(object):
    """
    Encapsulates settings for the :py:class:`MatchLevel.EXACT`.
    """

    min_diff_intensity = attr.ib(
        default=0, metadata={JsonInclude.THIS: True}
    )  # type: int
    min_diff_width = attr.ib(default=0, metadata={JsonInclude.THIS: True})  # type: int
    min_diff_height = attr.ib(default=0, metadata={JsonInclude.THIS: True})  # type: int
    match_threshold = attr.ib(
        default=0, metadata={JsonInclude.THIS: True}
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
        type=Region, factory=list, metadata={JsonInclude.NAME: "Ignore"}
    )  # type: List[Region]
    layout_regions = attr.ib(
        type=Region, factory=list, metadata={JsonInclude.NAME: "Layout"}
    )  # type: List[Region]
    strict_regions = attr.ib(
        type=Region, factory=list, metadata={JsonInclude.NAME: "Strict"}
    )  # type: List[Region]
    content_regions = attr.ib(
        type=Region, factory=list, metadata={JsonInclude.NAME: "Content"}
    )  # type: List[Region]
    floating_match_settings = attr.ib(
        type=Region, factory=list, metadata={JsonInclude.NAME: "Floating"}
    )  # type: List[FloatingMatchSettings]
    accessibility = attr.ib(
        type=AccessibilityRegion, factory=list, metadata={JsonInclude.THIS: True}
    )  # type: List[AccessibilityRegion]
    accessibility_settings = attr.ib(
        default=None, type=AccessibilitySettings, metadata={JsonInclude.THIS: True}
    )  # type: Optional[AccessibilitySettings]

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
        img.accessibility = other.accessibility
        img.accessibility_settings = other.accessibility_settings

        return img


@attr.s(slots=True)
class FloatingBounds(object):
    """A floating bounds defined by max_left_offset, max_up_offset, max_right_offset
    and max_down_offset"""

    max_left_offset = attr.ib(default=0)  # type: int
    max_up_offset = attr.ib(default=0)  # type: int
    max_right_offset = attr.ib(default=0)  # type: int
    max_down_offset = attr.ib(default=0)  # type: int
