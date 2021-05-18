import json
import os
import uuid
from copy import copy
from distutils.util import strtobool
from os import path

import pytest
import requests

from applitools.common.utils import urljoin
from applitools.common.utils.datetime_utils import retry
from applitools.common.utils.json_utils import underscore_to_camelcase

REPORT_BASE_URL = "http://sdk-test-results.herokuapp.com"
REPORT_DATA = {
    "sdk": "python",
    "group": "selenium",
    "id": os.getenv("TRAVIS_COMMIT", str(uuid.uuid4())),
    "sandbox": bool(strtobool(os.getenv("TEST_REPORT_SANDBOX", "True"))),
    "mandatory": False,
    "results": [],
}
TESTS_DIR = path.dirname(path.abspath(__file__))


def prepare_result_data(test_name, passed, parameters):
    test_name = underscore_to_camelcase(test_name)
    result = dict(test_name=test_name, passed=passed)
    if parameters:
        result["parameters"] = parameters
    params_index_start = test_name.find("[")
    if params_index_start == -1:
        return result

    test_params = test_name[params_index_start + 1 : -1]
    test_name = test_name[:params_index_start]
    if test_params.find("StitchMode") == -1:
        # if not desktop tests
        result["test_name"] = test_name
        return result

    browser = "Chrome"
    if test_params.find("chrome") == -1:
        browser = "Firefox"
    stitching = "css"
    if test_params.find("CSS") == -1:
        stitching = "scroll"
    return dict(
        test_name=test_name,
        passed=passed,
        parameters=dict(browser=browser, stitching=stitching),
    )


@retry(exception=requests.HTTPError)
def send_result_report(test_name, passed, parameters=None, group="selenium"):
    report_data = copy(REPORT_DATA)
    report_data["results"] = [prepare_result_data(test_name, passed, parameters)]
    report_data["group"] = group
    r = requests.post(urljoin(REPORT_BASE_URL, "/result"), data=json.dumps(report_data))
    r.raise_for_status()
    print("Result report send: {} - {}".format(r.status_code, r.text))
    return r


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()
    if result.when == "setup":
        # skip tests on setup stage and if skipped
        return

    passed = result.outcome == "passed"
    group = "selenium"
    test_name = item.name
    parameters = None
    if result.when == "call":
        # For tests where eyes.close() inside test body
        if not (
            item.fspath.dirname.endswith("eyes_images")
            or item.fspath.dirname.endswith("selenium")
            or item.fspath.purebasename == "test_mobile"
        ):
            return

        # if eyes_images tests
        if item.fspath.dirname.endswith("eyes_images"):
            group = "images"
        # if eyes_selenium/mobile/test_mobile.py
        if item.fspath.purebasename == "test_mobile":
            test_name = item.originalname
            (
                device_name,
                platform_version,
                device_orientation,
                page,
            ) = item.callspec.id.split("-")
            parameters = dict(
                device_name=device_name,
                platform_version=platform_version,
                device_orientation=device_orientation,
                page=page,
            )
        send_result_report(
            test_name=test_name, passed=passed, parameters=parameters, group=group
        )
    elif result.when == "teardown":
        # For tests where eyes.close() inside fixture
        if not (
            item.fspath.dirname.endswith("visual_grid")
            or item.fspath.dirname.endswith("desktop")
        ):
            return

        if strtobool(os.getenv("TEST_RUN_ON_VG", "False")):
            test_name = item.originalname
            parameters = dict(mode="VisualGrid")
        send_result_report(
            test_name=test_name, passed=passed, parameters=parameters, group=group
        )
