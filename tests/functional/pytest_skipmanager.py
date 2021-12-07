import itertools
import os
from collections import defaultdict
from distutils.util import strtobool
from os import path

import pytest
import yaml
from six import iteritems

here = path.abspath(path.dirname(__file__))

TRAVIS_COMMIT = os.getenv("TRAVIS_COMMIT")
BUILD_TAG = os.getenv("BUILD_TAG")
RUNNING_ON_TRAVIS_REGRESSION_SUITE = TRAVIS_COMMIT and BUILD_TAG is None


if RUNNING_ON_TRAVIS_REGRESSION_SUITE:

    def pytest_collection_modifyitems(items):
        skip = pytest.mark.skip(
            reason="Skipping this test because it's fail or in skip list"
        )
        skip_tests_list = get_skip_tests_list()
        for item in items:
            if item.fspath.basename in skip_tests_list:
                if item.originalname in skip_tests_list[item.fspath.basename]:
                    if skip_tests_list[item.fspath.basename][item.originalname] is None:
                        item.add_marker(skip)
                        continue

                    if os.getenv("TEST_PLATFORM") == "Linux":
                        set_skip_for_linux_platform(item, skip_tests_list, skip)
                    if os.getenv("TEST_PLATFORM") in ["iOS", "Android"]:
                        set_skip_for_mobile_platform(item, skip_tests_list, skip)

    def get_skip_tests_list():
        result = defaultdict(dict)
        for test_file, test_dict in itertools.chain(
            get_failed_tests_from_file(), get_skip_duplicates_tests_from_file()
        ):
            for test_name, val in iteritems(test_dict):
                result[test_file][test_name] = val
        return result

    def get_failed_tests_from_file():
        with open(path.join(here, "failedTestsSuite.yaml")) as f:
            failed_tests = yaml.load(f, Loader=yaml.Loader)
            return iteritems(failed_tests)

    def get_skip_duplicates_tests_from_file():
        with open(path.join(here, "generatedTestsSuite.yaml")) as f:
            generated_tests = yaml.load(f, Loader=yaml.Loader)
            return iteritems(generated_tests)

    def set_skip_for_linux_platform(item, failed_tests, skip):
        if strtobool(os.getenv("TEST_RUN_ON_VG", "False")):
            if "VG" in failed_tests[item.fspath.basename][item.originalname][0]:
                item.add_marker(skip)
        else:
            if ("stitch_mode" in item.callspec.params) and (
                item.callspec.params["stitch_mode"].value
                in failed_tests[item.fspath.basename][item.originalname][0]
            ):
                item.add_marker(skip)
            if ("eyes_runner" in item.callspec.params) and (
                string_contains_list_element(
                    str(type(item.callspec.params["eyes_runner"])),
                    failed_tests[item.fspath.basename][item.originalname][0],
                )
            ):
                item.add_marker(skip)

    def set_skip_for_mobile_platform(item, failed_tests, skip):
        for excluded_item in failed_tests[item.fspath.basename][item.originalname]:
            if (
                item.callspec.params["mobile_eyes"]["deviceName"] in excluded_item
                and item.callspec.params["mobile_eyes"]["deviceOrientation"]
                in excluded_item
                and item.callspec.params["mobile_eyes"]["platformVersion"]
                in excluded_item
                and str(item.callspec.params["mobile_eyes"]["fully"]) in excluded_item
                and item.callspec.params["page"] in excluded_item
            ):
                item.add_marker(skip)

    def string_contains_list_element(string_check, list_check):
        for element in list_check:
            if element in string_check:
                return True
        return False
