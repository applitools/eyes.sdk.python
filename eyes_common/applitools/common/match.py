import typing
from enum import Enum

import attr

from applitools.common.utils.converters import value_from_enum

from .geometry import Region

if typing.TYPE_CHECKING:
    from typing import Optional, Text

__all__ = (
    "MatchLevel",
    "MatchResult",
    "FloatingMatchSettings",
    "ExactMatchSettings",
    "ImageMatchSettings",
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
    as_expected = attr.ib(default=None)
    window_id = attr.ib(default=None)
    screenshot = attr.ib(default=None)


@attr.s
class FloatingMatchSettings(object):
    left = attr.ib()
    top = attr.ib()
    width = attr.ib()
    height = attr.ib()
    max_up_offset = attr.ib()
    max_down_offset = attr.ib()
    max_left_offset = attr.ib()
    max_right_offset = attr.ib()

    def get_region(self):
        # type: () -> Region
        return Region(
            left=self.left, top=self.top, width=self.width, height=self.height
        )


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
        default=MatchLevel.STRICT.value, converter=value_from_enum
    )  # type: Text
    exact = attr.ib(
        default=None, type=ExactMatchSettings
    )  # type: Optional[ExactMatchSettings]
    ignore_caret = attr.ib(default=None)
    send_dom = attr.ib(default=False)
    use_dom = attr.ib(default=False)
    enable_patterns = attr.ib(default=False)

    ignore_regions = attr.ib(factory=list)
    layout_regions = attr.ib(factory=list)
    strict_regions = attr.ib(factory=list)
    content_regions = attr.ib(factory=list)
    floating_regions = attr.ib(factory=list)
