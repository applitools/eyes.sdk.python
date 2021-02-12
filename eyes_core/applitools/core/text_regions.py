from abc import abstractmethod
from copy import copy
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Text, Union

import attr

from applitools.common import AppOutput, Region
from applitools.common.geometry import Rectangle
from applitools.common.utils import argument_guard
from applitools.common.utils.compat import ABC, basestring
from applitools.common.utils.json_utils import JsonInclude
from applitools.core import AppOutputWithScreenshot


class TextRegionProvider(ABC):
    @abstractmethod
    def get_text(self, *regions):
        # type: (*BaseOCRRegion) -> Text
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
        # type: (*Union[Text, List[Text]]) -> None
        self.values = TextRegionSettingsValues()
        self._add_patterns(*patterns)

    def _add_patterns(self, *patterns):
        if not patterns:
            return self
        if len(patterns) == 1 and argument_guard.is_list_or_tuple(patterns[0]):
            patterns = patterns[0]
        argument_guard.is_list_or_tuple(patterns)
        cloned = self.clone()
        cloned.values.patterns.extend(list(patterns))
        return cloned

    def patterns(self, *patterns):
        # type: (*Union[Text, List[Text]]) -> TextRegionSettings
        return self._add_patterns(*patterns)

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
class ExpectedTextRegion(Rectangle):
    expected = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text

    def __init__(
        self,
        left,  # type: int
        top,  # type: int
        width,  # type: int
        height,  # type: int
        expected=None,  # type: Text
    ):
        # type: (...) -> None
        super(ExpectedTextRegion, self).__init__(left, top, width, height)
        self.expected = expected


@attr.s(init=False)
class BaseOCRRegion(object):
    target = attr.ib()
    hint = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[Text]
    language = attr.ib(default="eng", metadata={JsonInclude.THIS: True})  # type: Text
    min_match = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[float]
    app_output = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[AppOutputWithScreenshot]
    regions = attr.ib(
        factory=list, metadata={JsonInclude.THIS: True}
    )  # type: List[ExpectedTextRegion]

    def __init__(self, target, hint="", language="eng", min_match=None):
        # type: (Region, Text, Text, Optional[float]) -> None
        argument_guard.not_list_or_tuple(target)
        self.target = target
        self.hint = hint
        self.language = language
        self.min_match = min_match
        self.process_app_output = None  # type: Optional[Callable]
        self.regions = []

    def add_process_app_output(self, callback):
        # type: (Callable) -> None
        if not callable(callback):
            raise ValueError
        self.process_app_output = callback


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
        default=None, metadata={JsonInclude.NON_NONE: True}
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
    hint = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[Text]


PATTERN_TEXT_REGIONS = Dict[Text, TextRegion]  # typedef
