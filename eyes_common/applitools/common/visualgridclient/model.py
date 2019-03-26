import typing
from enum import Enum

import attr

from applitools.common.config.misc import BrowserType
from applitools.common.geometry import RectangleSize, Region
from applitools.common.utils import general_utils
from applitools.common.utils.compat import ABC, basestring

if typing.TYPE_CHECKING:
    from typing import List
    from applitools.common import TestResults


@attr.s
class RenderingInfo(object):
    service_url = attr.ib()
    access_token = attr.ib()
    results_url = attr.ib()


class ScreenOrientation(Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


@attr.s
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


@attr.s
class EmulationInfo(EmulationBaseInfo):
    DeviceName = DeviceName
    device_name = attr.ib()  # type: DeviceName
    screen_orientation = attr.ib()  # type: ScreenOrientation


@attr.s
class EmulationDevice(EmulationBaseInfo):
    width = attr.ib()  # type: int
    height = attr.ib()  # type: int
    device_scale_factor = attr.ib()  # type: float
    is_mobile = attr.ib()  # type: bool
    screen_orientation = attr.ib()  # type: ScreenOrientation
    device_name = attr.ib(init=False, default=None)  # type: DeviceName


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


@attr.s
class TestResultSummary(object):
    _all_results = attr.ib(factory=list)  # type:List[TestResultContainer]
    _passed = attr.ib(default=0, init=False)  # type: int
    _unresolved = attr.ib(default=0, init=False)  # type: int
    _failed = attr.ib(default=0, init=False)  # type: int
    _exceptions = attr.ib(default=0, init=False)  # type: int
    _mismatches = attr.ib(default=0, init=False)  # type: int
    _missing = attr.ib(default=0, init=False)  # type: int
    _matches = attr.ib(default=0, init=False)  # type: int

    # TODO: getAllResults is missing
    def __attrs_post_init__(self):
        for result_cont in self._all_results:
            if result_cont.exception:
                self._exceptions += 1

            result = result_cont.test_results
            if result is None:
                continue
            if result.status:
                if result.is_failed:
                    self._failed += 1
                elif result.is_passed:
                    self._passed += 1
                elif result.is_unresolved:
                    self._unresolved += 1

            self._matches += result.matches
            self._missing += result.missing
            self._mismatches += result.matches


@attr.s
class TestResultContainer(object):
    test_results = attr.ib()  # type: TestResults
    exception = attr.ib()
