import attr

from applitools.common import Region
from applitools.core.fluent import CheckSettings


@attr.s
class ImagesCheckSettings(CheckSettings):
    _image = attr.ib()
    _ignore_mismatch = attr.ib(init=False, default=False)

    def ignore_mismatch(self, ignore=True):
        self._ignore_mismatch = ignore
        return self

    def region(self, region):
        # type: (Region) -> ImagesCheckSettings
        self.update_target_region(region)
        return self
