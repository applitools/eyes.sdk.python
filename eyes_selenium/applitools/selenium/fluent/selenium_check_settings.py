from __future__ import unicode_literals

from typing import TYPE_CHECKING, List, Text, Tuple, Union, overload

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
    RegionByCssSelector,
    RegionByElement,
)

if TYPE_CHECKING:
    from applitools.common.visual_grid import VisualGridSelector
    from applitools.common.utils.custom_types import (
        FrameReference,
        AnyWebElement,
        FrameNameOrId,
        FrameIndex,
        BySelector,
        CssSelector,
    )

BEFORE_CAPTURE_SCREENSHOT = "beforeCaptureScreenshot"


@attr.s
class FrameLocator(object):
    frame_element = attr.ib(default=None)  # type: AnyWebElement
    frame_selector = attr.ib(default=None)  # type: CssSelector
    frame_name_or_id = attr.ib(default=None)  # type: FrameNameOrId
    frame_index = attr.ib(default=None)  # type: FrameIndex
    scroll_root_selector = attr.ib(default=None)  # type: CssSelector
    scroll_root_element = attr.ib(default=None)  # type: AnyWebElement


@attr.s
class SeleniumCheckSettingsValues(CheckSettingsValues):
    # hide_caret = attr.ib(init=False, default=None)
    scroll_root_element = attr.ib(init=False, default=None)  # type: EyesWebElement
    scroll_root_selector = attr.ib(init=False, default=None)  # type: CssSelector
    target_selector = attr.ib(init=False, default=None)  # type: CssSelector
    target_element = attr.ib(init=False, default=None)  # type: EyesWebElement
    frame_chain = attr.ib(init=False, factory=list)  # type: List[FrameLocator]

    # for Rendering Grid
    selector = attr.ib(default=None)  # type: VisualGridSelector
    script_hooks = attr.ib(factory=dict)  # type: dict

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
    elif by == By.CLASS_NAME:
        value = ".%s" % value
    elif by == By.NAME:
        value = '[name="%s"]' % value
    elif by in [By.XPATH, By.CSS_SELECTOR, By.TAG_NAME]:
        value = value
    else:
        raise TypeError("By {} is not supported".format(by))
    return value


@attr.s
class SeleniumCheckSettings(CheckSettings):
    values = attr.ib(
        init=False, factory=SeleniumCheckSettingsValues
    )  # type: SeleniumCheckSettingsValues

    _region = attr.ib(default=None)
    _frame = attr.ib(default=None)

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
    def region(self, by_selector):
        # type: (BySelector) -> SeleniumCheckSettings
        pass

    def region(self, region):  # noqa
        if isinstance(region, Region):
            self.values.target_region = region
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

    @overload  # noqa
    def frame(self, frame_name_or_id):
        # type: (FrameNameOrId) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def frame(self, frame_element):
        # type: (AnyWebElement) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def frame(self, frame_index):
        # type: (FrameIndex) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def frame(self, frame_by_selector):
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
            selector = _css_selector_from_(by, value)
            fl.frame_selector = selector
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
            logger.debug("{name}: IgnoreRegionByCssSelector".format(name=method_name))
            return RegionByCssSelector(region)
        if is_list_or_tuple(region):
            by, val = region
            sel = _css_selector_from_(by, val)
            logger.debug("{name}: IgnoreRegionByCssSelector".format(name=method_name))
            return RegionByCssSelector(sel)
        elif is_webelement(region):
            logger.debug("{name}: IgnoreRegionByElement".format(name=method_name))
            return RegionByElement(region)
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

    @overload  # noqa
    def scroll_root_element(self, element):
        # type: (AnyWebElement) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def scroll_root_element(self, selector):
        # type: (CssSelector) -> SeleniumCheckSettings
        pass

    def scroll_root_element(self, element_or_selector):  # noqa
        if isinstance(element_or_selector, basestring):
            self._set_scroll_root_selector(element_or_selector)
        elif is_webelement(element_or_selector):
            self._set_scroll_root_element(element_or_selector)
        return self

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
    return (
        isinstance(elm, EyesWebElement)
        or isinstance(elm, WebElement)
        or isinstance(getattr(elm, "_element", None), WebElement)
    )
