from abc import abstractmethod
from copy import copy
from typing import Dict, List, Text, Union

import attr

from applitools.common import Region
from applitools.common.utils import argument_guard
from applitools.common.utils.compat import ABC, basestring
from applitools.common.utils.json_utils import JsonInclude
from applitools.common.validators import is_list_or_tuple

__all__ = ("VisualLocator", "VisualLocatorSettings")

LOCATORS_TYPE = Dict[Text, List[Region]]  # typedef


def _clean_names(names):
    argument_guard.not_list_or_tuple(names)
    if len(names) == 1 and is_list_or_tuple(names[0]):
        names = names[0]
    argument_guard.are_(names, klass=basestring)
    return names


@attr.s
class VisualLocatorSettingsValues(object):
    names = attr.ib()  # type: List[Text]
    first_only = attr.ib(default=True)  # type: bool

    @property
    def is_first_only(self):
        # type: () -> bool
        return self.first_only


class VisualLocatorSettings(ABC):
    def __init__(self, *names):
        # type: (*Text) -> None
        self.values = VisualLocatorSettingsValues(names=list(names))

    def first(self):
        # type: () -> VisualLocatorSettings
        clone = self.clone()
        clone.values.first_only = True
        return clone

    def all(self):
        # type: () -> VisualLocatorSettings
        clone = self.clone()
        clone.values.first_only = False
        return clone

    def clone(self):
        # type: () -> VisualLocatorSettings
        return copy(self)

    def name(self, name):
        # type: (Text) -> VisualLocatorSettings
        argument_guard.is_a(name, basestring)
        cloned = self.clone()
        cloned.values.names.append(name)
        return cloned

    def names(self, *names):
        # type: (*Union[Text, List[Text]]) -> VisualLocatorSettings
        cleaned_names = _clean_names(names)
        cloned = self.clone()
        cloned.values.names = cleaned_names
        return cloned


class VisualLocator(ABC):
    @staticmethod
    def name(name):
        # type: (Text) -> VisualLocatorSettings
        argument_guard.is_a(name, basestring)
        return VisualLocatorSettings(name)

    @staticmethod
    def names(*names):
        # type: (*Union[Text, List[Text]]) -> VisualLocatorSettings
        return VisualLocatorSettings(*_clean_names(names))


class VisualLocatorsProvider(ABC):
    @abstractmethod
    def get_locators(self, visual_locator_settings):
        # type: (VisualLocatorSettings) -> LOCATORS_TYPE
        pass


@attr.s
class VisualLocatorsData(object):
    app_name = attr.ib(metadata={JsonInclude.THIS: True})
    image_url = attr.ib(metadata={JsonInclude.THIS: True})
    first_only = attr.ib(metadata={JsonInclude.THIS: True})
    locator_names = attr.ib(metadata={JsonInclude.THIS: True})
