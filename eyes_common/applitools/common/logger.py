"""
Logs handling.
"""
from __future__ import absolute_import

import cgitb
import inspect
import logging
import logging.config
import platform
import re
import sys
import threading
import typing as tp
from enum import Enum
from typing import Any, Dict, Optional, Text

import attr
import structlog
import structlog.dev

from applitools.common.utils import json_utils
from applitools.common.utils.general_utils import get_env_with_prefix

__all__ = ("StdoutLogger", "FileLogger")
_DEFAULT_HANDLER_LEVEL = int(get_env_with_prefix("LOGGER_LEVEL", logging.INFO))
_frames_regex = re.compile(
    r"function calls leading up to the error, in the order they occurred\.\s*"
    r"(.*?)"
    r"\s*The above is a description of an error in a Python program.",
    re.DOTALL,
)


class Stage(Enum):
    GENERAL = "GENERAL"
    OPEN = "OPEN"
    CHECK = "CHECK"
    CLOSE = "CLOSE"
    RENDER = "RENDER"
    RESOURCE_COLLECTION = "RESOURCE_COLLECTION"
    LOCATE = "LOCATE"
    OCR = "OCR"


def create_message_from_log(
    agent_id,  # type: Text
    test_id,  # type: Text
    stage,  # type: Stage
    data,  # type: Dict[Text, Any]
    type=None,  # type: Optional[Text]
    methods_back=3,  # type: int
):
    # type: (...) -> Text
    d = {
        "agentId": agent_id,
        "testId": test_id,
        "stage": stage,
        "threadId": threading.current_thread().name,
        "stackTrace": [inspect.stack()[i][3] for i in range(2, methods_back + 1)],
        "pythonVersion": "{} {}".format(
            platform.python_implementation(),
            platform.python_version(),
        ),
        "platformName": platform.platform(),
    }
    if type:
        d["type"] = type

    d.update(data)
    return json_utils.to_json(d)


class StdoutLogger(object):
    """
    A simple logger class for printing to STDOUT.
    """

    @tp.overload
    def __init__(self, is_verbose):
        # type: (bool) -> None
        """
        :param is_verbose: enables logging DEBUG messages
        """
        pass

    @tp.overload
    def __init__(self, name, level):
        # type: (tp.Text, int) -> None
        """
        :param name: unused
        :param level: log level (e.g. logging.WARNING)
        """
        pass

    def __init__(self, name=None, level=_DEFAULT_HANDLER_LEVEL, is_verbose=None):
        is_verbose = is_verbose if is_verbose is not None else name
        if is_verbose is True:
            self.level = logging.DEBUG
        elif is_verbose is False:
            self.level = logging.INFO
        else:
            self.level = level

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
    # type: (tp.Union[StdoutLogger, FileLogger]) -> None
    std_logger = logging.getLogger(__name__)
    logger.configure(std_logger)


def _add_thread_name(_, __, event_dict):
    event_dict["_thread_name"] = threading.current_thread().name
    return event_dict


def _format_exc_stack_trace_with_vars(_, __, event_dict):
    exc_info = event_dict.get("exc_info", None)
    if exc_info:
        if sys.version_info[0] >= 3 and isinstance(exc_info, BaseException):
            exc_info = (exc_info.__class__, exc_info, exc_info.__traceback__)
        elif isinstance(exc_info, tuple):
            pass
        elif exc_info:
            exc_info = sys.exc_info()
        try:
            match = _frames_regex.search(cgitb.text(exc_info))
            event_dict["stack_trace_with_vars"] = match[1]
        except Exception as e:
            event_dict["stack_trace_with_vars"] = "Collection failure: {}".format(e)
    return event_dict


_timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f", utc=False)
_pre_chain = [
    structlog.stdlib.add_log_level,
    _timestamper,
    _add_thread_name,
]
structlog.configure(
    processors=_pre_chain
    + [
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        _format_exc_stack_trace_with_vars,
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
logging.getLogger(__name__).propagate = False

_logger = structlog.get_logger().bind()
bind = _logger.bind
info = _logger.info
debug = _logger.debug
warning = _logger.warning
exception = _logger.exception
error = _logger.error
