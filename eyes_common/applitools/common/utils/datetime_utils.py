from datetime import datetime, timedelta, tzinfo
from typing import Text

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
