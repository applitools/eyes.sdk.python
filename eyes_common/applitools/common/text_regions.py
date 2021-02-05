import typing

import attr

from applitools.common.app_output import AppOutput
from applitools.common.geometry import CoordinatesType, Rectangle, Region
from applitools.common.utils.json_utils import JsonInclude

if typing.TYPE_CHECKING:
    from typing import List, Optional, Text, Union

    from applitools.common.utils.custom_types import AnyWebElement, CssSelector


@attr.s(slots=True, init=False)
class TextRegion(Rectangle):
    left = attr.ib(metadata={JsonInclude.NAME: "x"})  # type: int
    top = attr.ib(metadata={JsonInclude.NAME: "y"})  # type: int
    width = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    height = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    text = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text

    @property
    def x(self):
        return self.left

    @property
    def y(self):
        return self.top

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
    target = attr.ib()  # type: Union[Region, AnyWebElement, CssSelector]
    hint = attr.ib(default="")  # type: Text
    language = attr.ib(default="eng")  # type: Text
    min_match = attr.ib(
        default=None,
    )  # type: Optional[float]


@attr.s
class TextSettingsData(object):
    app_output = attr.ib(
        type=AppOutput, metadata={JsonInclude.THIS: True}
    )  # type: AppOutput
    language = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    min_match = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: float
    regions = attr.ib(
        default=None, type=TextRegion, metadata={JsonInclude.NON_NONE: True}
    )  # type: List[ExpectedTextRegion]
    patterns = attr.ib(default=None, metadata={JsonInclude.NON_NONE: True})
    ignore_case = attr.ib(default=None, metadata={JsonInclude.NON_NONE: True})
    first_only = attr.ib(default=None, metadata={JsonInclude.NON_NONE: True})


PATTERN_TEXT_REGIONS = typing.Dict[typing.Text, TextRegion]  # typedef
