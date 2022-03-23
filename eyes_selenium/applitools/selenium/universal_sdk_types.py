from json import dumps
from typing import TYPE_CHECKING, Iterable, Text, Tuple, Union

import attr
import cattr

from applitools.common import (
    AccessibilityGuidelinesVersion,
    AccessibilityLevel,
    AccessibilityRegionType,
)
from applitools.common import ChromeEmulationInfo as ApiChromeEmulationInfo
from applitools.common import DesktopBrowserInfo, DeviceName, FloatingBounds
from applitools.common import IosDeviceInfo
from applitools.common import IosDeviceInfo as ApiIosDeviceInfo
from applitools.common import IosDeviceName, IosVersion, MatchLevel, MatchResult
from applitools.common import Region as APIRegion
from applitools.common import (
    RenderBrowserInfo,
    ScreenOrientation,
    SessionType,
    StitchMode,
    TestResults,
    VisualGridOption,
)
from applitools.common.utils.json_utils import attr_from_json, underscore_to_camelcase

from ..common.geometry import Rectangle
from ..core import (
    FloatingRegionByRectangle,
    GetRegion,
    RegionByRectangle,
    TextRegionSettings,
    VisualLocatorSettings,
)
from ..core.fluent import AccessibilityRegionByRectangle
from ..core.locators import VisualLocatorSettingsValues
from .fluent import FloatingRegionBySelector, RegionBySelector
from .fluent.region import AccessibilityRegionBySelector
from .fluent.target_path import Locator

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Union

    from selenium.webdriver.remote.webdriver import WebDriver, WebElement

    from applitools.common import BatchInfo, ImageMatchSettings, ProxySettings
    from applitools.common.selenium import BrowserType, Configuration
    from applitools.core.batch_close import _EnabledBatchClose

    from ..common.utils.custom_types import ViewPort
    from . import OCRRegion
    from .fluent import FrameLocator, SeleniumCheckSettings
    from .fluent.selenium_check_settings import SeleniumCheckSettingsValues


@attr.s
class CustomProperty(object):
    name = attr.ib()  # type: Text
    value = attr.ib()  # type: Text

    @classmethod
    def convert(cls, properties):
        # type: (List[Dict[Text, Text]]) -> List[CustomProperty]
        if properties:
            return [cls(p["name"], p["value"]) for p in properties]
        else:
            return []


@attr.s
class Batch(object):
    id = attr.ib(default=None)  # type: Optional[Text]
    name = attr.ib(default=None)  # type: Optional[Text]
    sequence_name = attr.ib(default=None)  # type: Optional[Text]
    started_at = attr.ib(default=None)  # type: Optional[Text]
    notify_on_completion = attr.ib(default=None)  # type: Optional[bool]
    properties = attr.ib(default=None)  # type: Optional[List[CustomProperty]]

    @classmethod
    def convert(cls, batch_info):
        # type: (Optional[BatchInfo]) -> Optional[Batch]
        if batch_info:
            if batch_info.started_at:
                started_at = batch_info.started_at.strftime("%Y-%m-%dT%H:%M:%SZ")
            else:
                started_at = None
            return cls(
                batch_info.id,
                batch_info.name,
                batch_info.sequence_name,
                started_at,
                batch_info.notify_on_completion,
                # TODO: Verify
                CustomProperty.convert(batch_info.properties),
            )
        else:
            return None


@attr.s
class Location(object):
    x = attr.ib()  # type: float
    y = attr.ib()  # type: float


@attr.s
class Size(object):
    width = attr.ib()  # type: float
    height = attr.ib()  # type: float

    @classmethod
    def convert_viewport(cls, viewport):
        # type: (Optional[ViewPort]) -> Optional[Size]
        if viewport:
            return cls(viewport["width"], viewport["height"])
        else:
            return None


@attr.s
class Region(Location, Size):
    @classmethod
    def convert(cls, rect):
        # type: (Union[Region, Rectangle]) -> Region
        return cls(rect.left, rect.top, rect.width, rect.height)


@attr.s
class ImageCropRegion(Region):
    pass


@attr.s
class ImageCropRect(object):
    top = attr.ib()  # type: float
    right = attr.ib()  # type: float
    bottom = attr.ib()  # type: float
    left = attr.ib()  # type: float


@attr.s
class AccessibilityRegion(object):
    region = attr.ib()  # type: Region
    type = attr.ib(default=None)  # type: Optional[AccessibilityRegionType]

    @classmethod
    def convert(cls, region, type_):
        # type: (Region, Optional[AccessibilityRegionType]) -> AccessibilityRegion
        return cls(region, type_)


@attr.s
class FloatingRegion(object):
    region = attr.ib()  # type: Region
    max_up_offset = attr.ib()  # type: Optional[int]
    max_down_offset = attr.ib()  # type: Optional[int]
    max_left_offset = attr.ib()  # type: Optional[int]
    max_right_offset = attr.ib()  # type: Optional[int]

    @classmethod
    def convert(cls, region, bounds):
        # type: (Region, FloatingBounds) -> FloatingRegion
        return cls(
            region,
            bounds.max_up_offset,
            bounds.max_down_offset,
            bounds.max_left_offset,
            bounds.max_right_offset,
        )


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


@attr.s
class DesktopBrowserRenderer(object):
    width = attr.ib()  # type: float
    height = attr.ib()  # type: float
    name = attr.ib(default=None)  # type: Optional[BrowserType]


@attr.s
class ChromeEmulationInfo(object):
    device_name = attr.ib()  # type: DeviceName
    screen_orientation = attr.ib(default=None)  # type: Optional[ScreenOrientation]


@attr.s
class ChromeEmulationDeviceRenderer(object):
    chrome_emulation_info = attr.ib()  # type: ChromeEmulationInfo


@attr.s
class IosDeviceInfo(object):
    device_name = attr.ib()  # type: IosDeviceName
    ios_version = attr.ib(default=None)  # type: Optional[IosVersion]
    screen_orientation = attr.ib(default=None)  # type: Optional[ScreenOrientation]


@attr.s
class IOSDeviceRenderer(object):
    ios_device_info = attr.ib()  # type: IosDeviceInfo


@attr.s
class FileLogHandler(object):
    type = attr.ib(default="file")
    filename = attr.ib(default=None)  # type: Optional[Text]
    append = attr.ib(default=None)  # type: Optional[bool]


@attr.s
class ConsoleLogHandler(object):
    type = attr.ib(default="console")


@attr.s
class DebugScreenshotHandler(object):
    save = attr.ib()  # type: bool
    path = attr.ib(default=None)  # type: Optional[Text]
    prefix = attr.ib(default=None)  # type: Optional[Text]


LogHandler = Union[FileLogHandler, ConsoleLogHandler]
ElementReference = dict
RegionReference = Union[ElementReference, Region]
FrameReference = Union[ElementReference, int, Text]
BrowserInfo = Union[
    DesktopBrowserRenderer, ChromeEmulationDeviceRenderer, IOSDeviceRenderer
]


def record_convert(records):
    # type: (Optional[Iterable[VisualGridOption]]) -> Optional[Dict[Text, Any]]
    if records:
        return {r.key: r.value for r in records}
    else:
        return None


def optional_element_reference_convert(is_selenium, locator=None):
    # type: (bool, Optional[Locator]) -> Optional[ElementReference]
    if locator is None:
        return None
    else:
        return locator.to_dict(is_selenium)


def frame_reference_convert(is_selenium, locator=None, number=None, name=None):
    # type: (bool, Optional[Locator], Optional[int], Optional[Text]) -> FrameReference
    if name is not None:
        return name
    elif number is not None:
        return number
    else:
        return locator.to_dict(is_selenium)


def browsers_info_convert(browsers_info):
    # type: (List[RenderBrowserInfo]) -> List[BrowserInfo]
    result = []
    for bi in browsers_info:
        if isinstance(bi, DesktopBrowserInfo):
            result.append(DesktopBrowserRenderer(bi.width, bi.height, bi.browser))
        elif isinstance(bi, ApiChromeEmulationInfo):
            result.append(
                ChromeEmulationDeviceRenderer(
                    ChromeEmulationInfo(bi.device_name, bi.screen_orientation)
                )
            )
        elif isinstance(bi, ApiIosDeviceInfo):
            result.append(
                IOSDeviceRenderer(
                    IosDeviceInfo(bi.device_name, bi.ios_version, bi.screen_orientation)
                )
            )
        else:
            raise RuntimeError("Unexpected BrowserInfo type", type(bi))
    return result


def target_reference_convert(is_selenium, values):
    # type: (bool, SeleniumCheckSettingsValues) -> Optional[RegionReference]
    if values.target_locator:
        return values.target_locator.to_dict(is_selenium)
    elif values.target_region:
        return Region.convert(values.target_region)
    else:
        return None


def ocr_target_convert(is_selenium, target):
    # type:(bool, Union[Locator, WebElement, Region]) -> RegionReference
    if isinstance(target, Locator):
        return target.to_dict(is_selenium)
    else:
        return Region.convert(target)


def region_references_convert(is_selenium, regions):
    # type: (bool, List[GetRegion]) -> List[RegionReference]
    results = []
    for r in regions:
        if isinstance(r, RegionBySelector):
            results.append(r._target_path.to_dict(is_selenium))  # noqa
        elif isinstance(r, RegionByRectangle):
            results.append(Region.convert(r._region))  # noqa
        else:
            raise RuntimeError("Unexpected region type", type(r))
    return results


def floating_region_references_convert(is_selenium, regions):
    # type: (bool, List[GetRegion]) -> List[FloatingRegion]
    results = []
    for r in regions:
        if isinstance(r, FloatingRegionBySelector):
            region = r._target_path.to_dict(is_selenium)  # noqa
            bounds = r._bounds  # noqa
        elif isinstance(r, FloatingRegionByRectangle):
            region, bounds = Region.convert(r._rect), r._bounds  # noqa
        else:
            raise RuntimeError("Unexpected region type", type(r))
        results.append(FloatingRegion.convert(region, bounds))
    return results


def accessibility_region_references_convert(is_selenium, regions):
    # type: (bool, List[GetRegion]) -> List[AccessibilityRegion]
    results = []
    for r in regions:
        if isinstance(r, AccessibilityRegionBySelector):
            region = r._target_path.to_dict(is_selenium)  # noqa
            type_ = r._type  # noqa
        elif isinstance(r, AccessibilityRegionByRectangle):
            region, type_ = Region.convert(r._rect), r._type  # noqa
        else:
            raise RuntimeError("Unexpected region type", type(r))
        results.append(AccessibilityRegion.convert(region, type_))
    return results


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

    @classmethod
    def convert(cls, is_selenium, image_match_settings):
        # type: (bool, Optional[ImageMatchSettings]) -> Optional[MatchSettings]
        if image_match_settings:
            return cls(
                exact=image_match_settings.exact,
                match_level=image_match_settings.match_level,
                send_dom=None,  # TODO: verify
                use_dom=image_match_settings.use_dom,
                enable_patterns=image_match_settings.enable_patterns,
                ignore_caret=image_match_settings.ignore_caret,
                ignore_displacements=image_match_settings.ignore_displacements,
                accessibility_settings=image_match_settings.accessibility_settings,
                ignore_regions=image_match_settings.ignore_regions,  # todo: verify
                layout_regions=image_match_settings.layout_regions,
                strict_regions=image_match_settings.strict_regions,
                content_regions=image_match_settings.content_regions,
                floating_regions=floating_region_references_convert(
                    is_selenium, image_match_settings.floating_match_settings
                ),
                accessibility_regions=accessibility_region_references_convert(
                    is_selenium, image_match_settings.accessibility
                ),
            )
        else:
            return None


@attr.s
class Proxy(object):
    url = attr.ib()  # type: Text
    username = attr.ib(default=None)  # type: Optional[Text]
    password = attr.ib(default=None)  # type: Optional[Text]
    is_http_only = attr.ib(default=None)  # type: Optional[bool]

    @classmethod
    def convert(cls, proxy):
        # type: (Optional[ProxySettings]) -> Proxy
        if proxy:
            return cls(proxy.url, proxy.username, proxy.password)
        else:
            return None


@attr.s
class RemoteEvents(object):
    server_url = attr.ib()  # type: Text
    access_key = attr.ib(default=None)  # type: Optional[Text]
    timeout = attr.ib(default=None)  # type: Optional[int]


@attr.s
class EyesBaseConfig(object):
    logs = attr.ib(default=None)  # type: Optional[LogHandler]
    debug_screenshots = attr.ib(default=None)  # type: Optional[DebugScreenshotHandler]
    agent_id = attr.ib(default=None)  # type: Optional[Text]
    api_key = attr.ib(default=None)  # type: Optional[Text]
    server_url = attr.ib(default=None)  # type: Optional[Text]
    proxy = attr.ib(default=None)  # type: Optional[Proxy]
    is_disabled = attr.ib(default=None)  # type: Optional[bool]
    connection_timeout = attr.ib(default=None)  # type: Optional[int]
    remove_session = attr.ib(default=None)  # type: Optional[bool]
    remote_events = attr.ib(default=None)  # type: Optional[RemoteEvents]


@attr.s
class EyesOpenConfig(object):
    app_name = attr.ib(default=None)  # type: Optional[Text]
    test_name = attr.ib(default=None)  # type: Optional[Text]
    display_name = attr.ib(default=None)  # type: Optional[Text]
    viewport_size = attr.ib(default=None)  # type: Optional[Size]
    session_type = attr.ib(default=None)  # type: Optional[SessionType]
    properties = attr.ib(default=None)  # type: Optional[List[CustomProperty]]
    batch = attr.ib(default=None)  # type: Optional[Batch]
    default_match_settings = attr.ib(default=None)  # type: Optional[MatchSettings]
    host_app = attr.ib(default=None)  # type: Optional[Text]
    host_o_s = attr.ib(default=None)  # type: Optional[Text]
    host_app_info = attr.ib(default=None)  # type: Optional[Text]
    host_o_s_info = attr.ib(default=None)  # type: Optional[Text]
    device_info = attr.ib(default=None)  # type: Optional[Text]
    baseline_env_name = attr.ib(default=None)  # type: Optional[Text]
    environment_name = attr.ib(default=None)  # type: Optional[Text]
    branch_name = attr.ib(default=None)  # type: Optional[Text]
    parent_branch_name = attr.ib(default=None)  # type: Optional[Text]
    baseline_branch_name = attr.ib(default=None)  # type: Optional[Text]
    compare_with_parent_branch = attr.ib(default=None)  # type: Optional[bool]
    ignore_baseline = attr.ib(default=None)  # type: Optional[bool]
    save_failed_tests = attr.ib(default=None)  # type: Optional[bool]
    save_new_tests = attr.ib(default=None)  # type: Optional[bool]
    save_diffs = attr.ib(default=None)  # type: Optional[bool]
    dont_close_batches = attr.ib(default=None)  # type: Optional[bool]


@attr.s
class EyesCheckConfig(object):
    send_dom = attr.ib(default=None)  # type: Optional[bool]
    match_timeout = attr.ib(default=None)  # type: Optional[float]
    force_full_page_screenshot = attr.ib(default=None)  # type: Optional[bool]


@attr.s
class EyesClassicConfig(object):
    wait_before_screenshots = attr.ib(default=None)  # type: Optional[float]
    wait_before_capture = attr.ib(default=None)  # type: Optional[int]
    stitch_mode = attr.ib(default=None)  # type: Optional[StitchMode]
    hide_scrollbars = attr.ib(default=None)  # type: Optional[bool]
    hide_caret = attr.ib(default=None)  # type: Optional[bool]
    stitch_overlap = attr.ib(default=None)  # type: Optional[int]
    scroll_root_element = attr.ib(default=None)  # type: Optional[ElementReference]
    cut = attr.ib(default=None)  # type: Optional[Union[ImageCropRect,ImageCropRegion]]
    rotation = attr.ib(default=None)  # type: Optional[int]
    scale_ratio = attr.ib(default=None)  # type: Optional[float]


@attr.s
class EyesUFGConfig(object):
    concurrent_sessions = attr.ib(default=None)  # type: Optional[int]
    browsers_info = attr.ib(default=None)  # type: Optional[List[BrowserInfo]]
    visual_grid_options = attr.ib(default=None)  # type: Optional[Dict[Text, Any]]
    layout_breakpoints = attr.ib(default=None)  # type: Optional[Union[bool, List[int]]]
    disable_browser_fetching = attr.ib(default=None)  # type: Optional[bool]


@attr.s
class EyesConfig(
    EyesBaseConfig, EyesOpenConfig, EyesCheckConfig, EyesClassicConfig, EyesUFGConfig
):
    @classmethod
    def convert(cls, is_selenium, config):
        # type: (bool, Configuration) -> EyesConfig
        if config.cut_provider:
            cut = ImageCropRect(
                config.cut_provider.header,
                config.cut_provider.right,
                config.cut_provider.footer,
                config.cut_provider.left,
            )
        else:
            cut = None
        return cls(
            # EyesBaseConfig
            logs=None,  # TODO: verify
            debug_screenshots=DebugScreenshotHandler(
                config.save_debug_screenshots,
                config.debug_screenshots_path,
                config.debug_screenshots_prefix,
            ),
            agent_id=config.agent_id,
            api_key=config.api_key,
            server_url=config.server_url,
            proxy=Proxy.convert(config.proxy),
            is_disabled=config.is_disabled,
            connection_timeout=config._timeout,  # TODO: verify
            remove_session=None,  # TODO: verify
            remote_events=None,  # TODO: verify
            # EyesOpenConfig
            app_name=config.app_name,
            test_name=config.test_name,
            display_name=None,  # TODO: verify
            viewport_size=Size.convert_viewport(config.viewport_size),
            session_type=config.session_type,
            properties=CustomProperty.convert(config.properties),
            batch=Batch.convert(config.batch),
            default_match_settings=MatchSettings.convert(
                is_selenium, config.default_match_settings
            ),
            host_app=config.host_app,
            host_o_s=config.host_os,
            host_o_s_info=None,  # TODO: verify
            host_app_info=None,  # TODO: verify
            device_info=None,  # TODO: verify
            baseline_env_name=config.baseline_env_name,
            environment_name=config.environment_name,
            branch_name=config.branch_name,
            parent_branch_name=config.parent_branch_name,
            baseline_branch_name=config.baseline_branch_name,
            compare_with_parent_branch=None,  # TODO: verify
            ignore_baseline=None,  # TODO: verify
            save_failed_tests=config.save_failed_tests,
            save_new_tests=config.save_new_tests,
            save_diffs=config.save_diffs,
            dont_close_batches=True,  # TODO: verify
            # EyesCheckConfig
            send_dom=config.send_dom,
            match_timeout=config.match_timeout,
            force_full_page_screenshot=config.force_full_page_screenshot,
            # EyesClassicConfig
            wait_before_screenshots=config.wait_before_screenshots,
            wait_before_capture=config.wait_before_capture,
            stitch_mode=config.stitch_mode,
            hide_scrollbars=config.hide_scrollbars,
            hide_caret=config.hide_caret,
            stitch_overlap=config.stitch_overlap,
            scroll_root_element=None,  # TODO: verify
            cut=cut,
            rotation=config.rotation,
            scale_ratio=config.scale_ratio,
            # EyesUFGConfig
            concurrent_sessions=None,  # TODO: verify
            browsers_info=browsers_info_convert(config.browsers_info),
            visual_grid_options=record_convert(config.visual_grid_options),
            layout_breakpoints=config.layout_breakpoints,
            disable_browser_fetching=config.disable_browser_fetching,
        )


@attr.s
class ContextReference(object):
    frame = attr.ib()  # type: FrameReference
    scroll_root_element = attr.ib(default=None)  # type: Optional[ElementReference]

    @classmethod
    def convert(cls, is_selenium, frame_locators):
        # type: (bool, List[FrameLocator]) -> List[ContextReference]
        return [
            cls(
                frame=frame_reference_convert(
                    is_selenium,
                    frame_locator.frame_locator,
                    frame_locator.frame_index,
                    frame_locator.frame_name_or_id,
                ),
                scroll_root_element=optional_element_reference_convert(
                    is_selenium,
                    frame_locator.scroll_root_locator,
                ),
            )
            for frame_locator in frame_locators
        ]


@attr.s
class ScreenshotSettings(object):
    region = attr.ib(default=None)  # type: Optional[RegionReference]
    frames = attr.ib(default=None)  # type: Optional[List[ContextReference]]
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
    visual_grid_options = attr.ib(default=None)  # type: Optional[Dict[Text, Any]]
    hooks = attr.ib(default=None)  # type: Optional[CheckSettingsHooks]
    render_id = attr.ib(default=None)  # type: Optional[Text]
    variation_group_id = attr.ib(default=None)  # type: Optional[Text]
    timeout = attr.ib(default=None)  # type: Optional[int]
    wait_before_capture = attr.ib(default=None)  # type: Optional[int]

    @classmethod
    def convert(cls, is_selenium, values):
        # type: (bool, SeleniumCheckSettingsValues) -> CheckSettings
        if "beforeCaptureScreenshot" in values.script_hooks:
            hooks = CheckSettingsHooks(values.script_hooks["beforeCaptureScreenshot"])
        else:
            hooks = None
        return cls(
            # CheckSettings
            name=values.name,
            disable_browser_fetching=values.disable_browser_fetching,
            layout_breakpoints=values.layout_breakpoints,
            visual_grid_options=record_convert(values.visual_grid_options),
            hooks=hooks,
            render_id=None,  # TODO: verify
            variation_group_id=values.variation_group_id,
            timeout=values.timeout,
            wait_before_capture=values.wait_before_capture,
            # MatchSettings
            exact=None,  # TODO: verify
            match_level=values.match_level,
            send_dom=values.send_dom,
            use_dom=values.use_dom,
            enable_patterns=values.enable_patterns,
            ignore_caret=values.ignore_caret,
            ignore_displacements=values.ignore_displacements,
            accessibility_settings=None,  # TODO: verify
            ignore_regions=region_references_convert(
                is_selenium, values.ignore_regions
            ),
            layout_regions=region_references_convert(
                is_selenium, values.layout_regions
            ),
            strict_regions=region_references_convert(
                is_selenium, values.strict_regions
            ),
            content_regions=region_references_convert(
                is_selenium, values.content_regions
            ),
            floating_regions=floating_region_references_convert(
                is_selenium, values.floating_regions
            ),
            accessibility_regions=accessibility_region_references_convert(
                is_selenium, values.accessibility_regions
            ),
            # ScreenshotSettings
            region=target_reference_convert(is_selenium, values),
            frames=ContextReference.convert(is_selenium, values.frame_chain),
            scroll_root_element=optional_element_reference_convert(
                is_selenium, values.scroll_root_locator
            ),
            fully=values.stitch_content,
        )


@attr.s
class LocateSettings(object):
    locator_names = attr.ib(factory=list)  # type: List[Text]
    first_only = attr.ib(default=None)  # type: Optional[bool]

    @classmethod
    def convert(cls, visual_locators_settings_values):
        # type: (VisualLocatorSettingsValues) -> LocateSettings
        return cls(
            visual_locators_settings_values.names,
            visual_locators_settings_values.first_only,
        )


@attr.s
class OCRSearchSettings(object):
    patterns = attr.ib(factory=list)  # type: List[Text]
    ignore_case = attr.ib(default=None)  # type: Optional[bool]
    first_only = attr.ib(default=None)  # type: Optional[bool]
    language = attr.ib(default=None)  # type: Optional[Text]

    @classmethod
    def convert(cls, search_settigns):
        # type: (TextRegionSettings) -> OCRSearchSettings
        return cls(
            search_settigns._patterns,
            search_settigns._ignore_case,
            search_settigns._first_only,
            search_settigns._language,
        )


@attr.s
class OCRExtractSettings(object):
    target = attr.ib()  # type: RegionReference
    hint = attr.ib(default=None)  # type: Optional[Text]
    min_match = attr.ib(default=None)  # type: Optional[float]
    language = attr.ib(default=None)  # type: Optional[Text]

    @classmethod
    def convert(cls, is_selenium, ocr_regions):
        # type: (bool, Tuple[OCRRegion]) -> List[OCRExtractSettings]
        return [
            cls(
                ocr_target_convert(is_selenium, region.target),
                region._hint,
                region._min_match,
                region._language,
            )
            for region in ocr_regions
        ]


@attr.s
class CloseBatchesSettings(object):
    batch_ids = attr.ib()  # type: List[Text]
    server_url = attr.ib()  # type: Optional[Text]
    api_key = attr.ib()  # type: Optional[Text]
    proxy = attr.ib()  # type: Optional[Proxy]

    @classmethod
    def convert(cls, enabled_batch_close):
        # type: (_EnabledBatchClose) -> CloseBatchesSettings
        return cls(
            list(enabled_batch_close._ids),
            enabled_batch_close.server_url,
            enabled_batch_close.api_key,
            Proxy.convert(enabled_batch_close.proxy),
        )


@attr.s
class DeleteTestSettings(object):
    test_id = attr.ib()  # type: Text
    batch_id = attr.ib()  # type: Text
    secret_token = attr.ib()  # type: Text
    server_url = attr.ib()  # type: Optional[Text]
    api_key = attr.ib()  # type: Optional[Text]
    proxy = attr.ib()  # type: Optional[Proxy]

    @classmethod
    def convert(cls, test_results):
        # type: (TestResults) -> DeleteTestSettings
        server_url, api_key, proxy = test_results._connection_config  # noqa
        return cls(
            test_results.id,
            test_results.batch_id,
            test_results.secret_token,
            server_url,
            api_key,
            Proxy.convert(proxy),
        )


@attr.s
class ServerInfo(object):
    logs_dir = attr.ib()  # type: Text


def marshal_webdriver_ref(driver):
    # type: (WebDriver) -> dict
    return {
        "sessionId": driver.session_id,
        "serverUrl": driver.command_executor._url,  # noqa
        "capabilities": driver.capabilities,
    }


def marshal_configuration(is_selenium, configuration):
    # type: (bool, Configuration) -> dict
    eyes_config = EyesConfig.convert(is_selenium, configuration)
    return _keys_underscore_to_camel_remove_none(cattr.unstructure(eyes_config))


def marshal_check_settings(is_selenium, check_settings):
    # type: (bool, SeleniumCheckSettings) -> dict
    check_settings = CheckSettings.convert(is_selenium, check_settings.values)
    return _keys_underscore_to_camel_remove_none(cattr.unstructure(check_settings))


def marshal_locate_settings(locate_settings):
    # type: (VisualLocatorSettings) -> dict
    locate_settings = LocateSettings.convert(locate_settings.values)
    return _keys_underscore_to_camel_remove_none(cattr.unstructure(locate_settings))


def marshal_ocr_search_settings(search_settings):
    # type: (TextRegionSettings) -> dict
    search_settings = OCRSearchSettings.convert(search_settings)
    return _keys_underscore_to_camel_remove_none(cattr.unstructure(search_settings))


def marshal_ocr_extract_settings(is_selenium, extract_settings):
    # type: (bool, Tuple[OCRRegion]) -> dict
    extract_settings = OCRExtractSettings.convert(is_selenium, extract_settings)
    return _keys_underscore_to_camel_remove_none(cattr.unstructure(extract_settings))


def marshal_viewport_size(viewport_size):
    # type: (ViewPort) -> dict
    size = Size.convert_viewport(viewport_size)
    return _keys_underscore_to_camel_remove_none(cattr.unstructure(size))


def marshal_enabled_batch_close(close_batches):
    # type: (_EnabledBatchClose) -> dict
    close_batches = CloseBatchesSettings.convert(close_batches)
    return _keys_underscore_to_camel_remove_none(cattr.unstructure(close_batches))


def marshal_delete_test_settings(test_results):
    # type: (TestResults) -> dict
    delete_settings = DeleteTestSettings.convert(test_results)
    return _keys_underscore_to_camel_remove_none(cattr.unstructure(delete_settings))


def demarshal_match_result(results_dict):
    # type: (dict) -> MatchResult
    return attr_from_json(dumps(results_dict), MatchResult)


def demarshal_locate_result(results):
    # type: (dict) -> Dict[Text, List[APIRegion]]
    return {
        locator_id: [APIRegion.from_(region) for region in regions] if regions else []
        for locator_id, regions in results.items()
    }


def demarshal_test_results(results_dict_list, config):
    # type: (List[dict], Optional[Configuration]) -> List[TestResults]
    results = [attr_from_json(dumps(r), TestResults) for r in results_dict_list]
    if config:
        for result in results:
            if result:  # in case of internal USDK failure, None result is observed
                result.set_connection_config(
                    config.server_url, config.api_key, config.proxy
                )
    return results


def demarshal_server_info(info_dict):
    # type: (dict) -> ServerInfo
    return ServerInfo(info_dict["logsDir"])


def _keys_underscore_to_camel_remove_none(obj):
    if isinstance(obj, dict):
        return {
            underscore_to_camelcase(k): _keys_underscore_to_camel_remove_none(v)
            for k, v in obj.items()
            if v is not None
        }
    elif isinstance(obj, list):
        return [_keys_underscore_to_camel_remove_none(i) for i in obj]
    else:
        return obj
