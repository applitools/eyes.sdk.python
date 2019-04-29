from __future__ import unicode_literals

import typing

import attr
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from applitools.common import Region, logger
from applitools.common.utils.compat import basestring
from applitools.core.fluent import CheckSettings, CheckSettingsValues
from applitools.selenium.fluent import SelectorByElement, SelectorByLocator
from applitools.selenium.webelement import EyesWebElement

from .region import (
    FloatingRegionByCssSelector,
    FloatingRegionByElement,
    IgnoreRegionByCssSelector,
    IgnoreRegionByElement,
)

if typing.TYPE_CHECKING:
    from typing import List, Union, Text, Tuple
    from applitools.common.visual_grid import VisualGridSelector
    from applitools.common.utils.custom_types import FrameReference


@attr.s
class FrameLocator(object):
    frame_element = attr.ib(default=None)
    frame_selector = attr.ib(default=None)
    frame_name_or_id = attr.ib(default=None)
    frame_index = attr.ib(default=None)
    scroll_root_selector = attr.ib(default=None)
    scroll_root_element = attr.ib(default=None)


@attr.s
class SeleniumCheckSettingsValues(CheckSettingsValues):
    # hide_caret = attr.ib(init=False, default=None)
    scroll_root_element = attr.ib(init=False, default=None)  # type: EyesWebElement
    scroll_root_selector = attr.ib(init=False, default=None)
    target_selector = attr.ib(init=False, default=None)
    target_element = attr.ib(init=False, default=None)
    frame_chain = attr.ib(init=False, factory=list)  # type: List[FrameLocator]

    # for Rendering Grid
    BEFORE_CAPTURE_SCREENSHOT = "beforeCaptureScreenshot"
    region = attr.ib(factory=list)
    selector = attr.ib(default=None)  # type: VisualGridSelector
    script_hooks = attr.ib(factory=dict)

    @property
    def target_provider(self):
        target_selector = self.target_selector
        target_element = self.target_element
        if target_selector:
            return SelectorByLocator(target_selector)
        elif target_element:
            return SelectorByElement(target_element)

    @property
    def size_mode(self):
        target_region = self.target_region
        target_element = self.target_element
        stitch_content = self.stitch_content
        target_selector = self.target_selector
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


def _css_selector_from_(by, value):
    if by == By.ID:
        value = "#%s" % value
    elif by == By.TAG_NAME:
        value = value
    elif by == By.CLASS_NAME:
        value = ".%s" % value
    elif by == By.NAME:
        value = '[name="%s"]' % value
    else:
        raise TypeError("By {} is not supported".format(by))
    return value


@attr.s
class SeleniumCheckSettings(CheckSettings):
    values = attr.ib(init=False)  # type: SeleniumCheckSettingsValues

    _region = attr.ib(default=None)
    _frame = attr.ib(default=None)

    def __attrs_post_init__(self):
        # type: () -> None
        self.values = SeleniumCheckSettingsValues()
        if self._region:
            self.region(self._region)
        if self._frame:
            self.frame(self._frame)

    def region(self, region):
        # type: (Union[Region, Text, List, Tuple, WebElement, EyesWebElement]) -> CheckSettings
        if isinstance(region, Region):
            self.update_target_region(region)
        elif is_list_or_tuple(region):
            by, value = region
            self.values.target_selector = _css_selector_from_(by, value)
        elif isinstance(region, basestring):
            self.values.target_selector = region
        elif is_webelement(region):
            self.values.target_element = region
        else:
            raise TypeError("region method called with argument of unknown type!")
        return self

    def frame(self, frame):
        # type: (FrameReference) -> CheckSettings
        fl = FrameLocator()
        if isinstance(frame, int):
            fl.frame_index = frame
        elif isinstance(frame, basestring):
            fl.frame_name_or_id = frame
        elif is_webelement(frame):
            fl.frame_element = frame
        else:
            raise TypeError("frame method called with argument of unknown type!")
        self.values.frame_chain.append(fl)
        return self

    def _region_provider_from(self, region, method_name):
        if isinstance(region, basestring):
            logger.debug("{name}: IgnoreRegionByCssSelector".format(name=method_name))
            return IgnoreRegionByCssSelector(region)
        if is_list_or_tuple(region):
            by, val = region
            sel = _css_selector_from_(by, val)
            logger.debug("{name}: IgnoreRegionByCssSelector".format(name=method_name))
            return IgnoreRegionByCssSelector(sel)
        elif is_webelement(region):
            logger.debug("{name}: IgnoreRegionByElement".format(name=method_name))
            return IgnoreRegionByElement(region)
        return super(SeleniumCheckSettings, self)._region_provider_from(
            region, method_name
        )

    def _set_scroll_root_selector(self, selector):
        if len(self.values.frame_chain) == 0:
            self.values.scroll_root_selector = selector
        else:
            self.values.frame_chain[-1].scroll_root_selector = selector

    def _set_scroll_root_element(self, element):
        if len(self.values.frame_chain) == 0:
            self.values.scroll_root_element = element
        else:
            self.values.frame_chain[-1].scroll_root_element = element

    def scroll_root_element(self, element_or_selector):
        if isinstance(element_or_selector, basestring):
            self._set_scroll_root_selector(element_or_selector)
        elif is_webelement(element_or_selector):
            self._set_scrool_root_element(element_or_selector)

    def _floating_provider_from(self, region, bounds):
        if is_webelement(region):
            logger.debug("floating: FloatingRegionByElement")
            return FloatingRegionByElement(region, bounds)
        if isinstance(region, basestring):
            logger.debug("floating: FloatingRegionByCssSelector")
            return FloatingRegionByCssSelector(region, bounds)
        if is_list_or_tuple(region):
            by, value = region
            selector = _css_selector_from_(by, value)
            logger.debug("floating: FloatingRegionByCssSelector")
            return FloatingRegionByCssSelector(selector, bounds)
        return super(SeleniumCheckSettings, self)._floating_provider_from(
            region, bounds
        )


def is_list_or_tuple(elm):
    return isinstance(elm, list) or isinstance(elm, tuple)


def is_webelement(elm):
    return isinstance(elm, WebElement) or isinstance(
        getattr(elm, "_element", None), WebElement
    )
