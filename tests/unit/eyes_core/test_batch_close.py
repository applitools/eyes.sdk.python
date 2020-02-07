import os
from distutils.util import strtobool

import pytest
from mock import patch

from applitools.core import BatchClose


@pytest.mark.parametrize("env_dont_close", ["1", "True", "true", "false", "False"])
def test_batch_no_api_key_error(env_dont_close):
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


@patch.dict(os.environ, {"APPLITOOLS_API_KEY": "Some-key"})
def test_pass_multiple_batches_ids():
    with patch("requests.delete") as mocked_request:
        BatchClose().set_batch_ids("test-batch-id").close()
        assert "test-batch-id" in mocked_request.call_args[0][0]
        BatchClose().set_batch_ids("test-batch-id", "test-batch-second").close()
        assert "test-batch-second" in mocked_request.call_args[0][0]
        BatchClose().set_batch_ids(["test-batch-id", "test-batch-second"]).close()
        assert "test-batch-second" in mocked_request.call_args[0][0]
