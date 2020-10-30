import itertools
import time
from datetime import datetime, timedelta, tzinfo
from typing import Optional, Text, Union

from applitools.common import logger

__all__ = ("UTC", "to_rfc1123_datetime", "current_time_in_rfc1123")


class _UtcTz(tzinfo):
    """
    A UTC timezone class which is tzinfo compliant.
    """

    _ZERO = timedelta(0)

    def utcoffset(self, dt):
        return _UtcTz._ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return _UtcTz._ZERO


UTC = _UtcTz()


def to_rfc1123_datetime(dt):
    # type: (datetime) -> Text
    """Return a string representation of a date according to RFC 1123
    (HTTP/1.1).

    The supplied date must be in UTC.

    """
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
    month = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ][dt.month - 1]
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (
        weekday,
        dt.day,
        month,
        dt.year,
        dt.hour,
        dt.minute,
        dt.second,
    )


def current_time_in_rfc1123():
    # type: () -> Text
    return to_rfc1123_datetime(datetime.now(UTC))


def to_sec(millisecond):
    # type: (Union[int, float]) -> float
    return millisecond / 1000.0


def to_ms(seconds):
    # type: (Union[int, float]) -> int
    return int(seconds * 1000)


def sleep(time_ms, msg=None, verbose=True):
    # type: (int, Optional[Text], bool) -> None
    """Make program sleep for a specified time

    The main API uses milliseconds but python internally uses seconds.
    So this helper uses for seamlessly conversion.

    Args:
        time_ms: time in milliseconds
    """
    time.sleep(to_sec(time_ms))
    if verbose:
        logger.debug("Sleep for {} ms | {}".format(time_ms, msg if msg else ""))


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        if "log_time" in kw:
            name = kw.get("log_name", method.__name__.upper())
            kw["log_time"][name] = to_ms(te - ts)
        else:
            logger.debug("%r  %2.2f ms" % (method.__name__, to_ms(te - ts)))
        return result

    return timed


def retry(delays=(0, 1000, 5000), exception=Exception, report=lambda *args: None):
    """
    This is a Python decorator which helps implementing an aspect oriented
    implementation of a retrying of certain steps which might fail sometimes.
    https://code.activestate.com/recipes/580745-retry-decorator-in-python/
    """

    def wrapper(function):
        def wrapped(*args, **kwargs):
            problems = []
            for delay in itertools.chain(delays, [None]):
                try:
                    return function(*args, **kwargs)
                except exception as problem:
                    problems.append(problem)
                    if delay is None:
                        report("retryable failed definitely: {}".format(problems))
                        raise
                    else:
                        report(
                            "retryable failed: {} -- delaying for {}".format(
                                problem, delay
                            )
                        )
                        sleep(delay)

        return wrapped

    return wrapper
