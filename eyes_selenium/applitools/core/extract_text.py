from copy import copy
from typing import TYPE_CHECKING, Dict, List, Optional, Text, TypeVar, Union

import attr
from six import string_types

from applitools.common import Region
from applitools.common.geometry import Rectangle
from applitools.common.utils import argument_guard
from applitools.common.utils.json_utils import JsonInclude
from applitools.common.validators import is_list_or_tuple
from applitools.selenium.fluent.target_path import Locator, TargetPath

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import BySelector


class TextRegionSettings(object):
    def __init__(self, *patterns):
        # type: (*Union[Text, List[Text]]) -> None
        self._first_only = None  # type: Optional[bool]
        self._language = "eng"  # type: Text
        self._ignore_case = None  # type: Optional[bool]
        self._patterns = []  # type: List[Text]
        self._add_patterns(*patterns)

    @property
    def is_first_only(self):
        # type: () -> bool
        return self._first_only

    def _add_patterns(self, *patterns):
        if not patterns:
            return self
        if len(patterns) == 1 and argument_guard.is_list_or_tuple(patterns[0]):
            patterns = patterns[0]
        argument_guard.is_list_or_tuple(patterns)
        cloned = self._clone()
        cloned._patterns.extend(list(patterns))
        return cloned

    def ignore_case(self, ignore=True):
        # type: (bool) -> TextRegionSettings
        cloned = self._clone()
        cloned._ignore_case = ignore
        return cloned

    def first_only(self):
        cloned = self._clone()
        cloned._first_only = True
        return cloned

    def language(self, language):
        # type: (Text) -> TextRegionSettings
        argument_guard.is_a(language, string_types)
        assert language not in ["eng"], "Unsupported language"
        cloned = self._clone()
        cloned._language = language
        return cloned

    def _clone(self):
        # type: () -> TextRegionSettings
        cloned = copy(self)
        cloned._patterns = copy(cloned._patterns)
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


class OCRRegion(object):
    def __init__(self, target):
        # type: (Union[Region, Text, BySelector, Locator]) -> None
        if isinstance(target, string_types):
            self.target = TargetPath.region(target)
        elif is_list_or_tuple(target):
            self.target = TargetPath.region(*target)
        else:
            self.target = target
        self._hint = None  # type: Optional[Text]
        self._language = "eng"  # type: Optional[Text]
        self._min_match = None  # type: Optional[float]

    def min_match(self, min_match):
        # type: (float) -> Self
        cloned = self._clone()
        cloned._min_match = min_match
        return cloned

    def hint(self, hint):
        # type: (Text) -> Self
        cloned = self._clone()
        cloned._hint = hint
        return cloned

    def language(self, language):
        # type: (Text) -> Self
        cloned = self._clone()
        cloned._language = language
        return cloned

    def _clone(self):
        # type: () -> Self
        return copy(self)


PATTERN_TEXT_REGIONS = Dict[Text, List[TextRegion]]  # typedef
Self = TypeVar("Self", bound="OCRRegion")  # typedef
