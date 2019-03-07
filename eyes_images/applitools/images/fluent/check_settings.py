import attr

from applitools.common import Region
from applitools.core.fluent import CheckSettings, CheckSettingsValues


@attr.s
class ImageCheckSettingsValues(CheckSettingsValues):
    """
    Access to values stored in :py:class:`CheckSettings`
    """

    _check_settings = attr.ib()  # type: ImagesCheckSettings

    @property
    def image(self):
        return self._check_settings._image


@attr.s
class ImagesCheckSettings(CheckSettings):
    _image = attr.ib()
    _ignore_mismatch = attr.ib(init=False, default=False)

    @property
    def values(self):
        return ImageCheckSettingsValues(self)

    def ignore_mismatch(self, ignore=True):
        self._ignore_mismatch = ignore
        return self

    def region(self, region):
        # type: (Region) -> ImagesCheckSettings
        self.update_target_region(region)
        return self
