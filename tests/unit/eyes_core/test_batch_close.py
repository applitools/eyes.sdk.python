import os
from distutils.util import strtobool

import pytest
from mock import ANY, call, patch

from applitools.common import ProxySettings
from applitools.core import BatchClose
from applitools.selenium import ClassicRunner, VisualGridRunner


@pytest.mark.parametrize("env_dont_close", ["1", "True", "true", "false", "False"])
def test_batch_closes_with_dont_closes_env(env_dont_close):
    with patch.dict(
        os.environ,
        {
            "APPLITOOLS_API_KEY": "Some-key",
            "APPLITOOLS_DONT_CLOSE_BATCHES": env_dont_close,
        },
    ):
        with patch("requests.delete") as mocked_request:
            BatchClose().set_batch_ids("test-batch-id").close()
            if strtobool(env_dont_close):
                assert not mocked_request.called
            else:
                assert mocked_request.call_args[0][0]


@pytest.mark.parametrize("dont_close_batches", [True, False])
@pytest.mark.parametrize("runner_cls", [ClassicRunner, lambda: VisualGridRunner(1)])
def test_batch_closes_with_dont_closes_in_runner(dont_close_batches, runner_cls):
    runner = runner_cls()
    runner.set_dont_close_batches(dont_close_batches)

    with patch.dict(
        os.environ,
        {
            "APPLITOOLS_API_KEY": "Some-key",
        },
    ):
        with patch("requests.delete") as mocked_request:
            BatchClose().set_batch_ids("test-batch-id").close()
            if dont_close_batches:
                assert not mocked_request.called
            else:
                assert mocked_request.call_args[0][0]


@patch.dict(os.environ, {"APPLITOOLS_API_KEY": "Some-key"})
def test_pass_multiple_batches_ids():
    with patch("requests.delete") as mocked_request:
        BatchClose().set_batch_ids("test batch-id").close()
        assert "test+batch-id" in mocked_request.call_args[0][0]
        BatchClose().set_batch_ids("test-batch-id", "test-batch//@second").close()
        assert "test-batch%2F%2F%40second" in mocked_request.call_args[0][0]
        BatchClose().set_batch_ids(["test-batch-id", "test-batch-second"]).close()
        assert "test-batch-second" in mocked_request.call_args[0][0]


def test_batch_close_uses_proxy():
    with patch("requests.delete") as mocked_request:
        BatchClose().set_batch_ids("test-id").set_proxy(
            ProxySettings("localhost", 80)
        ).close()
        assert mocked_request.call_args_list == [
            call(
                ANY,
                params={"apiKey": ANY},
                verify=False,
                proxies={"http": "http://localhost:80", "https": "http://localhost:80"},
            )
        ]
