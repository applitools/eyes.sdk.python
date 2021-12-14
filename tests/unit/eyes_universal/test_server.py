import sys

import pytest
from mock import Mock, call

from applitools.eyes_universal.server import SDKServer, executable_path


@pytest.fixture
def popen(monkeypatch):
    popen_mock = Mock()
    monkeypatch.setattr("applitools.eyes_universal.server.Popen", popen_mock)
    return popen_mock


@pytest.fixture
def tempfile(monkeypatch):
    tempfile_mock = Mock()
    tempfile_mock.return_value.readline.side_effect = [b"123\n"]
    tempfile_mock.return_value.name = "temp_file_name"
    monkeypatch.setattr(
        "applitools.eyes_universal.server.NamedTemporaryFile", tempfile_mock
    )
    return tempfile_mock


@pytest.fixture
def close_fds_kw():
    if sys.version_info < (3,) and sys.platform != "win32":
        return {"close_fds": True}
    else:
        return {}


def test_sdk_server_default_args(popen, tempfile, close_fds_kw):
    server = SDKServer()
    server.close()

    assert server.port == 123
    assert server.log_file_name == "temp_file_name"
    assert popen.mock_calls == [
        call([executable_path], stdout=tempfile.return_value, stderr=-2, **close_fds_kw)
    ]
    assert tempfile.mock_calls == [
        call("w+b"),
        call().seek(0),
        call().readline(),
        call().close(),
    ]


def test_sdk_server_file_not_read_immediately(popen, tempfile):
    tempfile.return_value.readline.side_effect = [b"", b"123\n"]
    server = SDKServer()
    server.close()

    assert tempfile.mock_calls == [
        call("w+b"),
        call().seek(0),
        call().readline(),
        call().seek(0),
        call().readline(),
        call().close(),
    ]


def test_sdk_server_with_port(popen, tempfile, close_fds_kw):
    server = SDKServer(port=345)
    server.close()

    assert server.port == 123  # mock return this
    assert server.log_file_name == "temp_file_name"
    assert popen.mock_calls == [
        call(
            [executable_path, "--port", 345],
            stdout=tempfile.return_value,
            stderr=-2,
            **close_fds_kw
        )
    ]
    assert tempfile.mock_calls == [
        call("w+b"),
        call().seek(0),
        call().readline(),
        call().close(),
    ]


def test_sdk_server_no_singleton(popen, tempfile, close_fds_kw):
    server = SDKServer(singleton=False)
    server.close()

    assert server.port == 123
    assert server.log_file_name == "temp_file_name"
    assert popen.mock_calls == [
        call(
            [executable_path, "--no-singleton"],
            stdout=tempfile.return_value,
            stderr=-2,
            **close_fds_kw
        ),
        call().terminate(),
    ]
    assert tempfile.mock_calls == [
        call("w+b"),
        call().seek(0),
        call().readline(),
        call().close(),
    ]


def test_sdk_server_lazy(popen, tempfile, close_fds_kw):
    server = SDKServer(lazy=True)
    server.close()

    assert server.port == 123
    assert server.log_file_name == "temp_file_name"
    assert popen.mock_calls == [
        call(
            [executable_path, "--lazy"],
            stdout=tempfile.return_value,
            stderr=-2,
            **close_fds_kw
        ),
    ]


def test_sdk_server_idle_timeout(popen, tempfile, close_fds_kw):
    server = SDKServer(idle_timeout=True)
    server.close()

    assert server.port == 123
    assert server.log_file_name == "temp_file_name"
    assert popen.mock_calls == [
        call(
            [executable_path, "--idle-timeout", 1],
            stdout=tempfile.return_value,
            stderr=-2,
            **close_fds_kw
        ),
    ]
