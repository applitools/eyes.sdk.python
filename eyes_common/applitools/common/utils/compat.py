"""
Compatibility layer between Python 2 and 3
"""
from __future__ import absolute_import

import abc
import io
import sys
import types
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
    "with_metaclass",
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
        quote_plus,
    )  # noqa
    from gzip import compress as gzip_compress  # noqa
    from queue import Queue  # noqa

    basestring = str
    ABC = abc.ABC
    range = range  # type: ignore
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


def iteritems(dct):
    return (getattr(dct, "iteritems", None) or dct.items)()


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(type):
        def __new__(cls, name, this_bases, d):
            if sys.version_info[:2] >= (3, 7):
                # This version introduced PEP 560 that requires a bit
                # of extra care (we mimic what is done by __build_class__).
                resolved_bases = types.resolve_bases(bases)
                if resolved_bases is not bases:
                    d["__orig_bases__"] = bases
            else:
                resolved_bases = bases
            return meta(name, resolved_bases, d)

        @classmethod
        def __prepare__(cls, name, this_bases):
            return meta.__prepare__(name, bases)

    return type.__new__(metaclass, "temporary_class", (), {})


class DynamicClassAttributeGetter(object):
    def __init__(self, fget=None):
        self.fget = fget

    def __get__(self, instance, ownerclass=None):
        if instance is None:
            raise AttributeError()
        return self.fget(instance)
