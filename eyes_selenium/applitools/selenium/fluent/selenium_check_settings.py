from __future__ import unicode_literals

import typing

import attr
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from applitools.common import FloatingBounds, Region, logger
from applitools.common.utils.compat import basestring
from applitools.core.fluent import CheckSettings
from applitools.selenium.webelement import EyesWebElement

from .region import (
    FloatingRegionByCssSelector,
    FloatingRegionByElement,
    IgnoreRegionByCssSelector,
    IgnoreRegionByElement,
)
from .selector import SelectorByElement, SelectorByLocator

if typing.TYPE_CHECKING:
    from typing import List
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


def _css_selector_from_(by, value):
    if by == By.ID:
        value = '[id="%s"]' % value
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
    _region = attr.ib(default=None)
    _frame = attr.ib(default=None)

    # _hide_caret = attr.ib(init=False, default=None)
    _scroll_root_element = attr.ib(init=False, default=None)
    _scroll_root_selector = attr.ib(init=False, default=None)
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
        elif is_list_or_tuple(region):
            by, value = region
            self._target_selector = _css_selector_from_(by, value)
        elif isinstance(region, basestring):
            self._target_selector = region
        elif is_webelement(region):
            self._target_element = region
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
        self._frame_chain.append(fl)
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
        if len(self._frame_chain) == 0:
            self._scroll_root_selector = selector
        else:
            self._frame_chain[-1].scroll_root_selector = selector

    def _set_scroll_root_element(self, element):
        if len(self._frame_chain) == 0:
            self._scroll_root_element = element
        else:
            self._frame_chain[-1].scroll_root_element = element

    def scroll_root_element(self, element_or_selector):
        if isinstance(element_or_selector, basestring):
            self._set_scroll_root_selector(element_or_selector)
        elif is_webelement(element_or_selector):
            self._set_scrool_root_element(element_or_selector)

    def _floating_provider_from(self, *args, **kwargs):
        region_or_container = args[0]
        if len(args) > 1:
            bounds = FloatingBounds(
                max_up_offset=args[1],
                max_down_offset=args[2],
                max_left_offset=args[3],
                max_right_offset=args[4],
            )
            if is_webelement(region_or_container):
                logger.debug("floating: FloatingRegionByElement")
                return FloatingRegionByElement(region_or_container, bounds)
            if isinstance(region_or_container, basestring):
                logger.debug("floating: FloatingRegionByCssSelector")
                return FloatingRegionByCssSelector(region_or_container, bounds)
            if is_list_or_tuple(region_or_container):
                by, value = region_or_container
                selector = _css_selector_from_(by, value)
                logger.debug("floating: FloatingRegionByCssSelector")
                return FloatingRegionByCssSelector(selector, bounds)
            kwargs["bounds"] = bounds
        return super(SeleniumCheckSettings, self)._floating_provider_from(
            *args, **kwargs
        )


def is_list_or_tuple(elm):
    return isinstance(elm, list) or isinstance(elm, tuple)


def is_webelement(elm):
    return isinstance(elm, WebElement) or isinstance(elm, EyesWebElement)
