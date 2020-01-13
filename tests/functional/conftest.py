import json
import os
import uuid
from distutils.util import strtobool
from urllib.parse import urljoin

import pytest
import requests

from applitools.common import BatchInfo, StdoutLogger, logger, Configuration
from applitools.common.utils import iteritems

logger.set_logger(StdoutLogger())

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


@pytest.fixture(scope="session")
def eyes_runner_class():
    return lambda: None


@pytest.fixture(scope="session")
def eyes_runner(eyes_runner_class):
    runner = eyes_runner_class()
    yield runner
    if runner:
        all_results = runner.get_all_test_results(False)
        for trc in all_results:
            passed = trc.test_results.is_passed
            test_name = trc.test_results.name
            browser = trc.test_results.host_app.lower()
            stitching = "css"
            if test_name.endswith("_Scroll"):
                test_name = test_name.rstrip("_Scroll")
                stitching = "scroll"
            parameters = dict(browser=browser, stitching=stitching)

            if test_name.endswith("_VG"):
                test_name = test_name.rstrip("_Scroll")
                parameters = dict(mode="VisualGrid")

            REPORT_DATA["results"].append(
                dict(test_name=test_name, passed=passed, parameters=parameters)
            )
        r = requests.post(
            urljoin(REPORT_BASE_URL, "/result"), data=json.dumps(REPORT_DATA)
        )
        print(all_results)
        print("Report status: {}".format(r.status_code))
        print("Response: {}".format(r.text))


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
