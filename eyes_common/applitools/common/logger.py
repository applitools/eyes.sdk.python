"""
Logs handling.
"""
from __future__ import absolute_import

import logging
import logging.config
import sys
import typing as tp
import warnings
from typing import Text

import attr
import structlog
import structlog.dev

from applitools.common.utils.general_utils import get_env_with_prefix

__all__ = ("StdoutLogger", "FileLogger", "NullLogger")
_DEFAULT_HANDLER_LEVEL = int(get_env_with_prefix("LOGGER_LEVEL", logging.INFO))


@attr.s
class NullLogger(object):
    """
    A simple logger class which does nothing (log messages are ignored).

    :param name: unused
    :param level: The log level (e.g., logging.DEBUG)
    """

    name = attr.ib(default=None)
    level = attr.ib(default=_DEFAULT_HANDLER_LEVEL)  # type: int

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
    level = attr.ib(default=_DEFAULT_HANDLER_LEVEL)  # type: int

    def configure(self, std_logger):
        # type: (logging.Logger) -> None
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(self.level)
        handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                structlog.dev.ConsoleRenderer(), _pre_chain
            )
        )
        std_logger.addHandler(handler)


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
    level = attr.ib(default=_DEFAULT_HANDLER_LEVEL)  # type: int

    def configure(self, std_logger):
        # type: (logging.Logger) -> None
        handler = logging.FileHandler(
            self.filename, self.mode, self.encoding, self.delay
        )
        handler.setLevel(self.level)
        handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                structlog.processors.JSONRenderer(), _pre_chain
            )
        )
        std_logger.addHandler(handler)


def set_logger(logger=None):
    # type: (tp.Union[StdoutLogger, FileLogger, NullLogger]) -> None
    std_logger = logging.getLogger(__name__)
    logger.configure(std_logger)


def deprecation(msg):
    # type: (tp.Text) -> None
    warnings.warn(msg, stacklevel=2, category=DeprecationWarning)


_timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f", utc=False)
_pre_chain = [
    structlog.stdlib.add_log_level,
    _timestamper,
]
structlog.configure(
    processors=_pre_chain
    + [
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Allow everything so handlers can filter on their levels
logging.getLogger(__name__).setLevel(logging.DEBUG)

_logger = structlog.get_logger().bind()
bind = _logger.bind
info = _logger.info
debug = _logger.debug
warning = _logger.warning
exception = _logger.exception
error = _logger.error
