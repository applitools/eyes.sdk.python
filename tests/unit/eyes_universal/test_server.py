import sys

import pytest
from mock import Mock, call

from applitools.eyes_universal.server import SDKServer, executable_path


@pytest.fixture
def check_output(monkeypatch):
    mock = Mock(return_value=b"123\n")
    monkeypatch.setattr("applitools.eyes_universal.server.check_output", mock)
    return mock


@pytest.fixture
def close_fds_kw():
    if sys.version_info < (3,) and sys.platform != "win32":
        return {"close_fds": True}
    else:
        return {}


def test_sdk_server_default_args(check_output, close_fds_kw):
    server = SDKServer()

    assert server.port == 123
    assert check_output.mock_calls == [
        call([executable_path, "--fork"], universal_newlines=True, **close_fds_kw)
    ]


def test_sdk_server_with_port(check_output, close_fds_kw):
    server = SDKServer(port=345)

    assert server.port == 123  # mock return this
    assert check_output.mock_calls == [
        call(
            [executable_path, "--port", 345, "--fork"],
            universal_newlines=True,
            **close_fds_kw
        )
    ]


def test_sdk_server_no_singleton(check_output, close_fds_kw):
    server = SDKServer(singleton=False)

    assert server.port == 123
    assert check_output.mock_calls == [
        call(
            [executable_path, "--no-singleton", "--fork"],
            universal_newlines=True,
            **close_fds_kw
        )
    ]


def test_sdk_server_lazy(check_output, close_fds_kw):
    server = SDKServer(lazy=True)

    assert server.port == 123
    assert check_output.mock_calls == [
        call(
            [executable_path, "--lazy", "--fork"],
            universal_newlines=True,
            **close_fds_kw
        )
    ]


def test_sdk_server_idle_timeout(check_output, close_fds_kw):
    server = SDKServer(idle_timeout=5)

    assert server.port == 123
    assert check_output.mock_calls == [
        call(
            [executable_path, "--idle-timeout", 5, "--fork"],
            universal_newlines=True,
            **close_fds_kw
        )
    ]
