from mock import ANY, call, patch

from applitools.common import ProxySettings
from applitools.core import BatchClose


def test_pass_multiple_batches_ids(monkeypatch):
    monkeypatch.setenv("APPLITOOLS_API_KEY", "abc")
    with patch("applitools.selenium.command_executor.CommandExecutor") as commands:
        BatchClose().set_batch_ids("test batch-id", "test-batch-second").close()
        assert commands.mock_calls == [
            call.get_instance("eyes.sdk.python", ANY),
            call.get_instance().core_close_batches(
                {
                    "batchIds": ["test batch-id", "test-batch-second"],
                    "serverUrl": "https://eyesapi.applitools.com",
                    "apiKey": "abc",
                }
            ),
        ]


def test_batch_close_uses_proxy():
    with patch("applitools.selenium.command_executor.CommandExecutor") as commands:
        BatchClose().set_batch_ids("test-id").set_proxy(
            ProxySettings("localhost", 80)
        ).close()
        assert commands.mock_calls == [
            call.get_instance("eyes.sdk.python", ANY),
            call.get_instance().core_close_batches(
                {
                    "batchIds": ["test-id"],
                    "serverUrl": "https://eyesapi.applitools.com",
                    "apiKey": ANY,
                    "proxy": {"url": "http://localhost:80"},
                }
            ),
        ]
