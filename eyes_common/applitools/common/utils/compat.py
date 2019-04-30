"""
Compatibility layer between Python 2 and 3
"""
from __future__ import absolute_import

import abc
import io
import sys
from gzip import GzipFile

__all__ = (
    "ABC",
    "range",
    "iteritems",
    "urlparse",
    "urljoin",
    "Queue",
    "gzip_compress",
    "range",
    "basestring",
    "urlencode",
    "parse_qs",
    "urlsplit",
    "urlunsplit",
)

PY3 = sys.version_info >= (3,)

if PY3:
    from urllib.parse import (
        urlparse,
        urljoin,
        urlencode,
        parse_qs,
        urlsplit,
        urlunsplit,
    )  # noqa
    from gzip import compress as gzip_compress  # noqa
    from queue import Queue  # noqa

    basestring = str
    ABC = abc.ABC
    range = range  # type: ignore
else:
    from urlparse import urlparse, urljoin, parse_qs, urlsplit, urlunsplit  # noqa
    from urllib import urlencode  # noqa
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


def iteritems(dct):
    return (getattr(dct, "iteritems", None) or dct.items)()
