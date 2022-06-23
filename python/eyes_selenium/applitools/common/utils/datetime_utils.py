from datetime import timedelta, tzinfo

__all__ = ("UTC",)


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
