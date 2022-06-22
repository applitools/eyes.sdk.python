from unittest.mock import MagicMock

import pytest
from mock import Mock, call

from applitools.eyes_universal.server import SDKServer


@pytest.fixture
def popen_mock(monkeypatch):
    popen_mock = Mock()

    def constructor(_, stdout):
        stdout.write(b"1\n")
        return popen_mock

    monkeypatch.setattr("applitools.eyes_universal.server.Popen", constructor)
    return popen_mock


@pytest.fixture
def tempfile_mock(monkeypatch):
    temp_mock = MagicMock()
    temp_mock.readline.return_value = b"2\n"

    def constructor(_):
        return temp_mock

    monkeypatch.setattr("applitools.eyes_universal.server.TemporaryFile", constructor)
    return temp_mock


def test_sdk_server_parses_port_and_terminates(popen_mock):
    server = SDKServer()
    saved_port = server.port
    server.close()

    assert saved_port == 1
    assert server.port is None
    assert popen_mock.mock_calls == [call.terminate(), call.wait()]


def test_sdk_server_removes_temp_file(popen_mock, tempfile_mock):
    server = SDKServer()
    saved_port = server.port
    server.close()

    assert saved_port == 2
    assert server.port is None
    assert tempfile_mock.mock_calls == [
        call.write(b"1\n"),
        call.seek(0),
        call.readline(),
        call.close(),
    ]


def test_sdk_server_auto_deletes(popen_mock, tempfile_mock):
    SDKServer()

    assert popen_mock.mock_calls == [call.terminate(), call.wait()]
    assert tempfile_mock.mock_calls == [
        call.write(b"1\n"),
        call.seek(0),
        call.readline(),
        call.close(),
    ]
