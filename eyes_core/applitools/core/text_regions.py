from abc import ABC, abstractmethod
from copy import copy
from typing import TYPE_CHECKING, List, Text

import attr

from applitools.common.utils import argument_guard
from applitools.common.utils.compat import basestring

if TYPE_CHECKING:
    from applitools.common.text_regions import OCRRegion


class TextRegionsProvider(ABC):
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
    first_only = attr.ib(default=None)  # type: bool
    language = attr.ib(default="eng")  # type: Text
    ignore_case = attr.ib(default=None)  # type: bool
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
            return
        if len(patterns) == 1 and argument_guard.is_list_or_tuple(patterns[0]):
            patterns = patterns[0]
        argument_guard.is_list_or_tuple(patterns)
        cloned = self.clone()
        cloned.values.patterns.extend(list(patterns))
        return cloned

    def patterns(self, *patterns):
        return self._add_patterns(patterns)

    def ignore_case(self, ignore=True):
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
        cloned = copy(self)
        cloned.values.patterns = copy(cloned.values.patterns)
        return self
