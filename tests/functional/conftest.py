import os
from distutils.util import strtobool

import pytest

from applitools.common import BatchInfo, StdoutLogger, logger, Configuration
from applitools.common.utils import iteritems
from tests.utils import send_result_report

logger.set_logger(StdoutLogger())


@pytest.fixture(scope="session")
def eyes_runner_class():
    return lambda: None


@pytest.fixture(scope="session")
def eyes_runner(eyes_runner_class):
    runner = eyes_runner_class()
    yield runner
    if runner:
        results_summary = runner.get_all_test_results(False)
        print(results_summary)


@pytest.fixture
def eyes_config_base():
    return Configuration()


@pytest.fixture
def eyes_config(eyes_config_base):
    return eyes_config_base


@pytest.fixture
def batch_info():
    return BatchInfo(os.getenv("APPLITOOLS_BATCH_NAME", "Python SDK"))


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
