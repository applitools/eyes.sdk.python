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

    min_diff_intensity = attr.ib()  # type: int
    min_diff_width = attr.ib()  # type: int
    min_diff_height = attr.ib()  # type: int
    match_threshold = attr.ib()  # type: float


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
    send_dom = attr.ib(default=False, metadata={JsonInclude.THIS: True})  # type:bool
    use_dom = attr.ib(default=False, metadata={JsonInclude.THIS: True})  # type:bool
    enable_patterns = attr.ib(
        default=False, metadata={JsonInclude.THIS: True}
    )  # type:bool
    ignore_displacements = attr.ib(
        default=False, metadata={JsonInclude.THIS: True}
    )  # type:bool

    ignore = attr.ib(
        factory=list, metadata={JsonInclude.THIS: True}
    )  # type: List[Region]
    layout = attr.ib(
        factory=list, metadata={JsonInclude.THIS: True}
    )  # type: List[Region]
    strict = attr.ib(
        factory=list, metadata={JsonInclude.THIS: True}
    )  # type: List[Region]
    content = attr.ib(
        factory=list, metadata={JsonInclude.THIS: True}
    )  # type: List[Region]
    floating = attr.ib(
        factory=list, metadata={JsonInclude.THIS: True}
    )  # type: List[Region]

    @classmethod
    def create_from_check_settings(cls, check_settings):
        return ImageMatchSettings(
            match_level=check_settings.values.match_level,
            ignore_caret=check_settings.values.ignore_caret,
            send_dom=check_settings.values.send_dom,
            use_dom=check_settings.values.use_dom,
            enable_patterns=check_settings.values.enable_patterns,
            ignore_displacements=check_settings.values.ignore_displacements,
        )


@attr.s(slots=True)
class FloatingBounds(object):
    """A floating bounds defined by max_left_offset, max_up_offset, max_right_offset
    and max_down_offset"""

    max_left_offset = attr.ib(default=0)  # type: int
    max_up_offset = attr.ib(default=0)  # type: int
    max_right_offset = attr.ib(default=0)  # type: int
    max_down_offset = attr.ib(default=0)  # type: int
