from os import path
from typing import Dict, Text

import requests

from applitools.common import TestResults

TESTS_DIR = path.dirname(path.abspath(__file__))


def get_session_results(api_key, results):
    # type: (Text, TestResults) -> Dict
    api_session_url = results.api_urls.session
    r = requests.get(
        "{}?format=json&AccessToken={}&apiKey={}".format(
            api_session_url, results.secret_token, api_key
        ),
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
