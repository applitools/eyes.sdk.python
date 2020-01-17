import os

import pytest

from applitools.common import BatchInfo, StdoutLogger, logger, Configuration
from applitools.common.utils import iteritems
from tests.utils import (
    prepare_result_data_for_runner,
    send_result_report,
)

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
        results = [
            prepare_result_data_for_runner(
                trc.test_results.name,
                trc.test_results.is_passed,
                trc.test_results.host_app.lower(),
            )
            for trc in results_summary
        ]
        send_result_report(results, group="selenium")
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
