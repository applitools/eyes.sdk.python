"""
Logs handling.
"""
from __future__ import absolute_import

import functools
import json
import logging
import os
import sys
import typing as tp
import warnings
from enum import Enum
from logging import Logger
from typing import Text

import attr
import structlog
import structlog.dev
from structlog import BoundLogger, BoundLoggerBase, PrintLogger, PrintLoggerFactory
from structlog.processors import StackInfoRenderer
from structlog.stdlib import ProcessorFormatter

from applitools.common.utils.general_utils import get_env_with_prefix
from applitools.common.utils.json_utils import JsonInclude

_DEFAULT_EYES_FORMATTER = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(threadName)-9s) %(name)s: %(message)s"
)
_DEFAULT_LOGGER_LEVEL = int(get_env_with_prefix("LOGGER_LEVEL", logging.INFO))

__all__ = ("StdoutLogger", "FileLogger", "NullLogger")


@attr.s
class NullLogger(object):
    """
    A simple logger class which does nothing (log messages are ignored).

    :param name: unused
    :param level: The log level (e.g., logging.DEBUG)
    """

    name = attr.ib(default=None)
    level = attr.ib(default=_DEFAULT_LOGGER_LEVEL)  # type: int

    def configure(self, std_logger):
        # type: (logging.Logger) -> None
        pass


@attr.s
class StdoutLogger(object):
    """
    A simple logger class for printing to STDOUT.

    :param name: unused
    :param level: The log level (e.g., logging.DEBUG)
    """

    name = attr.ib(default=None)
    level = attr.ib(default=_DEFAULT_LOGGER_LEVEL)  # type: int

    def configure(self, std_logger):
        # type: (logging.Logger) -> None
        std_logger.addHandler(logging.StreamHandler(sys.stdout))
        std_logger.setLevel(self.level)


@attr.s
class FileLogger(object):
    """
    A simple logger class for outputting log messages to a file

    :param filename: The name of this file to which logs should be written.
    :param mode: The mode in which the log file is opened
                 ('a' for appending, 'w' for overwrite).
    :param encoding: The encoding in which logs will be written to the file.
    :param delay: If True, file will not be opened until the first log message
                  is emitted.
    :param name: unused
    :param level: The log level (e.g., logging.DEBUG)
    """

    filename = attr.ib(default="eyes.log")
    mode = attr.ib(default="a")
    encoding = attr.ib(default=None)
    delay = attr.ib(default=0)
    name = attr.ib(default=None)
    level = attr.ib(default=_DEFAULT_LOGGER_LEVEL)  # type: int

    def configure(self, std_logger):
        # type: (logging.Logger) -> None
        std_logger.addHandler(
            logging.FileHandler(self.filename, self.mode, self.encoding, self.delay)
        )
        std_logger.setLevel(self.level)


structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f", utc=False),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.set_exc_info,
        structlog.dev.ConsoleRenderer(colors=False),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
)

_logger = structlog.get_logger().bind()


def set_logger(logger=None):
    # type: (tp.Union[StdoutLogger, FileLogger, NullLogger]) -> None
    std_logger = logging.getLogger(__name__)
    logger.configure(std_logger)


def deprecation(msg):
    # type: (tp.Text) -> None
    warnings.warn(msg, stacklevel=2, category=DeprecationWarning)


bind = _logger.bind
info = _logger.info
debug = _logger.debug
warning = _logger.warning
exception = _logger.exception
error = _logger.error
