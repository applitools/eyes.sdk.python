from __future__ import absolute_import

import hashlib
import itertools
import json
import re
import time
import types
import typing
from datetime import timedelta, tzinfo

import attr

from applitools.common import logger

from .compat import iteritems, urlparse

"""
General purpose utilities.
"""


if typing.TYPE_CHECKING:
    from typing import Union, Callable, Any, Dict, List
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement
    from selenium.webdriver.remote.switch_to import SwitchTo

    from applitools.selenium.webdriver import EyesWebDriver, _EyesSwitchTo
    from applitools.selenium.webelement import EyesWebElement

    T = typing.TypeVar("T")


class _UtcTz(tzinfo):
    """
    A UTC timezone class which is tzinfo compliant.
    """

    _ZERO = timedelta(0)

    def utcoffset(self, dt):
        return _UtcTz._ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return _UtcTz._ZERO


# Constant representing UTC
UTC = _UtcTz()


def underscore_to_camelcase(text):
    return re.sub(r"(?!^)_([a-zA-Z])", lambda m: m.group(1).upper(), text)


def camelcase_to_underscore(text):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def change_case_of_keys(d, to_camel=False, to_underscore=False):
    # type: (dict, bool, bool)->dict
    if to_camel:
        func = underscore_to_camelcase
    elif to_underscore:
        func = camelcase_to_underscore
    else:
        raise ValueError("One of options should be selected. [to_camel|to_underscore]")
    new = {}
    for k, v in iteritems(d):
        if isinstance(v, dict):
            v = change_case_of_keys(v, to_camel, to_underscore)
        if v and isinstance(v, list):
            new_list = []
            for region in v[:]:
                if isinstance(region, dict):
                    new_list.append({func(k1): v1 for k1, v1 in iteritems(region)})
            v = new_list
        new[func(k)] = v
    return new


def to_json(obj, keys_to_camel_case=True):
    # type: (Any, bool) -> str
    """
    Returns an object's json representation of attrs based classes.
    """
    # TODO: Convert Enums to text
    d = attr.asdict(obj, filter=lambda a, _: not a.name.startswith("_"))
    if keys_to_camel_case:
        d = change_case_of_keys(d, to_camel=True)
    return json.dumps(d)


def use_default_if_none_factory(default_obj, obj):
    def default(attr_name):
        val = getattr(obj, attr_name)
        if val is None:
            return getattr(default_obj, attr_name)
        return val

    return default


def create_proxy_property(property_name, target_name, is_settable=False):
    # type: (str, str, bool) -> property
    """
    Returns a property object which forwards "name" to target.

    :param property_name: The name of the property.
    :param target_name: The target to forward to.
    """

    # noinspection PyUnusedLocal
    def _proxy_get(self):
        # type: (Any) -> Dict[str, float]
        return getattr(getattr(self, target_name), property_name)

    # noinspection PyUnusedLocal
    def _proxy_set(self, val):
        return setattr(getattr(self, target_name), property_name, val)

    if not is_settable:
        return property(_proxy_get)
    else:
        return property(_proxy_get, _proxy_set)


def create_forwarded_method(
    from_,  # type: Union[EyesWebDriver, EyesWebElement, _EyesSwitchTo]
    to,  # type: Union[WebDriver, WebElement, SwitchTo]
    func_name,  # type: str
):
    # type: (...) -> Callable
    """
    Returns a method(!) to be set on 'from_', which activates 'func_name' on 'to'.

    :param from_: Source.
    :param to: Destination.
    :param func_name: The name of function to activate.
    :return: Relevant method.
    """

    # noinspection PyUnusedLocal
    def forwarded_method(self_, *args, **kwargs):
        # type: (EyesWebDriver, *Any, **Any) -> Callable
        return getattr(to, func_name)(*args, **kwargs)

    return types.MethodType(forwarded_method, from_)


def create_proxy_interface(
    from_,  # type: Union[EyesWebDriver, EyesWebElement, _EyesSwitchTo]
    to,  # type: Union[WebDriver, WebElement, SwitchTo]
    ignore_list=None,  # type: List[str]
    override_existing=False,  # type: bool
):
    # type: (...) -> None
    """
    Copies the public interface of the destination object, excluding names in the
    ignore_list, and creates an identical interface in 'eyes_core',
    which forwards calls to dst.

    :param from_: Source.
    :param to: Destination.
    :param ignore_list: List of names to ignore while copying.
    :param override_existing: If False, attributes already existing in 'eyes_core'
                              will not be overridden.
    """
    if not ignore_list:
        ignore_list = []
    for attr_name in dir(to):
        if not attr_name.startswith("_") and attr_name not in ignore_list:
            if callable(getattr(to, attr_name)):
                if override_existing or not hasattr(from_, attr_name):
                    setattr(
                        from_, attr_name, create_forwarded_method(from_, to, attr_name)
                    )


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
    m.update(content.encode("utf-8"))
    return "".join(["%02x" % b for b in m.digest()])


def json_response_to_attrs_class(dct, cls):
    """
    Change case of `dct` keys to snake_case. Map existing keys in `dct` and `cls` and
    initialize `cls` by `dct` data.

    :param dct: dict with camelCase keys
    :param cls: class created by attrs
    :return: class instance
    """
    fields = [f.name for f in attr.fields(cls)]
    parsed_response = change_case_of_keys(dct, to_underscore=True)
    params = {k: v for k, v in iteritems(parsed_response) if k in fields}
    return cls(**params)
