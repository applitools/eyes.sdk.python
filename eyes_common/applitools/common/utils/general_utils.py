from __future__ import absolute_import

import hashlib
import itertools
import time
import typing

from applitools.common import logger

from .compat import parse_qs, urlencode, urlparse, urlsplit, urlunsplit

"""
General purpose utilities.
"""


if typing.TYPE_CHECKING:
    from typing import Callable, Any, List, Text

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


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        if "log_time" in kw:
            name = kw.get("log_name", method.__name__.upper())
            kw["log_time"][name] = int((te - ts) * 1000)
        else:
            logger.debug("%r  %2.2f ms" % (method.__name__, (te - ts) * 1000))
        return result

    return timed


def retry(delays=(0, 1, 5), exception=Exception, report=lambda *args: None):
    """
    This is a Python decorator which helps implementing an aspect oriented
    implementation of a retrying of certain steps which might fail sometimes.
    https://code.activestate.com/recipes/580745-retry-decorator-in-python/
    """

    def wrapper(function):
        def wrapped(*args, **kwargs):
            problems = []
            for delay in itertools.chain(delays, [None]):
                try:
                    return function(*args, **kwargs)
                except exception as problem:
                    problems.append(problem)
                    if delay is None:
                        report("retryable failed definitely:", problems)
                        raise
                    else:
                        report(
                            "retryable failed:", problem, "-- delaying for %ds" % delay
                        )
                        time.sleep(delay)

        return wrapped

    return wrapper


def get_sha256_hash(content):
    m = hashlib.sha256()
    m.update(content)
    return "".join(["%02x" % b for b in m.digest()])


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
