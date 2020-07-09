from abc import abstractmethod
from typing import Optional, Text, Union

import attr

from applitools.common.geometry import RectangleSize
from applitools.common.selenium.misc import BrowserType
from applitools.common.utils import ABC
from applitools.common.utils.json_utils import JsonInclude

from .config import (
    IosDeviceName,
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

    @property
    def baseline_env_name(self):
        # type: () -> Optional[Text]
        return self._baseline_env_name


@attr.s
class EmulationBaseInfo(ABC):
    device_name = attr.ib()  # type: Union[DeviceName,Text]
    screen_orientation = attr.ib()  # type:Union[ScreenOrientation,Text]


@attr.s(hash=True, init=False)
class ChromeEmulationInfo(EmulationBaseInfo, IRenderBrowserInfo):
    device_name = attr.ib(type=DeviceName, metadata={JsonInclude.THIS: True})
    screen_orientation = attr.ib(
        type=ScreenOrientation, metadata={JsonInclude.NON_NONE: True}
    )

    def __init__(
        self,
        device_name,  # type: Union[DeviceName,Text]
        screen_orientation=ScreenOrientation.PORTRAIT,  # type:Union[ScreenOrientation,Text] # noqa
        baseline_env_name=None,  # type: Optional[Text]
    ):
        # type: (...) -> None
        self.device_name = DeviceName(device_name)  # type: DeviceName
        self.screen_orientation = ScreenOrientation(
            screen_orientation
        )  # type: ScreenOrientation
        self._baseline_env_name = baseline_env_name  # type: Optional[Text]

    @property
    def width(self):
        # type: () -> int
        return 0

    @property
    def height(self):
        # type: () -> int
        return 0

    @property
    def browser(self):
        return BrowserType.CHROME.value

    @property
    def platform(self):
        # type: () -> Text
        return "linux"


@attr.s(hash=True, init=False)
class IosDeviceInfo(IRenderBrowserInfo):
    device_name = attr.ib(
        type=IosDeviceName, metadata={JsonInclude.NAME: "name"}
    )  # type: Union[DeviceName,Text]
    screen_orientation = attr.ib(
        type=ScreenOrientation, metadata={JsonInclude.NON_NONE: True}
    )  # type: Union[ScreenOrientation,Text]

    def __init__(
        self,
        device_name,  # type: Union[IosDeviceName,Text]
        screen_orientation=ScreenOrientation.PORTRAIT,  # type:Union[ScreenOrientation,Text] # noqa
        baseline_env_name=None,  # type: Optional[Text]
    ):
        self.device_name = IosDeviceName(device_name)  # type: IosDeviceName
        self.screen_orientation = ScreenOrientation(
            screen_orientation
        )  # type: ScreenOrientation
        self._baseline_env_name = baseline_env_name  # type: Optional[Text]

    @property
    def width(self):
        # type: () -> int
        return 0

    @property
    def height(self):
        # type: () -> int
        return 0

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
    browser_type = attr.ib(type=BrowserType)  # type: BrowserType

    def __init__(
        self, width, height, browser_type=BrowserType.CHROME, baseline_env_name=None
    ):
        # type: (int, int, Union[BrowserType,Text], Optional[Text])->None
        self._width = width  # type: int
        self._height = height  # type: int
        self._baseline_env_name = baseline_env_name
        self.browser_type = BrowserType(browser_type)  # type: BrowserType

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
