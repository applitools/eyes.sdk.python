from abc import ABC
from copy import copy
from typing import Text, List, Union

from applitools.common.utils import argument_guard
from applitools.common.utils.compat import basestring
from applitools.common.validators import is_list_or_tuple

__all__ = ("VisualLocator",)


class VisualLocatorSettings(ABC):
    def __init__(self, *names):
        # type: (*Text) -> None
        self._names = list(names)
        self._first_only = True

    def first(self):
        # type: () -> VisualLocatorSettings
        clone = copy(self)
        clone._first_only = True
        return clone

    def all(self):
        # type: () -> VisualLocatorSettings
        clone = copy(self)
        clone._first_only = False
        return clone

    @property
    def is_first_only(self):
        # type: () -> bool
        return self._first_only

    @property
    def names(self):
        # type: () -> List[Text]
        return self._names


class VisualLocator(ABC):
    @staticmethod
    def name(name):
        # type: (Text) -> VisualLocatorSettings
        """

        :param name:
        :return:
        """
        argument_guard.is_a(name, basestring)
        return VisualLocatorSettings(name)

    @staticmethod
    def names(*names):
        # type: (*Union[Text, List[Text]]) -> VisualLocatorSettings
        """

        :param names:
        :return:
        """
        argument_guard.not_list_or_tuple(names)
        if len(names) == 1 and is_list_or_tuple(names[0]):
            names = names[0]
        argument_guard.are_(names, klass=basestring)
        return VisualLocatorSettings(*names)
