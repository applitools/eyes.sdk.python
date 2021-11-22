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
    from gzip import compress as gzip_compress  # noqa
    from queue import Queue  # noqa
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
    from urllib import quote_plus, urlencode  # noqa

    from Queue import Queue  # noqa
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

    def gzip_compress(data, compresslevel=9):
        """Compress data in one shot and return the compressed string.
        Optional argument is the compression level, in range of 0-9.
        """
        buf = io.BytesIO()
        with GzipFile(fileobj=buf, mode="wb", compresslevel=compresslevel) as f:
            f.write(data)
        return buf.getvalue()

    def raise_from(exc, cause):
        """
        Equivalent to:

            raise EXCEPTION from CAUSE

        on Python 3. (See PEP 3134).
        """
        # Is either arg an exception class (e.g. IndexError) rather than
        # instance (e.g. IndexError('my message here')? If so, pass the
        # name of the class undisturbed through to "raise ... from ...".
        if isinstance(exc, type) and issubclass(exc, Exception):
            e = exc()
            # exc = exc.__name__
            # execstr = "e = " + _repr_strip(exc) + "()"
            # myglobals, mylocals = _get_caller_globals_and_locals()
            # exec(execstr, myglobals, mylocals)
        else:
            e = exc
        e.__suppress_context__ = False
        if isinstance(cause, type) and issubclass(cause, Exception):
            e.__cause__ = cause()
            e.__suppress_context__ = True
        elif cause is None:
            e.__cause__ = None
            e.__suppress_context__ = True
        elif isinstance(cause, BaseException):
            e.__cause__ = cause
            e.__suppress_context__ = True
        else:
            raise TypeError("exception causes must derive from BaseException")
        e.__context__ = sys.exc_info()[1]
        raise e


def iteritems(dct):
    return (getattr(dct, "iteritems", None) or dct.items)()
