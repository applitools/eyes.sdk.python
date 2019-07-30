from typing import Protocol

from applitools.common.geometry import Region
from applitools.core.fluent.check_settings import CheckSettings

_all_ = ("CheckTarget",)


class CheckTarget(Protocol):
    @staticmethod
    def window():
        # type: () -> CheckSettings
        pass

    @staticmethod
    def region(region):
        # type: (Region) -> CheckSettings
        pass
