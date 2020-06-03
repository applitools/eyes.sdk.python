from enum import Enum
from typing import Optional, Text, Union

import attr

from applitools.common.geometry import RectangleSize
from applitools.common.selenium.misc import BrowserType
from applitools.common.utils import ABC
from applitools.common.utils.compat import basestring
from applitools.common.utils.json_utils import JsonInclude


class ScreenOrientation(Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


@attr.s(hash=True, slots=True)
class EmulationBaseInfo(ABC):
    screen_orientation = attr.ib()  # type: ScreenOrientation


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


class IosDeviceName(Enum):
    iPhone_11_Pro = "iPhone 11 Pro"
    iPhone_11_Pro_Max = "iPhone 11 Pro Max"
    iPhone_11 = "iPhone 11"
    iPhone_XR = "iPhone XR"
    iPhone_XS = "iPhone Xs"
    iPhone_X = "iPhone_X"
    iPhone_8 = "iPhone 8"
    iPhone_7 = "iPhone 7"
    iPad_Pro_3 = "iPad Pro (12.9-inch) (3rd generation)"
    iPad_7 = "iPad (7th generation)"
    iPad_Air_2 = "iPad Air (2nd generation)"


class IosScreenOrientation(Enum):
    PORTRAIT = "portrait"
    LANDSCAPE_LEFT = "landscapeLeft"
    LANDSCAPE_RIGHT = "landscapeRight"


@attr.s(init=False)
class IosDeviceInfo(object):
    device_name = attr.ib(type=IosDeviceName, metadata={JsonInclude.NON_NONE: True})
    screen_orientation = attr.ib(
        type=IosScreenOrientation, metadata={JsonInclude.NON_NONE: True}
    )

    def __init__(self, device_name, screen_orientation=None):
        # type: (Union[IosDeviceName,Text], Union[IosScreenOrientation, Text]) -> None
        if isinstance(device_name, basestring):
            device_name = IosDeviceName(device_name)
        if isinstance(screen_orientation, basestring):
            screen_orientation = IosScreenOrientation(screen_orientation)
        self.device_name = device_name
        self.screen_orientation = screen_orientation


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
            BrowserType.EDGE_LEGACY,
        ]:
            return "windows"
        elif self.browser_type in [
            BrowserType.SAFARI,
            BrowserType.SAFARI_ONE_VERSION_BACK,
            BrowserType.SAFARI_TWO_VERSIONS_BACK,
        ]:
            return "mac os x"
        return "linux"
