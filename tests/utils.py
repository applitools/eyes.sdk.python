import json
from copy import copy
from os import path
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Text

import attr
import requests

from applitools.common import TestResults
from applitools.common.utils.datetime_utils import retry
from applitools.common.utils.json_utils import (
    _cleaned_dict_from_attrs,
    _to_serializable,
)

if TYPE_CHECKING:
    from http.cookiejar import CookieJar

    from applitools.common.utils.custom_types import AnyWebDriver


TESTS_DIR = path.dirname(path.abspath(__file__))


@retry(exception=requests.HTTPError)
def get_session_results(api_key, results):
    # type: (Text, TestResults) -> Dict
    api_session_url = results.api_urls.session
    r = requests.get(
        "{}?format=json&AccessToken={}&apiKey={}".format(
            api_session_url, results.secret_token, api_key
        ),
        verify=False,
    )
    r.raise_for_status()
    return r.json()


def get_resource_path(name):
    resource_dir = path.join(TESTS_DIR, "resources")
    return path.join(resource_dir, name)


def get_resource(name):
    pth = get_resource_path(name)
    with open(pth, "rb") as f:
        return f.read()


def update_browser_cookies(cookies, required_domain, driver):
    # type: (CookieJar, Text, AnyWebDriver) -> None
    """Helps to reuse existing cookies with webdriver"""
    from selenium.common.exceptions import (
        InvalidCookieDomainException,
        UnableToSetCookieException,
    )

    def dict_from_cookie(obj):
        d = {n: v for n, v in vars(obj).items() if not n.startswith("_")}
        d["secure"] = bool(d.get("secure", False))
        return d

    prev_url = None
    for cookie in cookies:
        if not cookie.domain.endswith(required_domain):
            continue
        next_url = "https://" + cookie.domain.lstrip(".")
        if next_url != prev_url:
            driver.get(next_url)
            prev_url = next_url
        try:
            driver.add_cookie(dict_from_cookie(cookie))
        except (UnableToSetCookieException, InvalidCookieDomainException):
            print(cookie)


def _to_json(val, params):
    # type: (Any, List) -> Text
    def __to_serializable(val):
        if isinstance(val, ModuleType):
            return val.__name__
        elif attr.has(val.__class__):
            obj = _cleaned_dict_from_attrs(val)
            if obj:
                return obj
            if params:
                return {name: getattr(obj, name) for name in params}
            return str(val)
        # print names of all custom classes
        elif val.__class__.__name__ != "type":
            return val.__class__.__name__
        return _to_serializable(val, with_attrs=False)

    return json.dumps(val, default=__to_serializable, sort_keys=True)


def parametrize_ids(parameters_ids, specify_to_display=None):
    # type: (Text, Optional[Text]) -> Callable
    """Allow to display pytest.mark.parametrize ids as json"""
    ids = parameters_ids.split(",")
    params = specify_to_display.split(",") if specify_to_display else []

    idgen = iter(ids)
    res = {}

    def wrap(value):
        res[next(idgen)] = value
        if len(res) == len(ids):
            return _to_json(res, params)

    return wrap
