import os

import requests
from six.moves.urllib.parse import urlencode, urlsplit, urlunsplit


def get_test_info(api_key, results):
    api_session_url = results.api_urls.session
    r = requests.get(
        "{}?format=json&AccessToken={}&apiKey={}".format(
            api_session_url, results.secret_token, api_key
        ),
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
                {"apiKey": os.getenv("APPLITOOLS_API_KEY_READ", None), "format": "json"}
            ),
        )
    )
    res = requests.get(url)
    res.raise_for_status()
    return res.json()


def getNodesByAttribute(node, attribute):
    nodes = [node] if attribute in node.get("attributes", {}) else []
    for n in node.get("childNodes", []):
        nodes.extend(getNodesByAttribute(n, attribute))
    return nodes
