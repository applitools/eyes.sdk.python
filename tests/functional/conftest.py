import functools
import os
from collections import defaultdict

import attr
import mock
import pytest

from applitools.common import (
    BatchInfo,
    Configuration,
    MatchResult,
    RunningSession,
    StdoutLogger,
    TestResults,
    logger,
)
from applitools.common.ultrafastgrid.render_request import RenderingInfo
from applitools.common.utils import iteritems
from applitools.common.utils.json_utils import attr_from_dict
from applitools.core import ServerConnector
from tests.utils import get_session_results

try:
    from contextlib import ExitStack
except ImportError:
    from contextlib2 import ExitStack

logger.set_logger(StdoutLogger(is_verbose=True))


pytest_plugins = (
    "tests.functional.pytest_reporting",
    "tests.functional.pytest_skipmanager",
)


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
