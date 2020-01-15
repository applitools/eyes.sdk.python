from __future__ import unicode_literals

from typing import TYPE_CHECKING, List, Optional, Text, Tuple, Union, overload

import attr
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from applitools.common import Region, logger
from applitools.common.utils.compat import basestring
from applitools.core.fluent import CheckSettings, CheckSettingsValues
from applitools.selenium.webelement import EyesWebElement

from .region import (
    FloatingRegionByElement,
    RegionByElement,
    RegionBySelector,
    FloatingRegionBySelector,
)

if TYPE_CHECKING:
    from applitools.common.visual_grid import VisualGridSelector
    from applitools.common.utils.custom_types import (
        AnyWebElement,
        FrameNameOrId,
        FrameIndex,
        BySelector,
        CssSelector,
        FLOATING_VALUES,
    )

BEFORE_CAPTURE_SCREENSHOT = "beforeCaptureScreenshot"


@attr.s
class FrameLocator(object):
    frame_element = attr.ib(default=None)  # type: AnyWebElement
    frame_selector = attr.ib(default=None)  # type: BySelector
    frame_name_or_id = attr.ib(default=None)  # type: FrameNameOrId
    frame_index = attr.ib(default=None)  # type: FrameIndex
    scroll_root_selector = attr.ib(default=None)  # type: CssSelector
    scroll_root_element = attr.ib(default=None)  # type: AnyWebElement


@attr.s
class SeleniumCheckSettingsValues(CheckSettingsValues):
    # hide_caret = attr.ib(init=False, default=None)
    scroll_root_element = attr.ib(init=False, default=None)  # type: EyesWebElement
    scroll_root_selector = attr.ib(init=False, default=None)  # type: CssSelector
    target_selector = attr.ib(init=False, default=None)  # type: BySelector
    target_element = attr.ib(init=False, default=None)  # type: EyesWebElement
    frame_chain = attr.ib(init=False, factory=list)  # type: List[FrameLocator]

    # for Rendering Grid
    selector = attr.ib(default=None)  # type: VisualGridSelector
    script_hooks = attr.ib(factory=dict)  # type: dict

    @property
    def size_mode(self):
        if (
            self.target_region is None
            and self.target_selector is None
            and self.target_element is None
        ):
            if self.stitch_content:
                return "full-page"
            return "viewport"
        if self.target_region:
            return "region"
        return "selector"


@attr.s
class SeleniumCheckSettings(CheckSettings):
    values = attr.ib(
        init=False, factory=SeleniumCheckSettingsValues
    )  # type: SeleniumCheckSettingsValues

    _region = attr.ib(default=None)
    _frame = attr.ib(default=None)

    @overload  # noqa
    def layout(self, *by):
        # type: (*BySelector)  -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def layout(self, *element):
        # type: (*AnyWebElement)  -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def layout(self, *css_selector):
        # type: (*CssSelector)  -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def layout(self, *region):
        # type: (*Region)  -> SeleniumCheckSettings
        pass

    def layout(self, *region):  # noqa
        return super(SeleniumCheckSettings, self).layout(*region)

    @overload  # noqa
    def strict(self, *by):
        # type: (*BySelector)  -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def strict(self, *element):
        # type: (*AnyWebElement)  -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def strict(self, *css_selector):
        # type: (*CssSelector)  -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def strict(self, *region):
        # type: (*Region)  -> SeleniumCheckSettings
        pass

    def strict(self, *region):  # noqa
        return super(SeleniumCheckSettings, self).strict(*region)

    @overload  # noqa
    def content(self, *by):
        # type: (*BySelector)  -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def content(self, *element):
        # type: (*AnyWebElement)  -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def content(self, *css_selector):
        # type: (*CssSelector)  -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def content(self, *region):
        # type: (*Region)  -> SeleniumCheckSettings
        pass

    def content(self, *region):  # noqa
        return super(SeleniumCheckSettings, self).content(*region)

    @overload  # noqa
    def ignore(self, *by):
        # type: (*BySelector)  -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def ignore(self, *element):
        # type: (*AnyWebElement)  -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def ignore(self, *css_selector):
        # type: (*CssSelector)  -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def ignore(self, *region):
        # type: (*Region)  -> SeleniumCheckSettings
        pass

    def ignore(self, *region):  # noqa
        return super(SeleniumCheckSettings, self).ignore(*region)

    @overload  # noqa
    def floating(self, max_offset, region):
        # type: (int, FLOATING_VALUES) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def floating(
        self, region, max_up_offset, max_down_offset, max_left_offset, max_right_offset
    ):
        # type: (FLOATING_VALUES, int, int, int, int) -> SeleniumCheckSettings
        pass

    def floating(self, *args):  # noqa
        return super(SeleniumCheckSettings, self).floating(*args)

    @overload  # noqa
    def region(self, region):
        # type: (Region) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def region(self, css_selector):
        # type: (CssSelector) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def region(self, element):
        # type: (AnyWebElement) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def region(self, by):
        # type: (BySelector) -> SeleniumCheckSettings
        pass

    def region(self, region):  # noqa
        if isinstance(region, Region):
            self.values.target_region = region
        elif is_list_or_tuple(region):
            by, value = region
            self.values.target_selector = [by, value]
        elif isinstance(region, basestring):
            self.values.target_selector = [By.CSS_SELECTOR, region]
        elif is_webelement(region):
            self.values.target_element = region
        else:
            raise TypeError("region method called with argument of unknown type!")
        return self

    @overload  # noqa
    def frame(self, frame_name_or_id):
        # type: (FrameNameOrId) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def frame(self, element):
        # type: (AnyWebElement) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def frame(self, index):
        # type: (FrameIndex) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def frame(self, by):
        # type: (BySelector) -> SeleniumCheckSettings
        pass

    def frame(self, frame):  # noqa
        fl = FrameLocator()
        if isinstance(frame, int):
            fl.frame_index = frame
        elif isinstance(frame, basestring):
            fl.frame_name_or_id = frame
        elif is_webelement(frame):
            fl.frame_element = frame
        elif is_list_or_tuple(frame):
            by, value = frame
            fl.frame_selector = [by, value]
        else:
            raise TypeError("frame method called with argument of unknown type!")
        self.values.frame_chain.append(fl)
        return self

    def before_render_screenshot_hook(self, hook):
        # type: (Text) -> SeleniumCheckSettings
        self.values.script_hooks[BEFORE_CAPTURE_SCREENSHOT] = hook
        return self

    def _region_provider_from(self, region, method_name):
        if isinstance(region, basestring):
            logger.debug("{name}: RegionByCssSelector".format(name=method_name))
            return RegionBySelector(By.CSS_SELECTOR, region)
        if is_list_or_tuple(region):
            by, val = region
            logger.debug("{name}: RegionBySelector".format(name=method_name))
            return RegionBySelector(by, val)
        elif is_webelement(region):
            logger.debug("{name}: RegionByElement".format(name=method_name))
            return RegionByElement(region)
        return super(SeleniumCheckSettings, self)._region_provider_from(
            region, method_name
        )

    def _set_scroll_root_selector(self, by, value):
        if len(self.values.frame_chain) == 0:
            self.values.scroll_root_selector = [by, value]
        else:
            self.values.frame_chain[-1].scroll_root_selector = [by, value]

    def _set_scroll_root_element(self, element):
        if len(self.values.frame_chain) == 0:
            self.values.scroll_root_element = element
        else:
            self.values.frame_chain[-1].scroll_root_element = element

    @overload  # noqa
    def scroll_root_element(self, element):
        # type: (AnyWebElement) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def scroll_root_element(self, selector):
        # type: (CssSelector) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def scroll_root_element(self, by):
        # type: (BySelector) -> SeleniumCheckSettings
        pass

    def scroll_root_element(self, element_or_selector):  # noqa
        if isinstance(element_or_selector, basestring):
            self._set_scroll_root_selector(By.CSS_SELECTOR, element_or_selector)
        elif is_list_or_tuple(element_or_selector):
            by, value = element_or_selector
            self._set_scroll_root_selector(by, value)
        elif is_webelement(element_or_selector):
            self._set_scroll_root_element(element_or_selector)
        return self

    def _floating_provider_from(self, region, bounds):
        if is_webelement(region):
            logger.debug("floating: FloatingRegionByElement")
            return FloatingRegionByElement(region, bounds)
        if isinstance(region, basestring):
            logger.debug("floating: FloatingRegionByCssSelector")
            return FloatingRegionBySelector(By.CSS_SELECTOR, region, bounds)
        if is_list_or_tuple(region):
            by, value = region
            logger.debug("floating: FloatingRegionBySelector")
            return FloatingRegionBySelector(by, value, bounds)
        return super(SeleniumCheckSettings, self)._floating_provider_from(
            region, bounds
        )


def is_list_or_tuple(elm):
    return isinstance(elm, list) or isinstance(elm, tuple)


def is_webelement(elm):
    return (
        isinstance(elm, EyesWebElement)
        or isinstance(elm, WebElement)
        or isinstance(getattr(elm, "_element", None), WebElement)
    )
