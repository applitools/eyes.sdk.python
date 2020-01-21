import base64
import typing
from enum import Enum

import attr

from .geometry import RectangleSize, Region
from .selenium.misc import BrowserType
from .utils import general_utils, json_utils
from .utils.compat import ABC
from .utils.json_utils import JsonInclude

if typing.TYPE_CHECKING:
    from typing import List, Text, Dict, Optional, Callable
    from requests import Response
    from applitools.common.utils.custom_types import Num
    from applitools.selenium.visual_grid.vg_task import VGTask

__all__ = (
    "RenderStatus",
    "RenderingInfo",
    "ScreenOrientation",
    "VisualGridSelector",
    "DeviceName",
    "ChromeEmulationInfo",
    "EmulationDevice",
    "RenderBrowserInfo",
    "RenderInfo",
    "RGridDom",
    "RunningRender",
    "VGResource",
    "RenderRequest",
    "RenderStatusResults",
)


class RenderStatus(Enum):
    NEED_MORE_RESOURCE = "need-more-resources"
    RENDERING = "rendering"
    RENDERED = "rendered"
    ERROR = "error"
    NEED_MORE_DOM = "need-more-dom"
    INTERNAL_FAILURE = "internal failure"


@attr.s
class VGRegion(object):
    x = attr.ib(default=None, metadata={JsonInclude.THIS: True})
    y = attr.ib(default=None, metadata={JsonInclude.THIS: True})
    width = attr.ib(default=None, metadata={JsonInclude.THIS: True})
    height = attr.ib(default=None, metadata={JsonInclude.THIS: True})
    error = attr.ib(default=None, metadata={JsonInclude.THIS: True})

    def to_region(self):
        return Region(self.x, self.y, self.width, self.height)

    def offset(self, dx, dy):
        return self.to_region().offset(dx, dy)


@attr.s(frozen=True)
class RenderingInfo(object):
    service_url = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    access_token = attr.ib(repr=False, metadata={JsonInclude.THIS: True})  # type: Text
    results_url = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text


class ScreenOrientation(Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


@attr.s(hash=True, slots=True)
class EmulationBaseInfo(ABC):
    screen_orientation = attr.ib()  # type: ScreenOrientation


@attr.s(hash=True, slots=True)
class VisualGridSelector(object):
    selector = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Text
    category = attr.ib()  # type: Text
    type = attr.ib(default="xpath", metadata={JsonInclude.THIS: True})


class DeviceName(Enum):
    iPhone_4 = "iPhone 4"
    iPhone_5SE = "iPhone 5/SE"
    iPhone_6_7_8 = "iPhone 6/7/8"
    iPhone6_7_8_Plus = "iPhone 6/7/8 Plus"
    iPhone_X = "iPhone X"
    iPad = "iPad"
    iPad_Pro = "iPad Pro"
    BlackBerry_Z30 = "BlackBerry Z30"
    Nexus_4 = "Nexus 4"
    Nexus_5 = "Nexus 5"
    Nexus_5X = "Nexus 5X"
    Nexus_6 = "Nexus 6"
    Nexus_6P = "Nexus 6P"
    Pixel_2 = "Pixel 2"
    Pixel_2_XL = "Pixel 2 XL"
    LG_Optimus_L70 = "LG Optimus L70"
    Nokia_N9 = "Nokia N9"
    Nokia_Lumia_520 = "Nokia Lumia 520"
    Microsoft_Lumia_550 = "Microsoft Lumia 550"
    Microsoft_Lumia_950 = "Microsoft Lumia 950"
    Galaxy_S3 = "Galaxy S III"
    Galaxy_S5 = "Galaxy S5"
    Kindle_Fire_HDX = "Kindle Fire HDX"
    iPad_Mini = "iPad Mini"
    Blackberry_PlayBook = "Blackberry PlayBook"
    Nexus_10 = "Nexus 10"
    Nexus_7 = "Nexus 7"
    Galaxy_Note_3 = "Galaxy Note 3"
    Galaxy_Note_2 = "Galaxy Note II"
    Laptop_with_touch = "Laptop with touch"
    Laptop_with_HiDPI_screen = "Laptop with HiDPI screen"
    Laptop_with_MDPI_screen = "Laptop with MDPI screen"


@attr.s(hash=True)
class ChromeEmulationInfo(EmulationBaseInfo):
    device_name = attr.ib(
        converter=DeviceName, metadata={JsonInclude.NON_NONE: True}
    )  # type: DeviceName
    screen_orientation = attr.ib(
        converter=ScreenOrientation, metadata={JsonInclude.NON_NONE: True}
    )  # type: ScreenOrientation


@attr.s(hash=True)
class EmulationDevice(EmulationBaseInfo):
    width = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: int
    height = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: int
    device_scale_factor = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: float
    is_mobile = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: bool
    screen_orientation = attr.ib(
        metadata={JsonInclude.THIS: True}
    )  # type: ScreenOrientation
    device_name = attr.ib(init=False, default=None)  # type: DeviceName


@attr.s(hash=True)
class RenderBrowserInfo(object):
    viewport_size = attr.ib(
        default=None, converter=attr.converters.optional(RectangleSize.from_)
    )  # type: Optional[RectangleSize]  # type: ignore
    browser_type = attr.ib(default=BrowserType.CHROME)  # type: BrowserType
    baseline_env_name = attr.ib(default=None)  # type: Optional[Text]
    emulation_info = attr.ib(
        default=None, repr=False
    )  # type: Optional[EmulationBaseInfo]
    # TODO: add initialization with width and height for viewport_size

    @property
    def width(self):
        # type: () -> int
        if self.viewport_size:
            return self.viewport_size["width"]
        return 0

    @property
    def height(self):
        # type: () -> int
        if self.viewport_size:
            return self.viewport_size["height"]
        return 0

    @property
    def platform(self):
        # type: () -> Text
        if self.browser_type in [
            BrowserType.IE_10,
            BrowserType.IE_11,
            BrowserType.EDGE,
        ]:
            return "windows"
        elif self.browser_type in [
            BrowserType.SAFARI,
            BrowserType.SAFARI_ONE_VERSION_BACK,
            BrowserType.SAFARI_TWO_VERSIONS_BACK,
        ]:
            return "mac os x"
        return "linux"


@attr.s
class RenderInfo(object):
    width = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Optional[Num]
    height = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Optional[Num]
    size_mode = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Optional[Text]
    region = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[Region]
    selector = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[VisualGridSelector]
    emulation_info = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[EmulationBaseInfo]


@attr.s
class RGridDom(object):
    CONTENT_TYPE = "x-applitools-html/cdt"  # type: Text

    dom_nodes = attr.ib(repr=False)  # type: List[dict]
    resources = attr.ib()  # type: Dict[Text, VGResource]
    url = attr.ib()  # type: Text
    msg = attr.ib(default=None)  # type: Text
    hash = attr.ib(init=False, metadata={JsonInclude.THIS: True})  # type: Text
    hash_format = attr.ib(
        default="sha256", metadata={JsonInclude.THIS: True}
    )  # type: Text

    def __attrs_post_init__(self):
        # TODO: add proper hash
        self.hash = general_utils.get_sha256_hash(self.content.encode("utf-8"))

    @property
    def resource(self):
        # type: () -> VGResource
        return VGResource(
            self.url,
            self.CONTENT_TYPE,
            self.content.encode("utf-8"),
            "RGridDom {}".format(self.msg),
        )

    @property
    def content(self):
        # type: () -> Text
        data = {"resources": self.resources, "domNodes": self.dom_nodes}
        return json_utils.to_json(data)


@attr.s(slots=True)
class VGResource(object):
    url = attr.ib()  # type: Text
    content_type = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    content = attr.ib(repr=False)  # type: bytes
    msg = attr.ib(default=None)  # type: Optional[Text]
    hash = attr.ib(init=False, metadata={JsonInclude.THIS: True})  # type: Text
    hash_format = attr.ib(
        init=False, default="sha256", metadata={JsonInclude.THIS: True}
    )  # type: Text
    _handle_func = attr.ib(default=None)

    def __hash__(self):
        return self.hash

    def __attrs_post_init__(self):
        self.hash = general_utils.get_sha256_hash(self.content)
        if callable(self._handle_func):
            self._handle_func()

    @classmethod
    def EMPTY(cls, url):
        return cls(url, "application/empty-response", b"")

    @classmethod
    def from_blob(cls, blob, on_created=None):
        # type: (Dict, Callable) -> VGResource
        content = base64.b64decode(blob.get("value", ""))
        content_type = blob.get("type")
        return cls(
            blob.get("url"),
            content_type,
            content,
            handle_func=lambda: on_created(content_type, content),
        )

    @classmethod
    def from_response(cls, url, response, on_created=None):
        # type: (Text, Response, Callable) -> VGResource
        if not response.ok:
            return VGResource.EMPTY(url)

        content_type = response.headers["Content-Type"]
        content = response.content
        return cls(
            url,
            content_type,
            content,
            handle_func=lambda: on_created(content_type, content),
        )


@attr.s
class RenderRequest(object):
    webhook = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Text
    agent_id = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    url = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Text
    dom = attr.ib(repr=False, metadata={JsonInclude.NON_NONE: True})  # type: RGridDom
    resources = attr.ib(repr=False, metadata={JsonInclude.NON_NONE: True})  # type: dict
    render_info = attr.ib(metadata={JsonInclude.THIS: True})  # type: RenderInfo
    platform = attr.ib()  # type: Text
    browser_name = attr.ib()  # type: BrowserType
    script_hooks = attr.ib(
        default=dict, metadata={JsonInclude.NON_NONE: True}
    )  # type: Dict
    selectors_to_find_regions_for = attr.ib(
        factory=list, metadata={JsonInclude.THIS: True}
    )  # type: List[VisualGridSelector]
    send_dom = attr.ib(
        default=False, metadata={JsonInclude.NON_NONE: True}
    )  # type: bool
    render_id = attr.ib(
        default=None, repr=True, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Text]
    task = attr.ib(default=None)  # type: Optional[VGTask]
    browser = attr.ib(
        init=False, default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[Dict]

    def __attrs_post_init__(self):
        if self.browser_name is None:
            return
        self.browser = {"name": self.browser_name.value, "platform": self.platform}


@attr.s(hash=True)
class RunningRender(object):
    render_id = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Text]
    job_id = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Text]
    render_status = attr.ib(
        default=None,
        converter=attr.converters.optional(RenderStatus),
        metadata={JsonInclude.THIS: True},
    )  # type: RenderStatus
    need_more_resources = attr.ib(
        default=None, hash=False, metadata={JsonInclude.THIS: True}
    )  # type: List[Text]
    need_more_dom = attr.ib(
        default=None, hash=False, metadata={JsonInclude.THIS: True}
    )  # type: bool


@attr.s
class RenderStatusResults(object):
    status = attr.ib(
        default=None,
        type=RenderStatus,
        converter=attr.converters.optional(RenderStatus),
        metadata={JsonInclude.THIS: True},
    )  # type: Optional[RenderStatus]
    dom_location = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Text]
    user_agent = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Text]
    image_location = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Text]
    os = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Text]
    error = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Text]
    selector_regions = attr.ib(
        factory=list, type=VGRegion, metadata={JsonInclude.THIS: True}
    )  # type: List[VGRegion]
    device_size = attr.ib(
        default=None,
        type=RectangleSize,
        converter=attr.converters.optional(RectangleSize.from_),
        metadata={JsonInclude.THIS: True},
    )  # type: Optional[RectangleSize]
    retry_count = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[int]
    render_id = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Text]
