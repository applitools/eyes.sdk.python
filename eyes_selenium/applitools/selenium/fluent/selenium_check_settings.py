from __future__ import unicode_literals

from typing import TYPE_CHECKING, List, Optional, Text, Tuple, overload

import attr
from selenium.webdriver.common.by import By

from applitools.common import logger
from applitools.common.accessibility import AccessibilityRegionType
from applitools.common.geometry import AccessibilityRegion, Region
from applitools.common.ultrafastgrid import VisualGridOption
from applitools.common.utils import argument_guard
from applitools.common.utils.compat import basestring
from applitools.core.fluent import CheckSettings, CheckSettingsValues
from applitools.selenium.validators import is_list_or_tuple, is_webelement
from applitools.selenium.webelement import EyesWebElement

from .region import (
    AccessibilityRegionByElement,
    AccessibilityRegionBySelector,
    FloatingRegionByElement,
    FloatingRegionBySelector,
    RegionByElement,
    RegionBySelector,
)

if TYPE_CHECKING:
    from applitools.common.ultrafastgrid import VisualGridSelector
    from applitools.common.utils.custom_types import (
        FLOATING_VALUES,
        AnyWebElement,
        BySelector,
        CssSelector,
        FrameIndex,
        FrameNameOrId,
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
    visual_grid_options = attr.ib(default=())  # type: Tuple[VisualGridOption]
    disable_browser_fetching = attr.ib(default=None)  # type: Optional[bool]

    @property
    def size_mode(self):
        if self.is_target_empty:
            if self.stitch_content:
                return "full-page"
            return "viewport"
        elif self.target_region:
            return "region"
        elif self.stitch_content:
            return "full-selector"
        return "selector"

    @property
    def is_target_empty(self):
        # type: () -> bool
        return (
            self.target_region is None
            and self.target_selector is None
            and self.target_element is None
        )


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
    def accessibility(self, region):  # noqa
        # type:(AccessibilityRegion) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def accessibility(self, css_selector, type):  # noqa
        # type:(CssSelector, AccessibilityRegionType) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def accessibility(self, by, type):  # noqa
        # type:(BySelector, AccessibilityRegionType) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def accessibility(self, element, type):  # noqa
        # type:(AnyWebElement, AccessibilityRegionType) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def accessibility(self, region, type):  # noqa
        # type:(Region, AccessibilityRegionType) -> SeleniumCheckSettings
        pass

    def accessibility(self, region, type=None):  # noqa
        # type:(...) -> SeleniumCheckSettings
        return super(SeleniumCheckSettings, self).accessibility(region, type)

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
        # type:(...) -> SeleniumCheckSettings
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
        # type:(...) -> SeleniumCheckSettings
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

    def _accessibility_provider_from(self, region, accessibility_region_type):
        if is_webelement(region):
            logger.debug("accessibility: AccessibilityRegionByElement")
            return AccessibilityRegionByElement(region, accessibility_region_type)
        if isinstance(region, basestring):
            logger.debug("accessibility: AccessibilityRegionBySelector")
            return AccessibilityRegionBySelector(
                By.CSS_SELECTOR, region, accessibility_region_type
            )
        if is_list_or_tuple(region):
            by, value = region
            logger.debug("accessibility: AccessibilityRegionBySelector")
            return AccessibilityRegionBySelector(by, value, accessibility_region_type)
        return super(SeleniumCheckSettings, self)._floating_provider_from(
            region, accessibility_region_type
        )

    def visual_grid_options(self, *options):
        # type: (*VisualGridOption) -> SeleniumCheckSettings
        argument_guard.are_(options, VisualGridOption)
        self.values.visual_grid_options = options
        return self

    def disable_browser_fetching(self, disable=True):
        # type: (bool) -> SeleniumCheckSettings
        self.values.disable_browser_fetching = disable
        return self

    @property
    def is_check_window(self):
        # type: () -> bool
        return bool(self.values.is_target_empty and self.values.selector is None)
