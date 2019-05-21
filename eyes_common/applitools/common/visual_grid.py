import base64
import typing
from enum import Enum

import attr

from .config.misc import BrowserType
from .geometry import RectangleSize
from .utils import general_utils, json_utils
from .utils.compat import ABC, basestring
from .utils.json_utils import JsonInclude

if typing.TYPE_CHECKING:
    from typing import List, Text, Dict, Optional
    from requests import Response
    from applitools.common.utils.custom_types import Num
    from applitools.selenium.visual_grid.vg_task import VGTask
    from .geometry import Region

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


@attr.s(frozen=True)
class RenderingInfo(object):
    service_url = attr.ib()
    access_token = attr.ib(repr=False)
    results_url = attr.ib()


class ScreenOrientation(Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


@attr.s(hash=True)
class EmulationBaseInfo(ABC):
    screen_orientation = attr.ib()  # type: ScreenOrientation


@attr.s
class VisualGridSelector(object):
    selector = attr.ib()  # type: basestring
    category = attr.ib()  # type: basestring


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
    # DeviceName = DeviceName
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
    )  # type: Optional[RectangleSize]
    browser_type = attr.ib(default=BrowserType.CHROME)  # type: BrowserType
    baseline_env_name = attr.ib(default=None)  # type: Optional[basestring]
    emulation_info = attr.ib(
        default=None, repr=False
    )  # type: Optional[EmulationBaseInfo]
    # TODO: add initialization with width and height for viewport_size

    @property
    def width(self):
        if self.viewport_size:
            return self.viewport_size["width"]
        return 0

    @property
    def height(self):
        if self.viewport_size:
            return self.viewport_size["height"]
        return 0

    @property
    def size_mode(self):
        # TODO: Add more size modes
        return "full-page"

    @property
    def platform(self):
        if self.browser_type in [
            BrowserType.IE_10,
            BrowserType.IE_11,
            BrowserType.EDGE,
        ]:
            return "windows"
        return "linux"


@attr.s
class RenderInfo(object):
    width = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Optional[Num]
    height = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Optional[Num]
    size_mode = attr.ib(
        metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[basestring]
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
    CONTENT_TYPE = "x-applitools-html/cdt"

    dom_nodes = attr.ib(repr=False)  # type: List[dict]
    resources = attr.ib()  # type: Dict[Text, VGResource]
    url = attr.ib()  # type: basestring
    msg = attr.ib(default=None)  # type: basestring
    hash = attr.ib(init=False, metadata={JsonInclude.THIS: True})  # type: basestring
    hash_format = attr.ib(
        default="sha256", metadata={JsonInclude.THIS: True}
    )  # type: basestring

    def __attrs_post_init__(self):
        # TODO: add proper hash
        self.hash = general_utils.get_sha256_hash(self.content.encode("utf-8"))

    @property
    def resource(self):
        return VGResource(
            self.url,
            self.CONTENT_TYPE,
            self.content.encode("utf-8"),
            "RGridDom {}".format(self.msg),
        )

    @property
    def content(self):
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

    def __hash__(self):
        return self.hash

    def __attrs_post_init__(self):
        self.hash = general_utils.get_sha256_hash(self.content)

    @classmethod
    def from_blob(cls, blob):
        content = base64.b64decode(blob.get("value", ""))
        return cls(blob.get("url"), blob.get("type"), content)

    @classmethod
    def from_response(cls, url, response):
        # type: (Text, Response) -> VGResource
        if not response.ok:
            return cls(url, "application/empty-response", b"")
        return cls(url, response.headers["Content-Type"], response.content)


@attr.s
class RenderRequest(object):
    webhook = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Text
    agent_id = attr.ib(metadata={JsonInclude.THIS: True})
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
    )  # type: List
    send_dom = attr.ib(
        default=False, metadata={JsonInclude.NON_NONE: True}
    )  # type: bool
    render_id = attr.ib(default=None, repr=True, metadata={JsonInclude.THIS: True})
    task = attr.ib(default=None)  # type: Optional[VGTask]
    browser = attr.ib(init=False, default=None, metadata={JsonInclude.NON_NONE: True})

    def __attrs_post_init__(self):
        if self.browser_name is None:
            return
        self.browser = {"name": self.browser_name.value, "platform": self.platform}


@attr.s(hash=True)
class RunningRender(object):
    render_id = attr.ib(default=None)
    job_id = attr.ib(default=None)
    render_status = attr.ib(
        default=None, converter=attr.converters.optional(RenderStatus)
    )  # type: RenderStatus
    need_more_resources = attr.ib(default=None, hash=False)  # type: List[Text]
    need_more_dom = attr.ib(default=None, hash=False)  # type: bool


@attr.s
class RenderStatusResults(object):
    status = attr.ib(
        default=None,
        type=RenderStatus,
        converter=attr.converters.optional(RenderStatus),
    )
    dom_location = attr.ib(default=None)
    user_agent = attr.ib(default=None)
    image_location = attr.ib(default=None)
    os = attr.ib(default=None)
    error = attr.ib(
        default=None,
        type=RenderStatus,
        converter=attr.converters.optional(RenderStatus),
    )
    selector_regions = attr.ib(default=None)
    device_size = attr.ib(
        default=None,
        type=RectangleSize,
        converter=attr.converters.optional(RectangleSize.from_),
    )
    retry_count = attr.ib(default=None)
    render_id = attr.ib(default=None)
