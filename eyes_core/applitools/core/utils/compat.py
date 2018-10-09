"""
Compatibility layer between Python 2 and 3
"""
from __future__ import absolute_import

import abc
import sys

__all__ = ('ABC', 'range', 'iteritems')

PY3 = sys.version_info >= (3,)

if PY3:
    from urllib.parse import urlparse, urljoin
    ABC = abc.ABC
    range = range  # type: ignore
else:
    from urlparse import urlparse, urljoin
    ABC = abc.ABCMeta(str("ABC"), (), {})
    range = xrange  # type: ignore  # noqa: F821


def iteritems(dct):
    return (getattr(dct, 'iteritems') or dct.items)()
