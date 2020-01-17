import json
import os
import uuid
from copy import copy

from distutils.util import strtobool
from typing import Text, Dict

import requests

from applitools.common import TestResults, logger
from applitools.common.utils import urljoin
from applitools.common.utils.json_utils import underscore_to_camelcase

REPORT_BASE_URL = "http://sdk-test-results.herokuapp.com"
REPORT_DATA = {
    "sdk": "python",
    "group": "selenium",
    "id": os.getenv("TRAVIS_COMMIT", str(uuid.uuid4())),
    "sandbox": bool(strtobool(os.getenv("SANDBOX", "True"))),
    "mandatory": False,
    "results": [
        # {
        #     "test_name": "TestDuplicatedIFrames",
        #     "parameters": {"browser": "chrome", "stitching": "css"},
        #     "passed": True,
        # },
    ],
}


def prepare_result_data_for_makereport(test_name, passed):
    test_name = underscore_to_camelcase(test_name)
    return dict(test_name=test_name, passed=passed)


def prepare_result_data_for_runner(test_name, passed, browser):
    stitching = "css"
    if test_name.endswith("_Scroll"):
        test_name = test_name.rstrip("_Scroll")
        stitching = "scroll"
    parameters = dict(browser=browser, stitching=stitching)

    if test_name.endswith("_VG"):
        test_name = test_name.rstrip("_VG")
        parameters = dict(mode="VisualGrid")
    return dict(test_name=test_name, passed=passed, parameters=parameters)


def send_result_report(results, group="selenium"):
    report_data = copy(REPORT_DATA)
    report_data["results"] = results
    report_data["group"] = group
    r = requests.post(urljoin(REPORT_BASE_URL, "/result"), data=json.dumps(report_data))
    print("Result report send: {} - {}".format(r.status_code, r.text))
    return r


def get_session_results(api_key, results):
    # type: (Text, TestResults) -> Dict
    api_session_url = results.api_urls.session
    resp = requests.get(
        "{}?format=json&AccessToken={}&apiKey={}".format(
            api_session_url, results.secret_token, api_key
        ),
        verify=False,
    )
    return resp.json()
