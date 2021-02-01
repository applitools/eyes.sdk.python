import typing
from enum import Enum

import attr

from .app_output import AppOutput
from .geometry import CoordinatesType, Rectangle, Region
from .utils.json_utils import JsonInclude

if typing.TYPE_CHECKING:
    from typing import List, Optional, Text


class Language(Enum):
    ENGLISH = "eng"


@attr.s(slots=True, init=False)
class TextRegion(Rectangle):
    left = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    top = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    width = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    height = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    text = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Text

    def __init__(
        self,
        left,  # type: int
        top,  # type: int
        width,  # type: int
        height,  # type: int
        text,  # type: Text
    ):
        # type: (...) -> None
        super(TextRegion, self).__init__(left, top, width, height)
        self.text = text


@attr.s(slots=True, init=False)
class ExpectedTextRegion(Region):
    left = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    top = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    width = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    height = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    coordinates_type = attr.ib(
        converter=CoordinatesType,
        type=CoordinatesType,
        metadata={JsonInclude.THIS: True},
    )  # type: CoordinatesType
    expected = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Text

    def __init__(
        self,
        left,  # type: int
        top,  # type: int
        width,  # type: int
        height,  # type: int
        coordinates_type=CoordinatesType.SCREENSHOT_AS_IS,  # type: CoordinatesType
        expected=None,  # type: Text
    ):
        # type: (...) -> None
        super(TextRegion, self).__init__(left, top, width, height, coordinates_type)
        self.expected = expected


@attr.s
class OCRRegion(object):
    app_output = attr.ib(
        type=AppOutput, metadata={JsonInclude.THIS: True}
    )  # type: AppOutput
    regions = attr.ib(
        type=TextRegion, metadata={JsonInclude.THIS: True}
    )  # type: List[ExpectedTextRegion]
    language = attr.ib(
        type=Language, metadata={JsonInclude.THIS: True}
    )  # type: Language
    min_match = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[float]


@attr.s
class TextRegionSettings(object):
    app_output = attr.ib(
        type=AppOutput, metadata={JsonInclude.THIS: True}
    )  # type: AppOutput
    patterns = attr.ib(metadata={JsonInclude.THIS: True})  # type: List[Text]
    ignore_case = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[bool]
    first_only = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[bool]
    language = attr.ib(
        default=None, type=Language, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Language]
