from abc import abstractmethod

import attr

from applitools.common.config.misc import BrowserType
from applitools.common.geometry import RectangleSize, Region
from applitools.common.utils import general_utils
from applitools.common.utils.compat import ABC, basestring


@attr.s
class RenderingInfo(object):
    service_url = attr.ib()
    access_token = attr.ib()
    results_url = attr.ib()


@attr.s
class EmulationBaseInfo(ABC):
    screen_orientation = attr.ib()

    @abstractmethod
    def device_name(self):
        pass


@attr.s
class VisualGridSelector(object):
    selector = attr.ib()  # type: basestring
    category = attr.ib()  # type: dict


@attr.s
class EmulationDevice(EmulationBaseInfo):
    device_name = attr.ib()


@attr.s
class RenderBrowserInfo(object):
    viewport_size = attr.ib(default=None)  # type: RectangleSize
    browser_type = attr.ib(default=None)  # type: BrowserType
    baseline_env_name = attr.ib(default=None)  # type: basestring
    emulation_info = attr.ib(default=None)  # type: EmulationBaseInfo
    # TODO: add initialization with width and height for viewport_size

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
    # FIXME: Possible issue with region. In JAVA return region as x,y,width,height
    width = attr.ib()  # type: int
    height = attr.ib()  # type: int
    size_mode = attr.ib()  # type: basestring
    region = attr.ib(type=Region)  # type: Region
    emulation_info = attr.ib(type=EmulationBaseInfo)  # type: EmulationBaseInfo
    selector = attr.ib(type=VisualGridSelector)  # type: VisualGridSelector


@attr.s
class RGridResource(object):
    url = attr.ib()
    content_type = attr.ib()
    content = attr.ib()
    _sha256 = attr.ib(init=False)

    @property
    def sha256(self):
        if not self._sha256:
            self._sha256 = general_utils.get_sha256_hash(self.content)
        return self._sha256


@attr.s
class RenderRequest(object):
    render_id = attr.ib()
    task = attr.ib()
    webhook = attr.ib()
    url = attr.ib()
    dom = attr.ib()
    resources = attr.ib()
    render_info = attr.ib()
    platform = attr.ib()
    browser_name = attr.ib()
    script_hooks = attr.ib()
    selectors_to_find_regions_for = attr.ib()
    send_dom = attr.ib()


@attr.s
class RunningRender(object):
    render_id = attr.ib()
    job_id = attr.ib()
    render_status = attr.ib()
    need_more_resources = attr.ib()
    need_more_dom = attr.ib()
