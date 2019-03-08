from applitools.common.geometry import Region
from applitools.common.utils import ABC
from applitools.core.fluent.check_settings import CheckSettings

_all_ = ("CheckTarget",)


class CheckTarget(ABC):
    @staticmethod
    def window():
        # type: () -> CheckSettings
        return CheckSettings(None)

    @staticmethod
    def region(rect):
        # type: (Region) -> CheckSettings
        return CheckSettings(rect)
