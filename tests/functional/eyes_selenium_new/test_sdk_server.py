import os
import stat

from applitools.selenium.sdk_server import (
    AutoDownloadUSDKServer,
    USDKServer,
    _download_binary,
)


def test_usdk_server():
    server = USDKServer("/Users/igor/Downloads/cli-macos")
    port = server.port
    server.close()

    assert port


def test_download_binary():
    server_bin = _download_binary()

    assert server_bin
    assert os.stat(server_bin).st_mode & stat.S_IXUSR


def test_auto_download_usdk_server():
    server = AutoDownloadUSDKServer()
    port = server.port
    server.close()

    assert port
