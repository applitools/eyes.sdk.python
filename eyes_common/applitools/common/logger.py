"""
Logs handling.
"""
from __future__ import absolute_import

import functools
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
from structlog import BoundLoggerBase, PrintLogger, BoundLogger, PrintLoggerFactory

from structlog.stdlib import ProcessorFormatter
from structlog.processors import StackInfoRenderer

from applitools.common.utils.general_utils import get_env_with_prefix
from applitools.common.utils.json_utils import JsonInclude

_DEFAULT_EYES_LOGGER_NAME = "eyes"
_DEFAULT_EYES_FORMATTER = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(threadName)-9s) %(name)s: %(message)s"
)
_DEFAULT_LOGGER_LEVEL = int(get_env_with_prefix("LOGGER_LEVEL", logging.INFO))
_DEBUG_SCREENSHOT_PREFIX = get_env_with_prefix("DEBUG_SCREENSHOT_PREFIX", "screenshot_")
_DEBUG_SCREENSHOT_PATH = get_env_with_prefix("DEBUG_SCREENSHOT_PATH", ".")

__all__ = ("StdoutLogger", "FileLogger", "NullLogger")


class TraceLevel(Enum):
    Debug = 0
    Info = 1
    Notice = 2
    Warn = 3
    Error = 4


def current_time_in_iso8601():
    # break circular import in python2
    from . import utils

    global current_time_in_iso8601
    current_time_in_iso8601 = utils.current_time_in_iso8601
    return current_time_in_iso8601()


@attr.s
class ClientEvent(object):
    level = attr.ib(type=TraceLevel, metadata={JsonInclude.THIS: True})
    event = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    timestamp = attr.ib(
        factory=current_time_in_iso8601,
        metadata={JsonInclude.THIS: True},
    )  # type: Text


@attr.s
class LogSessionsClientEvents(object):
    events = attr.ib(
        factory=list, metadata={JsonInclude.THIS: True}
    )  # type List[ClientEvent]


class _Logger(object):
    """
    Simple logger. Supports only info and debug.
    """

    def __init__(
        self,
        name=__name__,
        level=_DEFAULT_LOGGER_LEVEL,
        handler_factory=lambda: None,
        formatter=None,
    ):
        # type: (tp.Text, int, tp.Callable, logging.Formatter) -> None
        """
        Ctor.

        :param name: The logger name.
        :param level: The log level (e.g., logging.DEBUG).
        :param handler_factory: A callable which creates a handler object.
                                We use a factory since the actual creation of the
                                handler should occur in open.
        :param formatter: A custom formatter for the logs.
        """
        self._name = name
        self._logger = None  # type: tp.Optional[Logger]
        # Setting handler (a logger must have at least one handler attached to it)
        self._handler_factory = handler_factory
        self._handler = None
        self._formatter = formatter
        self._level = level
        self._is_opened = False

    @property
    def is_opened(self):
        return self._is_opened

    def open(self):
        # type: () -> None
        """
        Open a handler.
        """
        # Actually create the handler
        self._handler = self._handler_factory()
        if self._handler:
            self._handler.setLevel(self._level)
            # Getting the logger
            self._logger = logging.getLogger(self._name)
            self._logger.setLevel(self._level)
            # Setting formatter
            if self._formatter is not None:
                self._handler.setFormatter(self._formatter)
            self._logger.addHandler(self._handler)
            self._is_opened = True

    def close(self):
        # type: () -> None
        """
        Close a handler.
        """
        if self._logger and self._handler:
            self._handler.close()
            # If we don't remove the handler and a call to logging.getLogger(...)
            # will be made with the same name as the current logger,
            # the handler will remain.
            self._logger.removeHandler(self._handler)
            self._logger = None
            self._handler = None
            self._is_opened = False

    def info(self, msg, *args, **kwargs):
        # type: (tp.Text, *tp.Any, **tp.Any) -> None
        """
        Writes info level msg to the logger.

        :param msg: The message that will be written to the logger.
        """
        if self._logger:
            self._logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        # type: (tp.Text, *tp.Any, **tp.Any) -> None
        """
        Writes debug level msg to the logger.

        :param msg: The message that will be written to the logger.
        """
        if self._logger:
            self._logger.debug(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        # type: (tp.Text, *tp.Any, **tp.Any) -> None
        if self._logger:
            self._logger.exception(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        # type: (tp.Text, *tp.Any, **tp.Any) -> None
        if self._logger:
            self._logger.error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        # type: (tp.Text, *tp.Any, **tp.Any) -> None
        if self._logger:
            self._logger.warning(msg, *args, **kwargs)


@attr.s
class NullLogger(object):
    """
    A simple logger class which does nothing (log messages are ignored).

    :param name: The logger name.
    :param level: The log level (e.g., logging.DEBUG)
    """

    name = attr.ib(default=_DEFAULT_EYES_LOGGER_NAME)  # type: Text
    level = attr.ib(default=_DEFAULT_LOGGER_LEVEL)  # type: int


@attr.s
class StdoutLogger(object):
    """
    A simple logger class for printing to STDOUT.

    :param name: The logger name.
    :param level: The log level (e.g., logging.DEBUG)
    """

    name = attr.ib(default=_DEFAULT_EYES_LOGGER_NAME)  # type: Text
    level = attr.ib(default=_DEFAULT_LOGGER_LEVEL)  # type: int


@attr.ib
class FileLogger(object):
    """
    A simple logger class for outputting log messages to a file

    :param filename: The name of this file to which logs should be written.
    :param mode: The mode in which the log file is opened
                 ('a' for appending, 'w' for overwrite).
    :param encoding: The encoding in which logs will be written to the file.
    :param delay: If True, file will not be opened until the first log message
                  is emitted.
    :param name: The logger name.
    :param level: The log level (e.g., logging.DEBUG)
    """

    filename = attr.ib(default="eyes.log")
    mode = attr.ib(default="a")
    encoding = attr.ib(default=None)
    delay = attr.ib(default=0)
    name = attr.ib(default=_DEFAULT_EYES_LOGGER_NAME)  # type: Text
    level = attr.ib(default=_DEFAULT_LOGGER_LEVEL)  # type: int


# Holds the actual logger after open is called.
_logger_origin = _Logger()  # type: _Logger
_logger_origin.set_handler(NullLogger())
_logger = structlog.wrap_logger(
    _logger_origin, wrapper_class=structlog.BoundLogger
)  # type: structlog.BoundLoggerBase


def set_logger(logger=None):
    # type: (tp.Optional[_Logger]) -> None
    """
    Sets the used logger to the logger.

    :param logger: The logger to use.
    """
    global _logger, _logger_origin
    if _logger_origin.is_opened:
        _logger_origin.close()
    if logger is not None and not logger.is_opened:
        logger.open()
    _logger_origin = logger
    _logger = structlog.wrap_logger(logger, wrapper_class=structlog.BoundLogger)


def get_logger():
    return _logger


def info(msg, *args, **kwargs):
    # type: (tp.Text, *tp.Any, **tp.Any) -> None
    """
    Writes info level msg to the logger.

    :param msg: The message that will be written to the log.
    """
    if _logger is not None:
        _logger.info(msg, *args, **kwargs)


def debug(msg, *args, **kwargs):
    # type: (tp.Text, *tp.Any, **tp.Any) -> None
    """
    Writes debug level msg to the logger.

    :param msg: The message that will be written to the log.
    """
    if _logger is not None:
        _logger.debug(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    # type: (tp.Text, *tp.Any, **tp.Any) -> None
    """
    Writes warning level msg to the logger.

    :param msg: The message that will be written to the log.
    """
    if _logger is not None:
        _logger.warning(msg, *args, **kwargs)


def deprecation(msg):
    # type: (tp.Text) -> None
    warnings.warn(msg, stacklevel=2, category=DeprecationWarning)


def exception(msg, *args, **kwargs):
    # type: (tp.Text, *tp.Any, **tp.Any) -> None
    """
    Writes error level msg to the logger with exception stack trace.

    :param msg: The message that will be written to the log.
    """

    if _logger is not None:
        _logger.exception(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    # type: (tp.Text, *tp.Any, **tp.Any) -> None
    """
    Writes error level msg to the logger.

    :param msg: The message that will be written to the log.
    """
    if _logger is not None:
        _logger.error(msg, *args, **kwargs)
