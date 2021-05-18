from os import path
from typing import TYPE_CHECKING, Dict, Text

import requests

from applitools.common import TestResults
from applitools.common.utils.datetime_utils import retry

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
