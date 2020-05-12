import os
from distutils.util import strtobool

import pytest
import yaml

from applitools.common import BatchInfo, StdoutLogger, logger, Configuration, StitchMode
from applitools.common.utils import iteritems
from tests.utils import send_result_report, get_session_results

logger.set_logger(StdoutLogger())

TRAVIS_COMMIT = os.getenv("TRAVIS_COMMIT")
BUILD_TAG = os.getenv("BUILD_TAG")
RUNNING_ON_TRAVIS_REGRESSION_SUITE = TRAVIS_COMMIT and BUILD_TAG is None


@pytest.fixture(scope="session")
def eyes_runner_class():
    return lambda: None


@pytest.fixture(scope="session")
def eyes_runner(eyes_runner_class):
    runner = eyes_runner_class()
    yield runner
    if runner:
        print(runner.get_all_test_results(False))


@pytest.fixture
def eyes_config_base():
    return Configuration()


@pytest.fixture
def eyes_config(eyes_config_base):
    return eyes_config_base


@pytest.fixture(scope="session")
def batch_info():
    return BatchInfo(os.getenv("APPLITOOLS_BATCH_NAME", "Python SDK"))


def check_test_result_(eyes):
    while True:
        comparision = yield
        test_result = yield
        session_results = get_session_results(eyes.api_key, test_result)
        img = session_results["actualAppOutput"][0]["imageMatchSettings"]
        for param in comparision:
            assert img[param["actual_name"]] == param["expected"]


@pytest.fixture(scope="function")
def check_test_result(eyes):
    g = check_test_result_(eyes)
    next(g)
    yield g


@pytest.fixture(name="eyes", scope="function")
def eyes_setup(request, eyes_class, eyes_config, eyes_runner, batch_info):
    # TODO: allow to setup logger level through pytest option
    # logger.set_logger(StdoutLogger())
    # in case eyes-images
    eyes = eyes_class()
    if eyes_runner:
        eyes = eyes_class(eyes_runner)

    # configure eyes options through @pytest.mark.eyes_config() marker
    config_mark_opts = request.node.get_closest_marker("eyes_config")
    config_mark_opts = config_mark_opts.kwargs if config_mark_opts else {}

    for key, val in iteritems(config_mark_opts):
        setattr(eyes_config, key, val)

    eyes.set_configuration(eyes_config)
    eyes.add_property("Agent ID", eyes.full_agent_id)

    yield eyes
    eyes.abort()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()
    if result.when == "setup" or not result.caplog:
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


if RUNNING_ON_TRAVIS_REGRESSION_SUITE:

    def pytest_collection_modifyitems(items):
        skip = pytest.mark.skip(reason="Skipping this test because it's still fail")
        failed_tests = get_failed_tests_from_file()
        for item in items:
            if item.fspath.basename in failed_tests:
                if item.originalname in failed_tests[item.fspath.basename]:
                    if failed_tests[item.fspath.basename][item.originalname] is None:
                        item.add_marker(skip)
                        continue

                    if os.getenv("TEST_PLATFORM") == "Linux":
                        set_skip_for_linux_platform(item, failed_tests, skip)
                    if os.getenv("TEST_PLATFORM") in ["iOS", "Android"]:
                        set_skip_for_mobile_platform(item, failed_tests, skip)

    def get_failed_tests_from_file():
        with open("tests/functional/resources/failedTestsSuite.yaml") as f:
            failed_tests = yaml.load(f, Loader=yaml.Loader)
            return failed_tests

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
