import typing

import attr
from selenium.webdriver.remote.webelement import WebElement

from applitools.common import Region
from applitools.core.fluent.check_settings import CheckSettings, CheckSettingsValues
from applitools.selenium.webelement import EyesWebElement

from .region import IgnoreRegionByElement, IgnoreRegionBySelector
from .selector import SelectorByElement, SelectorByLocator

if typing.TYPE_CHECKING:
    from typing import List
    from applitools.common.utils.custom_types import FrameReference


@attr.s(init=False)
class FrameLocator(object):
    frame_element = attr.ib()
    frame_selector = attr.ib()
    frame_name_or_id = attr.ib()
    frame_index = attr.ib()


class SeleniumCheckSettingsValues(CheckSettingsValues):
    _check_settings = attr.ib()  # type: SeleniumCheckSettings

    @property
    def target_element(self):
        return self._check_settings._target_element

    @property
    def target_selector(self):
        return self._check_settings._target_selector

    @property
    def target_provider(self):
        if self.target_selector:
            return SelectorByLocator(self.target_selector)
        elif self.target_element:
            return SelectorByElement(self.target_element)

    @property
    def size_mode(self):
        if (
            not self.target_region
            and not self.target_element
            and not self.target_selector
        ):
            if self.stitch_content:
                return "full-page"
            return "viewport"
        if self.target_region:
            if self.stitch_content:
                return "region"
            return "region"
        if self.stitch_content:
            return "selector"
        return "selector"


@attr.s(init=False)
class SeleniumCheckSettings(CheckSettings):
    _target_selector = attr.ib(default=None)
    _target_element = attr.ib(default=None)
    _frame_chain = attr.ib(factory=list)  # type: List[FrameLocator]

    def __init__(self, region=None, frame=None):

        # super(SeleniumCheckSettings).__init__(*args, **kwargs)
        if region:
            self.region(region)

        if frame:
            self.frame(frame)

    def region(self, region):
        if isinstance(region, Region):
            self.update_target_region(region)
        elif isinstance(region, str):
            self._target_selector = region
        elif isinstance(region, WebElement) or isinstance(region, EyesWebElement):
            self._target_element = region
        else:
            raise TypeError("region method called with argument of unknown type!")
        return self

    def frame(self, frame):
        # type: (FrameReference) -> CheckSettings
        fl = FrameLocator()
        if isinstance(frame, int):
            fl.frame_index = frame
        elif isinstance(frame, str):
            fl.frame_name_or_id = frame
        elif isinstance(frame, WebElement) or isinstance(frame, EyesWebElement):
            fl.frame_element = frame
        else:
            raise TypeError("region method called with argument of unknown type!")
        return self

    @staticmethod
    def _region_to_region_provider(region, method_name):
        if isinstance(region, str):
            return IgnoreRegionBySelector(region)
        elif isinstance(region, WebElement) or isinstance(region, EyesWebElement):
            return IgnoreRegionByElement(region)
        return super(SeleniumCheckSettings)._region_to_region_provider(
            region, method_name
        )
