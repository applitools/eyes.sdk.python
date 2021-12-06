import functools
import json
import os

import attr
import mock
import pytest

from applitools.common import BatchInfo, Configuration, StdoutLogger, logger
from applitools.common.utils import iteritems
from applitools.common.utils.json_utils import attr_from_json
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
            actual = attr_from_json(json.dumps(actual), expected.__class__)
        elif isinstance(expected, list):
            expected_cls = expected[0].__class__
            actual = [attr_from_json(json.dumps(a), expected_cls) for a in actual]
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
