import json
import os
import sys

import requests
from pip._vendor.retrying import retry

from applitools.common.utils import urlencode, urlsplit, urlunsplit


# @retry(exception=requests.HTTPError)
def get_test_info(api_key, results):
    api_session_url = results.api_urls.session
    r = requests.get(
        "{}?format=json&AccessToken={}&apiKey={}".format(
            api_session_url, results.secret_token, api_key
        ),
        verify=False,
    )
    r.raise_for_status()
    return r.json()


def get_dom(results, dom_id):
    app_session_url = results.app_urls.session
    urlsplit_app_session_url = urlsplit(app_session_url)
    accountId = urlsplit_app_session_url.query
    url = urlunsplit(
        urlsplit_app_session_url._replace(
            path="/api/images/dom/" + dom_id + "/",
            query=accountId
            + "&"
            + urlencode(
                {
                    "apiKey": os.getenv("APPLITOOLS_API_KEY_READ", None),
                    "format": "json",
                }
            ),
        )
    )
    res = requests.get(url)
    res.raise_for_status()
    return res.json()


def getNodesByAttribute(node, attribute):
    return sum(
        (getNodesByAttribute(n, attribute) for n in node.get("childNodes", [])),
        [node] if attribute in node.get("attributes", {}) else [],
    )
