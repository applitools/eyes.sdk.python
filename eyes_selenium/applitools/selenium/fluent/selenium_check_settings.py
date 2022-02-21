from __future__ import unicode_literals

from typing import TYPE_CHECKING, List, Optional, Text, Tuple, Union, overload

import attr
from six import string_types

from applitools.common.accessibility import AccessibilityRegionType
from applitools.common.geometry import AccessibilityRegion, Region
from applitools.common.ultrafastgrid import VisualGridOption
from applitools.common.utils import argument_guard
from applitools.common.utils.json_utils import JsonInclude
from applitools.common.validators import is_list_or_tuple, is_webelement
from applitools.core.fluent import CheckSettings, CheckSettingsValues

from .region import (
    AccessibilityRegionBySelector,
    FloatingRegionBySelector,
    RegionBySelector,
)
from .target_path import Locator, TargetPath

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import (
        FLOATING_VALUES,
        AnyWebElement,
        BySelector,
        CodedRegionPadding,
        CssSelector,
        FrameIndex,
        FrameNameOrId,
    )
    from applitools.core.extract_text import OCRRegion

BEFORE_CAPTURE_SCREENSHOT = "beforeCaptureScreenshot"


@attr.s
class FrameLocator(object):
    frame_locator = attr.ib(default=None)  # type: Locator
    frame_name_or_id = attr.ib(default=None)  # type: FrameNameOrId
    frame_index = attr.ib(default=None)  # type: FrameIndex
    scroll_root_locator = attr.ib(default=None)  # type: Locator


@attr.s
class LazyLoadOptions(object):
    scroll_length = attr.ib(default=None)
    waiting_time = attr.ib(default=None)
    page_height = attr.ib(default=None)


@attr.s
class SeleniumCheckSettingsValues(CheckSettingsValues):
    # hide_caret = attr.ib(init=False, default=None)
    scroll_root_locator = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, init=False, default=None
    )  # type: Locator
    target_locator = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, init=False, default=None
    )  # type: Locator
    frame_chain = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, init=False, factory=list
    )  # type: List[FrameLocator]

    script_hooks = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, factory=dict
    )  # type: dict
    visual_grid_options = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=()
    )  # type: Tuple[VisualGridOption]
    disable_browser_fetching = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=None
    )  # type: Optional[bool]
    ocr_region = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, init=False, default=None
    )  # type: Optional[OCRRegion]
    layout_breakpoints = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=None
    )  # type: Optional[Union[bool, List[int]]]
    lazy_load = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=None
    )  # type: Optional[LazyLoadOptions]

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
        return self.target_region is None and self.target_locator is None


@attr.s
class SeleniumCheckSettings(CheckSettings):
    values = attr.ib(
        init=False, factory=SeleniumCheckSettingsValues
    )  # type: SeleniumCheckSettingsValues

    _region = attr.ib(default=None)
    _frame = attr.ib(default=None)

    @overload  # noqa
    def layout(self, *by, **kwargs):
        # type: (*BySelector,**Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def layout(self, *element, **kwargs):
        # type: (*AnyWebElement,**Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def layout(self, *css_selector, **kwargs):
        # type: (*CssSelector,**Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def layout(self, *target_path, **kwargs):
        # type: (*Locator,**Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def layout(self, *region, **kwargs):
        # type: (*Region,**Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    def layout(self, *region, **kwargs):  # noqa
        """
        Adds one or more layout regions. And allow to set up paddings for them.

        :param kwargs: accepts `padding` parameter where there region paddings
         could be specified.
         Example of definition: `padding=dict(top=10, left=10, right=11, bottom=12)`
          where each keys are optional
        """
        return super(SeleniumCheckSettings, self).layout(*region, **kwargs)

    @overload  # noqa
    def strict(self, *by, **kwargs):
        # type: (*BySelector, **Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def strict(self, *element, **kwargs):
        # type: (*AnyWebElement,**Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def strict(self, *css_selector, **kwargs):
        # type: (*CssSelector,**Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def strict(self, *target_path, **kwargs):
        # type: (*Locator,**Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def strict(self, *region, **kwargs):
        # type: (*Region, **Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    def strict(self, *region, **kwargs):  # noqa
        """
        Adds one or more strict regions. And allow to set up paddings for them.

        :param kwargs: accepts `padding` parameter where there region paddings
         could be specified.
         Example of definition: `padding=dict(top=10, left=10, right=11, bottom=12)`
          where each keys are optional
        """
        return super(SeleniumCheckSettings, self).strict(*region, **kwargs)

    @overload  # noqa
    def content(self, *by, **kwargs):
        # type: (*BySelector, **Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def content(self, *element, **kwargs):
        # type: (*AnyWebElement,**Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def content(self, *css_selector, **kwargs):
        # type: (*CssSelector, **Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def content(self, *target_path, **kwargs):
        # type: (*Locator, **Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def content(self, *region, **kwargs):
        # type: (*Region, **Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    def content(self, *region, **kwargs):  # noqa
        """
        Adds one or more content regions. And allow to set up paddings for them.

        :param kwargs: accepts `padding` parameter where there region paddings
         could be specified.
         Example of definition: `padding=dict(top=10, left=10, right=11, bottom=12)`
          where each keys are optional
        """
        return super(SeleniumCheckSettings, self).content(*region, **kwargs)

    @overload  # noqa
    def ignore(self, *by, **kwargs):
        # type: (*BySelector, **Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def ignore(self, *element, **kwargs):
        # type: (*AnyWebElement,**Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def ignore(self, *css_selector, **kwargs):
        # type: (*CssSelector, **Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def ignore(self, *target_path, **kwargs):
        # type: (*Locator, **Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def ignore(self, *region, **kwargs):
        # type: (*Region, **Optional[CodedRegionPadding]) -> SeleniumCheckSettings
        pass

    def ignore(self, *region, **kwargs):  # noqa
        """
        Adds one or more ignore regions. And allow to set up paddings for them.

        :param kwargs: accepts `padding` parameter where there region paddings
         could be specified.
         Example of definition: `padding=dict(top=10, left=10, right=11, bottom=12)`
          where each keys are optional
        """
        return super(SeleniumCheckSettings, self).ignore(*region, **kwargs)

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
    def accessibility(self, target_path, type):  # noqa
        # type:(Locator, AccessibilityRegionType) -> SeleniumCheckSettings
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
    def shadow(self, css_selector):  # noqa
        # type: (CssSelector) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def shadow(self, css_selector):  # noqa
        # type: (Locator) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def shadow(self, element):  # noqa
        # type: (AnyWebElement) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def shadow(self, by):  # noqa
        # type: (BySelector) -> SeleniumCheckSettings
        pass

    def shadow(self, shadow):  # noqa
        # type:(...) -> SeleniumCheckSettings
        path = self.values.target_locator or TargetPath
        if isinstance(shadow, Locator):
            self.values.target_locator = shadow
        elif is_list_or_tuple(shadow):
            self.values.target_locator = path.shadow(*shadow)
        else:
            self.values.target_locator = path.shadow(shadow)
        return self

    @overload  # noqa
    def region(self, region):  # noqa
        # type: (Region) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def region(self, css_selector):  # noqa
        # type: (CssSelector) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def region(self, target_path):  # noqa
        # type: (Locator) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def region(self, element):  # noqa
        # type: (AnyWebElement) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def region(self, by):  # noqa
        # type: (BySelector) -> SeleniumCheckSettings
        pass

    def region(self, region):  # noqa
        # type:(...) -> SeleniumCheckSettings
        if isinstance(region, Region):
            self.values.target_region = region
        elif is_list_or_tuple(region):
            path = self.values.target_locator or TargetPath
            self.values.target_locator = path.region(*region)
        elif isinstance(region, string_types) or is_webelement(region):
            path = self.values.target_locator or TargetPath
            self.values.target_locator = path.region(region)
        elif isinstance(region, Locator):
            self.values.target_locator = region
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

    @overload  # noqa
    def frame(self, target_path):
        # type: (Locator) -> SeleniumCheckSettings
        pass

    def frame(self, frame):  # noqa
        # type:(...) -> SeleniumCheckSettings
        fl = FrameLocator()
        if isinstance(frame, int):
            fl.frame_index = frame
        elif isinstance(frame, string_types):
            fl.frame_name_or_id = frame
        elif is_webelement(frame):
            fl.frame_locator = TargetPath.frame(frame)
        elif is_list_or_tuple(frame):
            fl.frame_locator = TargetPath.frame(*frame)
        elif isinstance(frame, Locator):
            fl.frame_locator = frame
        else:
            raise TypeError("frame method called with argument of unknown type!")
        self.values.frame_chain.append(fl)
        return self

    def before_render_screenshot_hook(self, hook):
        # type: (Text) -> SeleniumCheckSettings
        self.values.script_hooks[BEFORE_CAPTURE_SCREENSHOT] = hook
        return self

    def _region_provider_from(self, region, method_name, padding):
        if isinstance(region, string_types) or is_webelement(region):
            return RegionBySelector(TargetPath.region(region), padding)
        elif is_list_or_tuple(region):
            return RegionBySelector(TargetPath.region(*region), padding)
        elif isinstance(region, Locator):
            return RegionBySelector(region, padding)
        return super(SeleniumCheckSettings, self)._region_provider_from(
            region, method_name, padding
        )

    def _set_scroll_root_locator(self, target_path):
        if len(self.values.frame_chain) == 0:
            self.values.scroll_root_locator = target_path
        else:
            self.values.frame_chain[-1].scroll_root_locator = target_path

    @overload  # noqa
    def scroll_root_element(self, element):
        # type: (AnyWebElement) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def scroll_root_element(self, selector):
        # type: (CssSelector) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def scroll_root_element(self, target_path):
        # type: (Locator) -> SeleniumCheckSettings
        pass

    @overload  # noqa
    def scroll_root_element(self, by):
        # type: (BySelector) -> SeleniumCheckSettings
        pass

    def scroll_root_element(self, element_or_selector):  # noqa
        if isinstance(element_or_selector, string_types) or is_webelement(
            element_or_selector
        ):
            self._set_scroll_root_locator(TargetPath.region(element_or_selector))
        elif is_list_or_tuple(element_or_selector):
            self._set_scroll_root_locator(TargetPath.region(*element_or_selector))
        elif isinstance(element_or_selector, Locator):
            self._set_scroll_root_locator(element_or_selector)
        else:
            raise TypeError("Unsupported type of scroll root element")
        return self

    def _floating_provider_from(self, region, bounds):
        if isinstance(region, string_types) or is_webelement(region):
            return FloatingRegionBySelector(TargetPath.region(region), bounds)
        elif is_list_or_tuple(region):
            return FloatingRegionBySelector(TargetPath.region(*region), bounds)
        elif isinstance(region, Locator):
            return FloatingRegionBySelector(region, bounds)
        return super(SeleniumCheckSettings, self)._floating_provider_from(
            region, bounds
        )

    def _accessibility_provider_from(self, region, accessibility_region_type):
        if isinstance(region, string_types) or is_webelement(region):
            return AccessibilityRegionBySelector(
                TargetPath.region(region), accessibility_region_type
            )
        elif is_list_or_tuple(region):
            return AccessibilityRegionBySelector(
                TargetPath.region(*region), accessibility_region_type
            )
        elif isinstance(region, Locator):
            return AccessibilityRegionBySelector(region, accessibility_region_type)
        return super(SeleniumCheckSettings, self)._accessibility_provider_from(
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

    @overload
    def layout_breakpoints(self, enabled):
        # type: (bool) -> SeleniumCheckSettings
        pass

    @overload
    def layout_breakpoints(self, *breakpoints):
        # type: (*int) -> SeleniumCheckSettings
        pass

    def layout_breakpoints(self, enabled_or_first, *rest):
        if isinstance(enabled_or_first, bool):
            self.values.layout_breakpoints = enabled_or_first
        elif isinstance(enabled_or_first, int):
            self.values.layout_breakpoints = [enabled_or_first] + list(rest)
        else:
            raise TypeError(
                "{} is not an instance of bool or int".format(enabled_or_first)
            )
        return self

    def lazy_load(self, scroll_length=300, waiting_time=2000, page_height=15000):
        # type: (int, int, int) -> SeleniumCheckSettings
        lazy_load = LazyLoadOptions(scroll_length, waiting_time, page_height)
        self.values.lazy_load = lazy_load
        return self

    @property
    def is_check_window(self):
        # type: () -> bool
        return self.values.is_target_empty
