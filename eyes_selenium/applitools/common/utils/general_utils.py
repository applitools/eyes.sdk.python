from __future__ import absolute_import

import os
import typing

"""
General purpose utilities.
"""


if typing.TYPE_CHECKING:
    from typing import Any, Callable, List, Optional, Text

    T = typing.TypeVar("T")


def cached_property(f):
    # type: (Callable) -> Any
    """
    Returns a cached property that is calculated by function f
    """

    def get(self):
        try:
            return self._property_cache[f]
        except AttributeError:
            self._property_cache = {}
            x = self._property_cache[f] = f(self)
            return x
        except KeyError:
            x = self._property_cache[f] = f(self)
            return x

    return property(get)


def get_env_with_prefix(env_name, default=None):
    # type: (Text, Optional[Text]) -> Optional[Text]
    """
    Takes name of ENV variable, check if exists origin and with list of prefixes
    """
    prefixes_to_check = ["bamboo"]
    try:
        return os.environ[env_name]
    except KeyError:
        for prefix in prefixes_to_check:
            name = "{}_{}".format(prefix, env_name)
            value = os.getenv(name)
            if value:
                return value
    return default


class DynamicEnumGetter(object):
    """
    Allow to use methods as values in Enum classes
    """

    def __init__(self, fget=None):
        self.fget = fget
        self.__doc__ = fget.__doc__

    def __get__(self, instance, ownerclass=None):
        return self.fget(ownerclass)
