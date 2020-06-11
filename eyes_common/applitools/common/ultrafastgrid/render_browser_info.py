from abc import abstractmethod
from typing import Optional, Text, Union, overload, Dict

import attr

from applitools.common.geometry import RectangleSize
from applitools.common.selenium.misc import BrowserType
from applitools.common.utils import ABC
from applitools.common.utils.compat import basestring
from applitools.common.utils.json_utils import JsonInclude

from .config import (
    IosDeviceName,
    IosScreenOrientation,
    ScreenOrientation,
    DeviceName,
)


class IRenderBrowserInfo(ABC):
    @property
    @abstractmethod
    def platform(self):
        # type: () -> Text
        pass

    @property
    @abstractmethod
    def browser(self):
        # type: () -> Text
        pass

    @property
    @abstractmethod
    def width(self):
        # type: () -> int
        pass

    @property
    @abstractmethod
    def height(self):
        # type: () -> int
        pass

    @property
    def viewport_size(self):
        # type: () -> RectangleSize
        return RectangleSize(self.width, self.height)


@attr.s
class EmulationBaseInfo(IRenderBrowserInfo, ABC):
    device_name = attr.ib()
    screen_orientation = attr.ib()

    @property
    def width(self):
        # type: () -> int
        return 0

    @property
    def height(self):
        # type: () -> int
        return 0


@attr.s(hash=True, init=False)
class ChromeEmulationInfo(EmulationBaseInfo):
    device_name = attr.ib(
        type=DeviceName, metadata={JsonInclude.THIS: True}
    )  # type: DeviceName
    screen_orientation = attr.ib(
        type=ScreenOrientation, metadata={JsonInclude.NON_NONE: True}
    )  # type: ScreenOrientation

    def __init__(self, device_name, screen_orientation=ScreenOrientation.PORTRAIT):
        # type: (Union[DeviceName,Text], Union[ScreenOrientation, Text, None]) -> None
        if isinstance(device_name, basestring):
            device_name = DeviceName(device_name)
        if isinstance(screen_orientation, basestring):
            screen_orientation = ScreenOrientation(screen_orientation)
        self.device_name = device_name  # type: DeviceName
        self.screen_orientation = screen_orientation  # type: ScreenOrientation

    @property
    def browser(self):
        return BrowserType.CHROME.value

    @property
    def platform(self):
        # type: () -> Text
        return "linux"


@attr.s(hash=True, init=False)
class IosDeviceInfo(EmulationBaseInfo):
    device_name = attr.ib(
        type=IosDeviceName, metadata={JsonInclude.NAME: "name"}
    )  # type: IosDeviceName
    screen_orientation = attr.ib(
        type=IosScreenOrientation, metadata={JsonInclude.NON_NONE: True}
    )  # type: IosScreenOrientation

    def __init__(self, device_name, screen_orientation=None):
        # type: (Union[IosDeviceName,Text], Union[IosScreenOrientation, Text]) -> None
        if isinstance(device_name, basestring):
            device_name = IosDeviceName(device_name)
        if isinstance(screen_orientation, basestring):
            screen_orientation = IosScreenOrientation(screen_orientation)
        self.device_name = device_name  # type: IosDeviceName
        self.screen_orientation = screen_orientation  # type: IosScreenOrientation

    @property
    def platform(self):
        return "ios"

    @property
    def browser(self):
        return BrowserType.SAFARI.value


@attr.s(hash=True)
class RenderBrowserInfo(IRenderBrowserInfo):
    viewport_size = attr.ib(
        default=None, converter=attr.converters.optional(RectangleSize.from_)
    )  # type: Optional[RectangleSize]  # type: ignore
    browser_type = attr.ib(
        default=BrowserType.CHROME,
        converter=attr.converters.optional(BrowserType),
        type=BrowserType,
    )  # type: BrowserType
    baseline_env_name = attr.ib(default=None)  # type: Optional[Text]
    emulation_info = attr.ib(
        default=None, repr=False
    )  # type: Optional[EmulationBaseInfo]

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

    @property
    def browser(self):
        return self.browser_type.value if self.browser_type else None


@attr.s(hash=True, init=False)
class DesktopBrowserInfo(IRenderBrowserInfo):
    _width = attr.ib()  # type: int
    _height = attr.ib()  # type: int
    browser_type = attr.ib(type=BrowserType,)  # type: BrowserType
    baseline_env_name = attr.ib()  # type: Optional[Text]

    def __init__(
        self, width, height, browser_type=BrowserType.CHROME, baseline_env_name=None
    ):
        # type: (int, int, Union[BrowserType,Text], Optional[Text])->None
        self._width = width
        self._height = height
        self.browser_type = browser_type
        self.baseline_env_name = baseline_env_name

    @property
    def width(self):
        # type: () -> int
        return self._width

    @property
    def height(self):
        # type: () -> int
        return self._height

    @property
    def browser(self):
        return self.browser_type.value

    @property
    def platform(self):
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
