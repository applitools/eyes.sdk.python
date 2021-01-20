import os
import subprocess
import sys

import pytest

__all__ = ("image",)

import structlog
from _pytest import logging

from applitools.common import logger


@pytest.fixture
def image():
    from PIL import Image

    img = Image.new("RGB", (800, 600), "black")
    pixels = img.load()  # create the pixel map

    for i in range(img.size[0]):  # for every col:
        for j in range(img.size[1]):  # For every row
            pixels[i, j] = (i, j, 100)  # set the colour accordingly
    return img


def pytest_generate_tests(metafunc):
    import uuid

    # setup environment variables once per test run if not settled up
    # needed for multi thread run

    os.environ["APPLITOOLS_BATCH_ID"] = os.getenv(
        "APPLITOOLS_BATCH_ID", str(uuid.uuid4())
    )


@pytest.fixture
def fake_httpserver():
    server = "http.server"
    if sys.version_info[:2] <= (2, 7):
        server = "SimpleHTTPServer"
    server = subprocess.Popen(
        ["python", "-m", server, "7374"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    yield
    server.terminate()


class StructlogLoggingPlugin(logging.LoggingPlugin):
    """Replacement logging plugin that uses structlog console renderer"""

    def _create_formatter(self, *args, **kwargs):
        return structlog.stdlib.ProcessorFormatter(
            structlog.dev.ConsoleRenderer(), logger._pre_chain
        )


def pytest_configure(config):
    config.pluginmanager.get_plugin("logging").LoggingPlugin = StructlogLoggingPlugin
