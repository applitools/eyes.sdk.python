import typing
from enum import Enum

import attr

from applitools.common.utils.json_utils import JsonInclude

from . import utils

if typing.TYPE_CHECKING:
    from typing import List, Text


class TraceLevel(Enum):
    Debug = 0
    Info = 1
    Notice = 2
    Warn = 3
    Error = 4


@attr.s
class ClientEvent(object):
    level = attr.ib(type=TraceLevel, metadata={JsonInclude.THIS: True})
    event = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    timestamp = attr.ib(
        factory=utils.current_time_in_iso8601,
        metadata={JsonInclude.THIS: True},
    )  # type: Text


@attr.s
class LogSessionsClientEvents(object):
    events = attr.ib(
        factory=list, metadata={JsonInclude.THIS: True}
    )  # type List[ClientEvent]
