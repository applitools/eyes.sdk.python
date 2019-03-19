from applitools.common.geometry import Region
from applitools.common.utils import ABC
from applitools.core.fluent.check_settings import CheckSettings

_all_ = ("CheckTarget",)


class CheckTarget(ABC):
    @staticmethod
    def window():
        # type: () -> CheckSettings
        return CheckSettings()

    @staticmethod
    def region(rect):
        # type: (Region) -> CheckSettings
        cs = CheckSettings()
        cs.update_target_region(rect)
        return cs
