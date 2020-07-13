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
    "range",
    "iteritems",
    "urlparse",
    "urljoin",
    "quote_plus",
    "Queue",
    "gzip_compress",
    "range",
    "basestring",
    "urlencode",
    "parse_qs",
    "urlsplit",
    "urlunsplit",
    "raise_from",
)


def _get_caller_globals_and_locals():
    """
    Returns the globals and locals of the calling frame.

    Is there an alternative to frame hacking here?
    """
    caller_frame = inspect.stack()[2]
    myglobals = caller_frame[0].f_globals
    mylocals = caller_frame[0].f_locals
    return myglobals, mylocals


PY3 = sys.version_info >= (3,)

if PY3:
    from urllib.parse import (
        urlparse,
        urljoin,
        urlencode,
        parse_qs,
        urlsplit,
        urlunsplit,
        quote_plus,
    )  # noqa
    from gzip import compress as gzip_compress  # noqa
    from queue import Queue  # noqa

    basestring = str
    ABC = abc.ABC
    range = range  # type: ignore

    def raise_from(exc, cause):
        """
        Equivalent to:

            raise EXCEPTION from CAUSE

        on Python 3. (See PEP 3134).
        """
        myglobals, mylocals = _get_caller_globals_and_locals()

        # We pass the exception and cause along with other globals
        # when we exec():
        myglobals = myglobals.copy()
        myglobals["__python_future_raise_from_exc"] = exc
        myglobals["__python_future_raise_from_cause"] = cause
        execstr = (
            "raise __python_future_raise_from_exc from __python_future_raise_from_cause"
        )

        exec(execstr, myglobals, mylocals)


else:
    from urlparse import (
        urlparse,
        urljoin,
        parse_qs,
        urlsplit,
        urlunsplit,
    )  # noqa
    from urllib import urlencode, quote_plus  # noqa
    from Queue import Queue  # noqa

    basestring = basestring
    ABC = abc.ABCMeta(str("ABC"), (), {})
    range = xrange  # type: ignore  # noqa

    def gzip_compress(data, compresslevel=9):
        """Compress data in one shot and return the compressed string.
        Optional argument is the compression level, in range of 0-9.
        """
        buf = io.BytesIO()
        with GzipFile(fileobj=buf, mode="wb", compresslevel=compresslevel) as f:
            f.write(data)
        return buf.getvalue()

    def raise_(tp, value=None, tb=None):
        """
        A function that matches the Python 2.x ``raise`` statement. This
        allows re-raising exceptions with the cls value and traceback on
        Python 2 and 3.
        """
        if value is not None and isinstance(tp, Exception):
            raise TypeError("instance exception may not have a separate value")
        if value is not None:
            exc = tp(value)
        else:
            exc = tp
        if exc.__traceback__ is not tb:
            raise exc.with_traceback(tb)
        raise exc


def iteritems(dct):
    return (getattr(dct, "iteritems", None) or dct.items)()
