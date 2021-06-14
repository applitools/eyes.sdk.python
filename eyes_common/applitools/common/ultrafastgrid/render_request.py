import base64
import typing
from enum import Enum

import attr

from applitools.common import logger
from applitools.common.errors import EyesError
from applitools.common.geometry import RectangleSize, Region
from applitools.common.utils import general_utils, json_utils
from applitools.common.utils.json_utils import JsonInclude

from .render_browser_info import (
    ChromeEmulationInfo,
    EmulationBaseInfo,
    IosDeviceInfo,
    IRenderBrowserInfo,
)

if typing.TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Optional, Text, Union

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
    "JobInfo",
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
    category = attr.ib()  # type: Union[Text, 'GetRegion']  # noqa
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
    MAX_CDT_SIZE = 30 * 1024 * 1024

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
        content = self.content.encode("utf-8")
        if len(content) > self.MAX_CDT_SIZE:
            raise EyesError("Page snapshot is too big for rendering")
        return VGResource(
            self.url,
            self.CONTENT_TYPE,
            content,
            "RGridDom {}".format(self.msg),
        )

    @property
    def content(self):
        # type: () -> Text
        data = {"resources": self.resources, "domNodes": self.dom_nodes}
        return json_utils.to_json(data)


@attr.s(slots=True)
class VGResource(object):
    MAX_RESOURCE_SIZE = 30 * 1024 * 1024  # type: int

    url = attr.ib()  # type: Text
    content_type = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    content = attr.ib(repr=False)  # type: Optional[bytes]
    msg = attr.ib(default=None)  # type: Optional[Text]
    error_status_code = attr.ib(
        default=None, hash=False, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[Text]
    hash = attr.ib(init=False, metadata={JsonInclude.NON_NONE: True})  # type: Text
    hash_format = attr.ib(
        init=False, default="sha256", metadata={JsonInclude.THIS: True}
    )  # type: Text
    child_resource_urls = attr.ib(factory=list)  # type: List[Text]
    _get_child_resource_urls_func = attr.ib(default=None)  # type: Callable

    def __hash__(self):
        return self.hash

    def __attrs_post_init__(self):
        if len(self.content) > self.MAX_RESOURCE_SIZE:
            logger.debug(
                "The content of {} is bigger then supported max size. "
                "Trimming to {} bytes".format(self.url, self.MAX_RESOURCE_SIZE)
            )
            self.content = self.content[: self.MAX_RESOURCE_SIZE]
        self.hash = general_utils.get_sha256_hash(self.content)
        if not self.error_status_code and callable(self._get_child_resource_urls_func):
            try:
                self.child_resource_urls = self._get_child_resource_urls_func(
                    self.content_type, self.content, self.url
                )
            except Exception:
                logger.exception(
                    "Exception has been appeared during processing"
                    " of VGResource({})".format(self.url),
                )

    @classmethod
    def from_blob(cls, blob, get_child_resource_urls_func):
        # type: (Dict, Callable) -> VGResource
        content = base64.b64decode(blob.get("value", ""))
        content_type = blob.get("type")
        url = blob.get("url")
        error_status = blob.get("errorStatusCode")

        return cls(
            url,
            content_type,
            content,
            error_status_code=str(error_status) if error_status is not None else None,
            get_child_resource_urls_func=get_child_resource_urls_func,
        )

    @classmethod
    def from_response(cls, url, response, get_child_resource_urls_func):
        # type: (Text, Response, Callable) -> VGResource
        content = response.content or b""
        content_type = response.headers.get("Content-Type")
        error_status = None if response.ok else str(response.status_code)

        return cls(
            url,
            content_type,
            content,
            error_status_code=error_status,
            get_child_resource_urls_func=get_child_resource_urls_func,
        )

    def clear(self):
        logger.debug("Clearing resource: {} {}".format(self.hash, self.url))
        self.content = None


@attr.s(hash=True)
class RenderRequest(object):
    webhook = attr.ib(default=None, metadata={JsonInclude.NON_NONE: True})  # type: Text
    agent_id = attr.ib(default=None, metadata={JsonInclude.THIS: True})  # type: Text
    url = attr.ib(default=None, metadata={JsonInclude.NON_NONE: True})  # type: Text
    stitching_service = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Text
    dom = attr.ib(
        repr=False, default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: RGridDom
    resources = attr.ib(
        repr=False, default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: dict
    render_info = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: RenderInfo
    platform_name = attr.ib(
        default=None,
    )  # type: Text
    browser_name = attr.ib(
        default=None,
    )  # type: Text
    script_hooks = attr.ib(
        factory=dict, metadata={JsonInclude.NON_NONE: True}
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
    renderer = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[Text]

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
        default=None,
        type=RectangleSize,
        converter=attr.converters.optional(RectangleSize.from_),
        metadata={JsonInclude.THIS: True},
    )  # type: Optional[RectangleSize]


@attr.s
class JobInfo(object):
    renderer = attr.ib(default="", metadata={JsonInclude.THIS: True})
    eyes_environment = attr.ib(default="", type=dict, metadata={JsonInclude.THIS: True})
