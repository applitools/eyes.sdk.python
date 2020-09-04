import math
import typing
from abc import abstractmethod

import attr

from applitools.common import logger
from applitools.common.utils import ABC
from applitools.selenium.useragent import BrowserNames, OSNames

if typing.TYPE_CHECKING:
    from applitools.common import Region

    from .eyes import Eyes
    from .useragent import UserAgent
    from .webdriver import EyesWebDriver


def get_region_position_compensation(useragent, eyes):
    # type: (UserAgent, Eyes) -> RegionPositionCompensation
    if useragent:
        if useragent.browser == BrowserNames.Firefox:
            if useragent.browser_major_version >= 48:
                return FirefoxRegionPositionCompensation(eyes, useragent)
        elif useragent.browser == BrowserNames.Safari:
            return SafariRegionPositionCompensation(eyes, useragent)
        elif useragent.browser == BrowserNames.IE:
            return InternetExplorerRegionPositionCompensation(eyes, useragent)
    return NullRegionPositionCompensation(eyes, useragent)


@attr.s
class RegionPositionCompensation(ABC):
    _eyes = attr.ib()  # type: Eyes
    _useragent = attr.ib()  # type: UserAgent

    @abstractmethod
    def compensate_region_position(self, region, pixel_ratio):
        pass


class NullRegionPositionCompensation(RegionPositionCompensation):
    def compensate_region_position(self, region, pixel_ratio):
        # type: (Region, float) -> Region
        return region


class FirefoxRegionPositionCompensation(RegionPositionCompensation):
    def compensate_region_position(self, region, pixel_ratio):
        logger.info(str(self._useragent))
        logger.info(pixel_ratio)

        if (
            self._useragent.os == OSNames.Windows
            and self._useragent.os_major_version <= 7
        ):
            logger.info("compensating by {} pixels".format(pixel_ratio))
            return region.offset(0, pixel_ratio)

        if pixel_ratio == 1.0:
            return region

        if self._useragent.browser_major_version > 60:
            return region

        driver = self._eyes.driver  # type: EyesWebDriver
        fc = driver.frame_chain
        logger.info("frame_chain size: {}".format(fc.size))
        if fc.size > 0:
            return region

        region = region.offset(0, -math.ceil(pixel_ratio / 2))
        if region.width <= 0 or region.height <= 0:
            return Region.EMPTY()

        return region


class SafariRegionPositionCompensation(RegionPositionCompensation):
    def compensate_region_position(self, region, pixel_ratio):
        if pixel_ratio == 1.0:
            return region
        if region.width <= 0 and region.height <= 0:
            return Region.EMPTY()
        return region.offset(0, math.ceil(pixel_ratio))


class InternetExplorerRegionPositionCompensation(RegionPositionCompensation):
    def compensate_region_position(self, region, pixel_ratio):
        return region.offset(0, math.ceil(pixel_ratio))
