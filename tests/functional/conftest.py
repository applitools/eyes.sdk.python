import functools
import itertools
import os
from collections import defaultdict
from distutils.util import strtobool
from os import path

import attr
import mock
import pytest
import yaml

from applitools.common import (
    BatchInfo,
    Configuration,
    JobInfo,
    MatchResult,
    RenderingInfo,
    RenderStatusResults,
    RunningRender,
    RunningSession,
    StdoutLogger,
    TestResults,
    logger,
)
from applitools.common.utils import iteritems
from applitools.common.utils.json_utils import attr_from_dict
from applitools.core import ServerConnector
from tests.utils import get_session_results, send_result_report

try:
    from contextlib import ExitStack
except ImportError:
    from contextlib2 import ExitStack

logger.set_logger(StdoutLogger(is_verbose=True))

here = path.abspath(path.dirname(__file__))

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
    return Configuration().set_save_new_tests(False)


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
        check_image_match_settings(eyes, test_result, comparision)


def check_image_match_settings(eyes, test_result, comparision):
    session_results = get_session_results(eyes.api_key, test_result)
    img = session_results["actualAppOutput"][0]["imageMatchSettings"]
    for param in comparision:
        actual = img[param["actual_name"]]
        expected = param["expected"]
        if attr.has(expected.__class__):
            actual = attr_from_dict(actual, expected.__class__)
        elif isinstance(expected, list):
            expected_cls = expected[0].__class__
            actual = [attr_from_dict(a, expected_cls) for a in actual]
        assert actual == expected


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


@pytest.fixture
def fake_connector_class():
    return FakeServerConnector


class FakeServerConnector(ServerConnector):
    def __init__(self):
        super(FakeServerConnector, self).__init__()
        self.input_calls = defaultdict(list)
        self.output_calls = defaultdict(list)
        self.running_session_result = RunningSession(
            **{
                "id": "MDAwMDANzk~",
                "session_id": "000002518",
                "batch_id": "000002518010",
                "baseline_id": "5411539b-558a-44c6-8a93-d95ddf909552",
                "is_new_session": False,
                "url": "https://eyes.applitools.com/app/batches/2124/04235423?accountId=asfd1124~~",
            }
        )
        self.test_result = TestResults(status="Passed")

    @property
    def calls(self):
        return {key: results[0] for key, results in iteritems(self.input_calls)}

    def start_session(self, session_start_info):
        self.input_calls["start_session"].append(session_start_info)
        self.output_calls["start_session"].append(self.running_session_result)
        return self.running_session_result

    def stop_session(self, running_session, is_aborted, save):
        self.input_calls["stop_session"].append((running_session, is_aborted, save))
        self.output_calls["stop_session"].append(self.test_result)
        return self.test_result

    def match_window(self, running_session, match_data):
        self.input_calls["match_window"].append((running_session, match_data))
        result = MatchResult(as_expected=True)
        self.output_calls["match_window"].append(result)
        return result

    def render(self, *render_requests):
        self.input_calls["render"].append(render_requests)
        result = [
            RunningRender(
                **{
                    "render_id": "d226bfd0-e6e0-4c5e-9651-3a844a3e9b45",
                    "job_id": "33305ec6-c03e-4fdf-8a11-bae62f3900a8",
                    "render_status": "rendering",
                }
            )
        ]
        self.output_calls["render"].append(result)
        return result

    def render_status_by_id(self, *render_ids):
        self.input_calls["render_status_by_id"].append(render_ids)
        result = [
            RenderStatusResults(
                **{
                    "image_location": "https://eyesapi.applitools.com/api/images/sti/se%-4e8e-9fd7-c01b33e47dcc?accessKey=None",
                    "status": "rendered",
                    "os": "linux",
                    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/85.0.4183.83 Safari/537.36",
                    "visual_viewport": {"width": 800, "height": 600},
                    "device_size": {"width": 800, "height": 600},
                    "retry_count": 0,
                    "dom_location": "https://eyespublicw0.blob.core/a255-se/40b1-bf12df29cd5?sv=2017-04-17&sr=c&sig=1smaTPYU27cwPZuGx9pEooNNc%3D&se=2015%3A11%3A50Z&sp=w&accessKey=None",
                    "render_id": "d226bfd0-e6e0-4c5e-9651-3a844a3e9b45",
                }
            )
        ]
        self.output_calls["render_status_by_id"].append(result)
        return result

    def render_put_resource(self, resource):
        self.input_calls["render_put_resource"].append(resource)
        self.output_calls["render_put_resource"].append(resource.hash)
        return resource.hash

    def render_info(self):
        self.input_calls["render_info"].append(True)

        result = RenderingInfo(
            **{
                "service_url": "https://render.applitools.com",
                "stitching_service_url": "https://eyesapi.applitools.com/api/images/s?accessKey=None",
                "access_token": "NYNyBxWppb1a0NvMrZXmMHqrUrdYUM",
                "results_url": "https://eyespublicwi0.blob.core/a-se/__random__?sv=2&sr=c&sig=wrasda%3D&se=09-29T10%3A12%3A13Z&sp=w&accessKey=None",
                "max_image_height": 15000,
                "max_image_area": 37500000,
            }
        )
        self.output_calls["render_info"].append(result)
        return result

    def job_info(self, render_requests):
        self.input_calls["job_info"].append(render_requests)
        result = [
            JobInfo(renderer=rr.renderer, eyes_environment=rr.browser_name)
            for rr in render_requests
        ]
        self.output_calls["job_info"].append(result)
        return result

    def check_resource_status(self, resources):
        self.input_calls["check_resource_status"].append(resources)
        result = [True for _ in resources]
        self.output_calls["check_resource_status"].append(result)
        return result

    def send_logs(self, *events):
        self.input_calls["send_logs"].append(events)

    def __deepcopy__(self, memo):
        return self


@pytest.fixture(scope="function")
def spy():
    def make_spy(obj, attribute):
        method = getattr(obj, attribute)

        @functools.wraps(method)
        def wrapped(*args, **kwargs):
            try:
                patched.return_list.append(method(*args, **kwargs))
                return patched.return_list[-1]
            except Exception as e:
                patched.raised_list.append(e)
                raise

        patched = exit_stack.enter_context(
            mock.patch.object(obj, attribute, side_effect=wrapped, autospec=True)
        )
        patched.return_list = []
        patched.raised_list = []
        return patched

    exit_stack = ExitStack()
    make_spy.ANY = mock.ANY
    make_spy.call = mock.call
    with exit_stack:
        yield make_spy
