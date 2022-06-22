import pytest
from mock import Mock, call

from applitools.eyes_universal.server import SDKServer


@pytest.fixture
def popen_mock(monkeypatch):
    popen_mock = Mock()

    def constructor(_, stdout):
        stdout.write(b"123\n")
        return popen_mock

    monkeypatch.setattr("applitools.eyes_universal.server.Popen", constructor)
    return popen_mock


def test_sdk_server_parses_port(popen_mock):
    server = SDKServer()

    assert server.port == 123


def test_sdk_server_terminates(popen_mock):
    server = SDKServer()
    server.close()

    assert popen_mock.mock_calls == [call.terminate(), call.wait()]


def test_sdk_server_deletes(popen_mock):
    SDKServer()

    assert popen_mock.mock_calls == [call.terminate(), call.wait()]
