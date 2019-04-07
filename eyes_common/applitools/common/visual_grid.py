import base64
import json
import typing
from enum import Enum

import attr
from requests import Response

from applitools.common.config.misc import BrowserType
from applitools.common.utils import general_utils
from applitools.common.utils.compat import ABC, basestring, iteritems

if typing.TYPE_CHECKING:
    from typing import List, Text, Dict, Optional
    from applitools.common.geometry import RectangleSize
    from applitools.selenium.visual_grid.vg_task import VGTask

__all__ = (
    "RenderStatus",
    "RenderingInfo",
    "ScreenOrientation",
    "VisualGridSelector",
    "DeviceName",
    "EmulationInfo",
    "EmulationDevice",
    "RenderBrowserInfo",
    "RenderInfo",
    "RGridDom",
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
class EmulationInfo(EmulationBaseInfo):
    DeviceName = DeviceName
    device_name = attr.ib()
    screen_orientation = attr.ib()  # type: ScreenOrientation


@attr.s(hash=True)
class EmulationDevice(EmulationBaseInfo):
    width = attr.ib()  # type: int
    height = attr.ib()  # type: int
    device_scale_factor = attr.ib()  # type: float
    is_mobile = attr.ib()  # type: bool
    screen_orientation = attr.ib()  # type: ScreenOrientation
    device_name = attr.ib(init=False, default=None)  # type: DeviceName


@attr.s(hash=True)
class RenderBrowserInfo(object):
    viewport_size = attr.ib(default=None)  # type: RectangleSize
    browser_type = attr.ib(default=None)  # type: BrowserType
    baseline_env_name = attr.ib(default=None)  # type: basestring
    emulation_info = attr.ib(default=None, repr=False)  # type: EmulationBaseInfo
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
        if self.browser_type:
            if (
                self.browser_type == BrowserType.CHROME
                or self.browser_type == BrowserType.FIREFOX
            ):
                return "linux"
            elif (
                self.browser_type == BrowserType.IE
                or self.browser_type == BrowserType.EDGE
            ):
                return "windows"
        return "linux"


@attr.s
class RenderInfo(object):
    width = attr.ib()  # type: int
    height = attr.ib()  # type: int
    size_mode = attr.ib()  # type: basestring
    # region = attr.ib(type=Region)  # type: Region
    # selector = attr.ib(type=VisualGridSelector)  # type: VisualGridSelector
    _emulation_info = attr.ib(type=EmulationBaseInfo)  # type: EmulationBaseInfo


@attr.s
class RGridDom(object):
    CONTENT_TYPE = "x-applitools-html/cdt"

    _dom_nodes = attr.ib(repr=False)  # type: List[dict]
    _resources = attr.ib()  # type: Dict[Text, VGResource]
    _url = attr.ib()
    _msg = attr.ib(default=None)
    hash = attr.ib(init=False)
    hash_format = attr.ib(default="sha256")

    def __attrs_post_init__(self):
        # TODO: add proper hash
        self.hash = general_utils.get_sha256_hash(self.content)

    @property
    def resource(self):
        return VGResource(
            self._url, self.CONTENT_TYPE, self.content, "RGridDom {}".format(self._msg)
        )

    @property
    def content(self):
        resources = {}
        for url, res in iteritems(self._resources):
            resources[url] = attr.asdict(
                res, filter=lambda a, _: not a.name.startswith("_")
            )
        data = {"resources": resources, "domNodes": self._dom_nodes}
        return json.dumps(data).encode("utf-8")


@attr.s(slots=True, hash=True)
class VGResource(object):
    _url = attr.ib()
    content_type = attr.ib()
    _content = attr.ib(repr=False)  # type: bytes
    _msg = attr.ib(default=None)
    hash = attr.ib(init=False, hash=False)
    hash_format = attr.ib(init=False, hash=False, default="sha256")

    @property
    def url(self):
        return self._url

    @property
    def content(self):
        return self._content

    def __attrs_post_init__(self):
        self.hash = general_utils.get_sha256_hash(self._content)

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
    webhook = attr.ib()  # type: Text
    url = attr.ib()  # type: dict
    dom = attr.ib(repr=False)  # type: RGridDom
    resources = attr.ib(repr=False)  # type: dict
    render_info = attr.ib()  # type: RenderInfo
    _platform = attr.ib()  # type: Text
    _browser_name = attr.ib()  # type: BrowserType
    script_hooks = attr.ib()  # type: Dict
    selectors_to_find_regions_for = attr.ib()  # type: List
    send_dom = attr.ib()  # type: bool
    _task = attr.ib()  # type: Optional[VGTask]
    render_id = attr.ib(default=None, repr=True)
    browser = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.browser = {"name": self._browser_name, "platform": self._platform}


@attr.s(hash=True)
class RunningRender(object):
    render_id = attr.ib(default=None)
    job_id = attr.ib(default=None)
    render_status = attr.ib(default=None, converter=RenderStatus)  # type: RenderStatus
    need_more_resources = attr.ib(default=None, hash=False)  # type: List[Text]
    need_more_dom = attr.ib(default=None, hash=False)  # type: bool


@attr.s
class RenderStatusResults(object):
    status = attr.ib(default=None)
    dom_location = attr.ib(default=None)
    user_agent = attr.ib(default=None)
    image_location = attr.ib(default=None)
    os = attr.ib(default=None)
    error = attr.ib(default=None, converter=attr.converters.optional(RenderStatus))
    selector_regions = attr.ib(default=None)
    device_size = attr.ib(default=None)
