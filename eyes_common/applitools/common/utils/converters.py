from __future__ import absolute_import

from datetime import datetime
from enum import Enum
from typing import Union


def value_from_enum(e):
    #  type: (Union[Enum, str]) -> str
    return e.value if isinstance(e, Enum) else e


def isoformat(d):
    # type: (datetime) -> str
    return d.isoformat()


def round_converter(x):
    # type: (float) -> int
    return int(round(x))
