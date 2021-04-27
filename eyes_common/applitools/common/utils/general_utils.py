from __future__ import absolute_import

import hashlib
import inspect
import os
import random
import typing
from string import ascii_lowercase, ascii_uppercase, digits

import attr

from .compat import parse_qs, urlencode, urlsplit, urlunsplit

"""
General purpose utilities.
"""


if typing.TYPE_CHECKING:
    from typing import Any, Callable, List, Optional, Text

    T = typing.TypeVar("T")


def random_alphanum(n):
    return "".join(
        random.choice(ascii_uppercase + ascii_lowercase + digits) for _ in range(n)
    )


def use_default_if_none_factory(default_obj, obj):
    def default(attr_name):
        val = getattr(obj, attr_name)
        if val is None:
            return getattr(default_obj, attr_name)
        return val

    return default


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


def get_sha256_hash(content):
    return hashlib.sha256(content).hexdigest()


def set_query_parameter(url, param_name, param_value):
    """Given a URL, set or replace a query parameter and return the
    modified URL.

    >>> set_query_parameter('http://example.com?foo=bar&biz=baz', 'foo', 'stuff')
    'http://example.com?foo=stuff&biz=baz'

    """
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)

    query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)

    return urlunsplit((scheme, netloc, path, new_query_string, fragment))


def proxy_to(proxy_obj_name, fields=None):
    # type: (Text, Optional[List[Text]]) -> Callable
    """
    Adds to decorated class __getter__ and __setter__ methods that allow to access
    attributes from proxy_object in the parent class.

    :param proxy_obj_name: The name of the proxy object that has decorated class.
    :param fields:
        Fields which should be accessible in parent object from the proxy object.
    """

    def __getattr__(self, name):
        _fields = fields or self._proxy_to_fields or []
        if name in _fields:
            proxy_obj = getattr(self, proxy_obj_name)
            return getattr(proxy_obj, name)
        module_with_class = "{}::{}".format(
            inspect.getfile(self.__class__), self.__class__.__name__
        )
        raise AttributeError("{} has not attr `{}`".format(module_with_class, name))

    def _setattr(cls):
        def __setattr__(self, key, value):
            _fields = fields or self._proxy_to_fields or []
            if key in _fields:
                proxy_obj = getattr(self, proxy_obj_name)
                setattr(proxy_obj, key, value)
            elif self.__class__ is cls:
                # if current class is the same that we've decorated
                super(self.__class__, self).__setattr__(key, value)
            else:
                # to prevent recursion error if not the current class is decorated one
                self.__dict__[key] = value

        return __setattr__

    def __dir__(self):
        _fields = fields or self._proxy_to_fields or []
        origin_fields = dir(self.__class__)
        return list(origin_fields) + _fields

    def dec(cls):
        cls._proxy_to_fields = None
        cls.__getattr__ = __getattr__
        cls.__setattr__ = _setattr(cls)
        cls.__dir__ = __dir__
        return cls

    return dec


def all_fields(obj):
    # type: (Any) -> List[Text]
    """Get all public fields from the object

    Args:
        obj: any kind object

    Returns:
        list of attributes and methods names
    """
    if attr.has(obj):
        return list(attr.fields_dict(obj).keys())
    else:
        return [f for f in vars(obj) if not f.startswith("_")]


def all_attrs(obj):
    # type: (Any) -> List[Text]
    """Get all public attributes from the object. Methods and fields.

    Args:
        obj: any kind object

    Returns:
        list of attributes and methods names
    """
    return [f for f in dir(obj) if not f.startswith("_")]


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


def counted(f):
    """
    Decorator that tracks how many times the function is called
    """

    def wrapped(*args, **kwargs):
        wrapped.calls += 1
        return f(*args, **kwargs)

    wrapped.calls = 0
    return wrapped


class DynamicEnumGetter(object):
    """
    Allow to use methods as values in Enum classes
    """

    def __init__(self, fget=None):
        self.fget = fget
        self.__doc__ = fget.__doc__

    def __get__(self, instance, ownerclass=None):
        return self.fget(ownerclass)
