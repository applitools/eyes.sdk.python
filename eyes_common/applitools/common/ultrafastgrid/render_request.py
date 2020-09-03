import base64
import typing
from enum import Enum

import attr

from applitools.common import logger
from applitools.common.geometry import RectangleSize, Region
from applitools.common.selenium.misc import BrowserType
from applitools.common.utils import general_utils, json_utils
from applitools.common.utils.json_utils import JsonInclude
from .render_browser_info import (
    IosDeviceInfo,
    IRenderBrowserInfo,
    ChromeEmulationInfo,
    EmulationBaseInfo,
)

if typing.TYPE_CHECKING:
    from typing import List, Text, Dict, Optional, Callable, Union, Any
    from requests import Response
    from applitools.common.utils.custom_types import Num
    from applitools.selenium.visual_grid.vg_task import VGTask

__all__ = (
    "RenderStatus",
    "RenderingInfo",
    "VisualGridSelector",
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
    service_url = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Text]
    access_token = attr.ib(
        default=None, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Text]
    results_url = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Text]
    stitching_service_url = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Text]
    max_image_height = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[int]
    max_image_area = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[int]


@attr.s(hash=True, slots=True)
class VisualGridSelector(object):
    selector = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Text
    category = attr.ib()  # type: Union[Text, Any]
    type = attr.ib(default="xpath", metadata={JsonInclude.THIS: True})


@attr.s
class RenderInfo(object):
    width = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Optional[Num]
    height = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Optional[Num]
    size_mode = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Optional[Text]
    region = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[Region]
    selector = attr.ib(
        default=None, type=VisualGridSelector, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[VisualGridSelector]
    emulation_info = attr.ib(
        default=None, type=EmulationBaseInfo, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[EmulationBaseInfo]
    ios_device_info = attr.ib(
        default=None, type=IosDeviceInfo, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[IosDeviceInfo]

    @classmethod
    def from_(
        cls,
        size_mode,  # type: Optional[Text]
        region,  # type: Optional[Region]
        selector,  # type: Optional[VisualGridSelector]
        render_browser_info,  # type: IRenderBrowserInfo
    ):
        # type: (...) -> RenderInfo
        ios_device_info = None
        emulation_info = None
        if isinstance(render_browser_info, IosDeviceInfo):
            ios_device_info = render_browser_info
        if isinstance(render_browser_info, ChromeEmulationInfo):
            emulation_info = render_browser_info
        return cls(
            width=render_browser_info.width,
            height=render_browser_info.height,
            size_mode=size_mode,
            region=region,
            selector=selector,
            emulation_info=emulation_info,
            ios_device_info=ios_device_info,
        )


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
            try:
                self._handle_func()
            except Exception:
                logger.exception(
                    "Exception has been appeared during processing"
                    " of VGResource({})".format(self.url),
                )

    @classmethod
    def EMPTY(cls, url):
        return cls(url, "application/empty-response", b"")

    @classmethod
    def from_blob(cls, blob, on_created=None):
        # type: (Dict, Callable) -> VGResource
        content = base64.b64decode(blob.get("value", ""))
        content_type = blob.get("type")
        url = blob.get("url")
        return cls(
            url,
            content_type,
            content,
            handle_func=lambda: on_created(content_type, content, url),
        )

    @classmethod
    def from_response(cls, url, response, on_created=None):
        # type: (Text, Response, Callable) -> VGResource
        if not response.ok:
            logger.debug(
                "We've got response code {} {} for URL {}".format(
                    response.status_code, response.reason, url
                )
            )
            return VGResource.EMPTY(url)

        content_type = response.headers.get("Content-Type")
        content = response.content
        return cls(
            url,
            content_type,
            content,
            handle_func=lambda: on_created(content_type, content, url),
        )


@attr.s
class RenderRequest(object):
    webhook = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Text
    agent_id = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    url = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Text
    stitching_service = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Text
    dom = attr.ib(repr=False, metadata={JsonInclude.NON_NONE: True})  # type: RGridDom
    resources = attr.ib(repr=False, metadata={JsonInclude.NON_NONE: True})  # type: dict
    render_info = attr.ib(metadata={JsonInclude.THIS: True})  # type: RenderInfo
    platform_name = attr.ib()  # type: Text
    browser_name = attr.ib()  # type: Text
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
    browser = attr.ib(init=False, default=None, metadata={JsonInclude.NON_NONE: True})
    platform = attr.ib(
        init=False, default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[Dict]
    options = attr.ib(
        factory=dict, metadata={JsonInclude.THIS: True}
    )  # type: Dict[str, Any]

    def __attrs_post_init__(self):
        if self.browser_name is None:
            return
        self.browser = {"name": self.browser_name}
        self.platform = {"name": self.platform_name}


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
    visual_viewport = attr.ib(
        default=None, type=RectangleSize, metadata={JsonInclude.THIS: True}
    )  # type: Optional[RectangleSize]
