import json
import os
import platform
import sys
import uuid
from copy import copy
from distutils.util import strtobool
from json import JSONDecoder

import pytest
import requests

from applitools.common.utils import iteritems, urljoin
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


@retry(exception=requests.HTTPError)
def send_result_report(tests, group):
    report_data = copy(REPORT_DATA)
    report_data["results"] = tests
    report_data["group"] = group
    r = requests.post(urljoin(REPORT_BASE_URL, "/result"), data=json.dumps(report_data))
    r.raise_for_status()
    print("Result report send: {} - {}".format(r.status_code, r.text))
    return r


@pytest.hookimpl(hookwrapper=True)
def pytest_terminal_summary(terminalreporter):
    yield
    # special check for pytest-xdist plugin, cause we do not want to send report for each worker.
    if hasattr(terminalreporter.config, "workerinput"):
        return

    passed_tests = terminalreporter.stats.get("passed", [])
    failed_tests = terminalreporter.stats.get("failed", [])
    result = _prepare_tests_data(passed_tests + failed_tests)
    for group, tests in iteritems(result):
        if tests:
            send_result_report(tests, group)


def _select_group(item):
    full_test_path = item.fspath
    test_dir_path_full = os.path.dirname(full_test_path)
    if len(test_dir_path_full.split("/")) <= 3:
        test_dir_path_base = test_dir_path_full
    else:
        test_dir_path_base = "/".join(test_dir_path_full.split("/")[:3])

    if test_dir_path_base in ["tests/functional/eyes_images"]:
        return "images"
    elif test_dir_path_base in [
        "tests/functional/eyes_selenium",
    ]:
        if test_dir_path_full.endswith("mobile"):
            return "appium"
        return "selenium"
    elif test_dir_path_base in [
        "tests/unit",
        "tests/unit/eyes_core",
        "tests/unit/eyes_common",
    ]:
        return "core"
    elif full_test_path.endswith("test_integration.py"):
        return "core"
    raise ValueError("Incorrect group: {}".format(item))


def _extract_json_objects(text, decoder=JSONDecoder()):
    """Find JSON objects in text, and yield the decoded JSON data

    Does not attempt to look for JSON arrays, text, or other JSON types outside
    of a parent JSON object.

    """
    pos = 0
    while True:
        match = text.find("{", pos)
        if match == -1:
            break
        try:
            result, index = decoder.raw_decode(text[match:])
            yield result
            pos = match + index
        except ValueError:
            pos = match + 1


def _prepare_tests_data(items):
    group_results = {
        "core": [],
        "selenium": [],
        "images": [],
        "appium": [],
    }
    for item in items:
        passed = item.outcome == "passed"
        parameters = {}

        try:
            test_name, test_params = item.location[2].split("[")
            for obj in _extract_json_objects(test_params):
                parameters.update(obj)
        except ValueError:
            test_name, test_params = item.location[2], None
        test_dir_path = os.path.dirname(item.fspath)
        if test_dir_path.endswith("visual_grid"):
            parameters["mode"] = "VisualGrid"

        group_results[_select_group(item)].append(
            dict(
                test_name=underscore_to_camelcase(test_name),
                passed=passed,
                parameters=parameters,
            )
        )
    return group_results
