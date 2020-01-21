from __future__ import absolute_import

import hashlib
import os
import typing

import attr

from .compat import parse_qs, urlencode, urlparse, urlsplit, urlunsplit

"""
General purpose utilities.
"""


if typing.TYPE_CHECKING:
    from typing import Callable, Any, List, Text, Optional

    T = typing.TypeVar("T")


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


def is_absolute_url(url):
    return bool(urlparse(url).netloc)


def is_url_with_scheme(url):
    return bool(urlparse(url).scheme)


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


def proxy_to(proxy_obj_name, fields):
    # type: (Text, List[Text]) -> Callable
    """
    Adds to decorated class __getter__ and __setter__ methods that allow to access
    attributes from proxy_object in the parent class

    :param proxy_obj_name: The name of the proxy object that has decorated class.
    :param fields:
        Fields which should be accessible in parent object from the proxy object.
    """

    def __getattr__(self, name):
        if name in fields:
            proxy_obj = getattr(self, proxy_obj_name)
            return getattr(proxy_obj, name)
        raise AttributeError("{} has not attr {}".format(self.__class__.__name__, name))

    def __setattr__(self, key, value):
        if key in fields:
            proxy_obj = getattr(self, proxy_obj_name)
            setattr(proxy_obj, key, value)
        else:
            super(self.__class__, self).__setattr__(key, value)

    def dec(cls):
        cls.__getattr__ = __getattr__
        cls.__setattr__ = __setattr__
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
    return []


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
