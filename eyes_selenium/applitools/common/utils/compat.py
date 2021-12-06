"""
Compatibility layer between Python 2 and 3
"""
from __future__ import absolute_import

import abc
import inspect
import io
import sys
from gzip import GzipFile

__all__ = (
    "ABC",
    "iteritems",
    "urlparse",
    "urljoin",
    "quote_plus",
    "range",
    "basestring",
    "urlencode",
    "parse_qs",
    "urlsplit",
    "urlunsplit",
    "urldefrag",
)


def _get_caller_globals_and_locals():
    """
    Returns the globals and locals of the calling frame.
    """
    caller_frame = inspect.stack()[2]
    myglobals = caller_frame[0].f_globals
    mylocals = caller_frame[0].f_locals
    return myglobals, mylocals


PY3 = sys.version_info[:1] >= (3,)

if PY3:
    from urllib.parse import (  # noqa
        parse_qs,
        quote_plus,
        urldefrag,
        urlencode,
        urljoin,
        urlparse,
        urlsplit,
        urlunsplit,
    )

    basestring = str
    ABC = abc.ABC
    range = range  # type: ignore


else:
    from urllib import quote_plus, urlencode  # noqa

    from urlparse import (  # noqa
        parse_qs,
        urldefrag,
        urljoin,
        urlparse,
        urlsplit,
        urlunsplit,
    )

    basestring = basestring
    ABC = abc.ABCMeta(str("ABC"), (), {})
    range = xrange  # type: ignore  # noqa


def iteritems(dct):
    return (getattr(dct, "iteritems", None) or dct.items)()
