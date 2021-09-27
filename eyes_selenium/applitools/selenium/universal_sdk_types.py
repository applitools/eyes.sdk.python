from enum import Enum
from json import dumps, loads
from typing import TYPE_CHECKING, Text, Union

import attr
import cattr
import cattr.generation
from six import text_type

from applitools.common import MatchResult, TestResults
from applitools.common.utils.json_utils import (
    attr_from_json,
    to_json,
    underscore_to_camelcase,
)

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Union

    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement

    from applitools.common import Configuration

    from . import EyesWebElement
    from .fluent import SeleniumCheckSettings
    from .fluent.selenium_check_settings import SeleniumCheckSettingsValues


class AccessibilityLevel(Enum):
    AA = "AA"
    AAA = "AAA"


class AccessibilityGuidelinesVersion(Enum):
    WCAG_2_0 = "WCAG_2_0"
    WCAG_2_1 = "WCAG_2_1"


class AccessibilityRegionType(Enum):
    IGNORE_CONTRAST = "IgnoreContrast"
    REGULAR_TEXT = "RegularText"
    LARGE_TEXT = "LargeText"
    BOLD_TEXT = "BoldText"
    GRAPHICAL_OBJECT = "GraphicalObject"


class MatchLevel(Enum):
    NONE = "None"
    LAYOUT = "Layout"
    LAYOUT1 = "Layout1"
    LAYOUT2 = "Layout2"
    CONTENT = "Content"
    STRICT = "Strict"
    EXACT = "Exact"


@attr.s
class Location(object):
    x = attr.ib(type=int)
    y = attr.ib(type=int)


@attr.s
class Size(object):
    width = attr.ib(type=int)
    height = attr.ib(type=int)


@attr.s
class Region(Location, Size):
    pass


@attr.s
class AccessibilityRegion(object):
    region = attr.ib()  # type: Region
    type = attr.ib(default=None)  # type: Optional[AccessibilityRegionType]


@attr.s
class FloatingRegion(object):
    region = attr.ib()  # type: Region
    max_up_offset = attr.ib()  # type: Optional[int]
    max_down_offset = attr.ib()  # type: Optional[int]
    max_left_offset = attr.ib()  # type: Optional[int]
    max_right_offset = attr.ib()  # type: Optional[int]


@attr.s
class TransformedDriver(object):
    session_id = attr.ib()  # type: Text
    server_url = attr.ib()  # type: Text
    capabilities = attr.ib()  # type: Dict[Text, Any]


@attr.s
class TransformedElement(object):
    element_id = attr.ib(type=text_type)


@attr.s
class TransformedSelector(object):
    selector = attr.ib()  # type: Union[Text, TransformedSelector]
    type = attr.ib(default=None)  # type: Optional[Text]
    shadow = attr.ib(default=None)  # type: Union[Text, TransformedSelector]
    frame = attr.ib(default=None)  # type: Union[Text, TransformedSelector]


@attr.s
class MatchSettingsExact(object):
    min_diff_intensity = attr.ib()  # type: int
    min_diff_width = attr.ib()  # type: int
    min_diff_height = attr.ib()  # type: int
    match_threshold = attr.ib()  # type: int


@attr.s
class AccessibilitySettings(object):
    level = attr.ib(
        default=None, type=AccessibilityLevel
    )  # type: Optional[AccessibilityLevel]
    guidelines_version = attr.ib(
        default=None, type=AccessibilityGuidelinesVersion
    )  # type: Optional[AccessibilityGuidelinesVersion]


ElementReference = Union[TransformedElement, TransformedSelector]
RegionReference = Union[TransformedElement, TransformedSelector, Region]
FrameReference = Union[TransformedElement, TransformedSelector, int, Text]


@attr.s
class MatchSettings(object):
    exact = attr.ib(default=None)  # type: Optional[MatchSettingsExact]
    match_level = attr.ib(default=None)  # type: Optional[MatchLevel]
    send_dom = attr.ib(default=None)  # type: Optional[bool]
    use_dom = attr.ib(default=None)  # type: Optional[bool]
    enable_patterns = attr.ib(default=None)  # type: Optional[bool]
    ignore_caret = attr.ib(default=None)  # type: Optional[bool]
    ignore_displacements = attr.ib(default=None)  # type: Optional[bool]
    accessibility_settings = attr.ib(
        default=None
    )  # type: Optional[AccessibilitySettings]
    ignore_regions = attr.ib(default=None)  # type: Optional[List[RegionReference]]
    layout_regions = attr.ib(default=None)  # type: Optional[List[RegionReference]]
    strict_regions = attr.ib(default=None)  # type: Optional[List[RegionReference]]
    content_regions = attr.ib(default=None)  # type: Optional[List[RegionReference]]
    floating_regions = attr.ib(
        default=None
    )  # type: Optional[List[Union[Region, FloatingRegion]]]
    accessibility_regions = attr.ib(
        default=None
    )  # type: Optional[List[Union[Region, AccessibilityRegion]]]


@attr.s
class ContextReference(object):
    frame = attr.ib()  # type: FrameReference
    scroll_root_element = attr.ib(default=None)  # type: Optional[ElementReference]


@attr.s
class ScreenshotSettings(object):
    region = attr.ib(default=None)  # type: Optional[RegionReference]
    frames = attr.ib(default=None)  # type: Optional[List]
    scroll_root_element = attr.ib(default=None)  # type: Optional[ElementReference]
    fully = attr.ib(default=None)  # type: Optional[bool]


@attr.s
class CheckSettingsHooks(object):
    before_capture_screenshot = attr.ib()  # type: Text


@attr.s
class CheckSettings(MatchSettings, ScreenshotSettings):
    name = attr.ib(default=None)  # type: Optional[Text]
    disable_browser_fetching = attr.ib(default=None)  # type: Optional[bool]
    layout_breakpoints = attr.ib(default=None)  # type: Optional[bool, List[int]]
    visual_grid_options = attr.ib(default=None)  # type: Dict[Text, Any]
    hooks = attr.ib(default=None)  # type: Optional[CheckSettingsHooks]
    render_id = attr.ib(default=None)  # type: Optional[Text]
    variation_group_id = attr.ib(default=None)  # type: Optional[Text]
    timeout = attr.ib(default=None)  # type: Optional[int]


def marshal_webdriver_ref(driver):
    # type: (WebDriver) -> dict
    return {
        "serverUrl": driver.command_executor._url,  # noqa
        "sessionId": driver.session_id,
        "capabilities": driver.capabilities,
    }


def marshal_webelement_ref(webelement):
    # type: (Union[WebElement, EyesWebElement]) -> TransformedElement
    return TransformedElement(webelement._id)


def marshal_configuration(configuration):
    # type: (Configuration) -> dict
    return loads(to_json(configuration))


def marshal_check_settings_region(values):
    # type: (SeleniumCheckSettingsValues) -> RegionReference
    if values.target_selector:
        by, selector = values.target_selector
        return TransformedSelector(selector=selector, type=by)
    elif values.target_element:
        return marshal_webelement_ref(values.target_element)
    elif values.selector:
        return TransformedSelector(
            selector=values.selector.selector, type=values.selector.type
        )


def marshal_check_settings(check_settings):
    # type: (SeleniumCheckSettings) -> dict
    values = check_settings.values
    check_settings = CheckSettings()
    check_settings.region = marshal_check_settings_region(
        values
    )  # or target_selector or target_element or selector
    check_settings.timeout = values.timeout
    check_settings.ignore_caret = values.ignore_caret
    check_settings.stitch_content = values.stitch_content
    check_settings.match_level = values.match_level
    check_settings.name = values.name
    check_settings.send_dom = values.send_dom
    check_settings.use_dom = values.use_dom
    check_settings.enable_patterns = values.enable_patterns
    check_settings.ignore_displacements = values.ignore_displacements

    check_settings.layout_regions = values.layout_regions
    check_settings.strict_regions = values.strict_regions
    check_settings.content_regions = values.content_regions
    check_settings.floating_regions = values.floating_regions
    check_settings.accessibility_regions = values.accessibility_regions
    check_settings.variation_group_id = values.variation_group_id

    check_settings.scroll_root_element = (
        values.scroll_root_element
    )  # or scroll_root_element_selector
    check_settings.frames = None  # values.frame_chain
    check_settings.hooks = values.script_hooks
    check_settings.visual_grid_options = values.visual_grid_options
    check_settings.disable_browser_fetching = values.disable_browser_fetching
    check_settings.layout_breakpoints = values.layout_breakpoints
    # check_settings.ocr_region
    return _keys_underscore_to_camel_remove_none(cattr.unstructure(check_settings))


def demarshal_match_result(results_dict):
    # type: (dict) -> MatchResult
    return attr_from_json(dumps(results_dict), MatchResult)


def demarshal_test_results(results_dict_list):
    # type: (List[dict]) -> List[TestResults]
    return [attr_from_json(dumps(r), TestResults) for r in results_dict_list]


def _keys_underscore_to_camel_remove_none(obj):
    if isinstance(obj, dict):
        return {
            underscore_to_camelcase(k): _keys_underscore_to_camel_remove_none(v)
            for k, v in obj.items()
            if v is not None
        }
    elif isinstance(obj, list):
        return [underscore_to_camelcase(i) for i in obj]
    else:
        return obj
