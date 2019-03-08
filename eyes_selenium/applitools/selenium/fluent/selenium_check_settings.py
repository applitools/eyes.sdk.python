import typing

import attr
from selenium.webdriver.remote.webelement import WebElement

from applitools.common import Region
from applitools.core.fluent import CheckSettings
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


@attr.s
class SeleniumCheckSettingsValues(object):
    _check_settings_values = attr.ib()

    def __getattr__(self, attr_name):
        return getattr(self._check_settings_values, attr_name)

    @property
    def target_provider(self):
        target_selector = self._check_settings_values.target_selector
        target_element = self._check_settings_values.target_element
        if target_selector:
            return SelectorByLocator(target_selector)
        elif target_element:
            return SelectorByElement(target_element)

    @property
    def size_mode(self):
        target_region = self._check_settings_values.target_region
        target_element = self._check_settings_values.target_element
        stitch_content = self._check_settings_values.stitch_content
        target_selector = self._check_settings_values.target_selector
        if not target_region and not target_element and not target_selector:
            if stitch_content:
                return "full-page"
            return "viewport"
        if target_region:
            if stitch_content:
                return "region"
            return "region"
        if stitch_content:
            return "selector"
        return "selector"


@attr.s
class SeleniumCheckSettings(CheckSettings):
    _region = attr.ib(default=None)
    _frame = attr.ib(default=None)

    _target_selector = attr.ib(init=False, default=None)
    _target_element = attr.ib(init=False, default=None)
    _frame_chain = attr.ib(init=False, factory=list)  # type: List[FrameLocator]

    def __attrs_post_init__(self):
        if self._region:
            self.region(self._region)
        if self._frame:
            self.frame(self._frame)

    @property
    def values(self):
        val = super(SeleniumCheckSettings, self).values
        return SeleniumCheckSettingsValues(val)

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
