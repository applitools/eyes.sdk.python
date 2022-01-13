from __future__ import absolute_import

from typing import Text


def round_converter(x):
    # type: (float) -> int
    return int(round(x))


def str2bool(v):
    # type: (Text) -> bool
    if v is None:
        return False
    return v.lower() in ("yes", "true", "t", "1")
