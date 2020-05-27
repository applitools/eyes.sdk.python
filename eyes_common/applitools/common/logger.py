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
from logging import Logger

from applitools.common.utils.general_utils import get_env_with_prefix

_DEFAULT_EYES_LOGGER_NAME = "eyes"
_DEFAULT_EYES_FORMATTER = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(threadName)-9s) %(name)s: %(message)s"
)
_DEFAULT_LOGGER_LEVEL = int(get_env_with_prefix("LOGGER_LEVEL", logging.INFO))
_DEBUG_SCREENSHOT_PREFIX = get_env_with_prefix("DEBUG_SCREENSHOT_PREFIX", "screenshot_")
_DEBUG_SCREENSHOT_PATH = get_env_with_prefix("DEBUG_SCREENSHOT_PATH", ".")

__all__ = ("StdoutLogger", "FileLogger", "NullLogger")


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


class StdoutLogger(_Logger):
    """
    A simple logger class for printing to STDOUT.
    """

    def __init__(self, name=_DEFAULT_EYES_LOGGER_NAME, level=_DEFAULT_LOGGER_LEVEL):
        # type: (tp.Text, int) -> None
        """
        Ctor.

        :param name: The logger name.
        :param level: The log level (default is logging.DEBUG).
        """
        handler_factory = functools.partial(logging.StreamHandler, sys.stdout)
        super(StdoutLogger, self).__init__(
            name, level, handler_factory, _DEFAULT_EYES_FORMATTER
        )


class FileLogger(_Logger):
    """
    A simple logger class for outputting log messages to a file
    """

    def __init__(
        self,
        filename="eyes.log",
        mode="a",
        encoding=None,
        delay=0,
        name=_DEFAULT_EYES_LOGGER_NAME,
        level=_DEFAULT_LOGGER_LEVEL,
    ):
        """
        Ctor.

        :param filename: The name of this file to which logs should be written.
        :param mode: The mode in which the log file is opened
                     ('a' for appending, 'w' for overwrite).
        :param encoding: The encoding in which logs will be written to the file.
        :param delay: If True, file will not be opened until the first log message
                      is emitted.
        :param name: The logger name.
        :param level: The log level (e.g., logging.DEBUG)
        """
        handler_factory = functools.partial(
            logging.FileHandler, filename, mode, encoding, delay
        )
        super(FileLogger, self).__init__(
            name, level, handler_factory, _DEFAULT_EYES_FORMATTER
        )


class NullLogger(_Logger):
    """
    A simple logger class which does nothing (log messages are ignored).
    """

    def __init__(self, name=_DEFAULT_EYES_LOGGER_NAME, level=_DEFAULT_LOGGER_LEVEL):
        """
        Ctor.

        :param name: The logger name.
        :param level: The log level (e.g., logging.DEBUG).
        """
        super(NullLogger, self).__init__(name, level)


# This will be set by the user.
_logger_to_use = None  # type: tp.Optional[_Logger]
# Holds the actual logger after open is called.
_logger = None  # type: tp.Optional[_Logger]


def set_logger(logger=None):
    # type: (tp.Optional[_Logger]) -> None
    """
    Sets the used logger to the logger.

    :param logger: The logger to use.
    """
    global _logger_to_use
    _logger_to_use = logger


def open_():
    # type: () -> None
    """
    Opens a new logger.
    """
    global _logger
    _logger = _logger_to_use
    if _logger is not None and not _logger.is_opened:
        _logger.open()


def close():
    # type: () -> None
    """
    Closed the logger.
    """
    global _logger
    if _logger is not None:
        _logger.close()
        _logger = None


def info(msg):
    # type: (tp.Text) -> None
    """
    Writes info level msg to the logger.

    :param msg: The message that will be written to the log.
    """
    if _logger is not None:
        _logger.info(msg)


def debug(msg):
    # type: (tp.Text) -> None
    """
    Writes debug level msg to the logger.

    :param msg: The message that will be written to the log.
    """
    if _logger is not None:
        _logger.debug(msg)


def warning(msg):
    # type: (tp.Text) -> None
    """
    Writes info level msg to the logger.

    :param msg: The message that will be written to the log.
    """
    warnings.warn(msg, stacklevel=2)


def deprecation(msg):
    # type: (tp.Text) -> None
    warnings.warn(msg, stacklevel=2, category=DeprecationWarning)


def exception(msg):
    if _logger is not None:
        _logger.exception(msg)


def error(msg):
    if _logger is not None:
        _logger.error(msg)
