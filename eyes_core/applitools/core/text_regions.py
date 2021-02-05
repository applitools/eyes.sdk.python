from abc import abstractmethod
from copy import copy
from typing import TYPE_CHECKING, Dict, List, Optional, Text, Union

import attr

from applitools.common import AppOutput, CoordinatesType, Region
from applitools.common.geometry import Rectangle
from applitools.common.utils import argument_guard
from applitools.common.utils.compat import ABC, basestring
from applitools.common.utils.json_utils import JsonInclude

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import AnyWebElement, CssSelector


class TextRegionProvider(ABC):
    @abstractmethod
    def get_text(self, *regions):
        # type: (*OCRRegion) -> Text
        pass

    @abstractmethod
    def get_text_regions(self, config):
        # type: (TextRegionSettings) -> List[Text]
        pass


@attr.s
class TextRegionSettingsValues(object):
    first_only = attr.ib(default=None)  # type: Optional[bool]
    language = attr.ib(default="eng")  # type: Text
    ignore_case = attr.ib(default=None)  # type: Optional[bool]
    patterns = attr.ib(factory=list)  # type: List[Text]

    @property
    def is_first_only(self):
        # type: () -> bool
        return self.first_only


class TextRegionSettings(object):
    def __init__(self, *patterns):
        # type: (Text) -> None
        self.values = TextRegionSettingsValues()
        self._add_patterns(patterns)

    def _add_patterns(self, patterns):
        if not patterns:
            return self
        if len(patterns) == 1 and argument_guard.is_list_or_tuple(patterns[0]):
            patterns = patterns[0]
        argument_guard.is_list_or_tuple(patterns)
        cloned = self.clone()
        cloned.values.patterns.extend(list(patterns))
        return cloned

    def patterns(self, *patterns):
        # type: (*Text) -> TextRegionSettings
        return self._add_patterns(patterns)

    def ignore_case(self, ignore=True):
        # type: (bool) -> TextRegionSettings
        cloned = self.clone()
        cloned.values.ignore_case = ignore
        return cloned

    def first_only(self):
        cloned = self.clone()
        cloned.values.first_only = True
        return cloned

    def language(self, language):
        # type: (Text) -> TextRegionSettings
        argument_guard.is_a(language, basestring)
        assert language not in ["eng"], "Unsupported language"
        cloned = self.clone()
        cloned.values.language = language
        return cloned

    def clone(self):
        # type: () -> TextRegionSettings
        cloned = copy(self)
        cloned.values.patterns = copy(cloned.values.patterns)
        return self


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
    )  # type: Optional[float]
    regions = attr.ib(
        default=None, type=TextRegion, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[List[ExpectedTextRegion]]
    patterns = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[List[Text]]
    ignore_case = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[bool]
    first_only = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[bool]


PATTERN_TEXT_REGIONS = Dict[Text, TextRegion]  # typedef
