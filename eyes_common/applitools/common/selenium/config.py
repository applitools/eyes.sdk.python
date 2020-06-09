from typing import TYPE_CHECKING, List, overload, Union

import attr

from applitools.common.config import Configuration as ConfigurationBase
from applitools.common.geometry import RectangleSize
from applitools.common.utils import argument_guard
from applitools.common.ultrafastgrid import (
    ChromeEmulationInfo,
    RenderBrowserInfo,
    ScreenOrientation,
    EmulationBaseInfo,
    IosDeviceInfo,
    DesktopBrowserInfo,
)

from .misc import BrowserType, StitchMode

if TYPE_CHECKING:
    from applitools.common.ultrafastgrid import DeviceName

__all__ = ("Configuration",)

DEFAULT_WAIT_BEFORE_SCREENSHOTS_MS = 1000  # type: int  # ms


@attr.s
class Configuration(ConfigurationBase):
    force_full_page_screenshot = attr.ib(default=None)  # type: bool
    wait_before_screenshots = attr.ib(
        default=DEFAULT_WAIT_BEFORE_SCREENSHOTS_MS
    )  # type: int  # ms
    stitch_mode = attr.ib(default=StitchMode.Scroll)  # type: StitchMode
    hide_scrollbars = attr.ib(default=False)  # type: bool
    hide_caret = attr.ib(default=False)  # type: bool

    # Rendering Configuration
    is_raise_exception_on = False  # type: bool
    is_rendering_config = False  # type: bool
    _browsers_info = attr.ib(init=False, factory=list)  # type: List[RenderBrowserInfo]

    def set_force_full_page_screenshot(self, force_full_page_screenshot):
        # type: (bool) -> Configuration
        self.force_full_page_screenshot = force_full_page_screenshot
        return self

    def set_wait_before_screenshots(self, wait_before_screenshots):
        # type: (int) -> Configuration
        self.wait_before_screenshots = wait_before_screenshots
        return self

    def set_stitch_mode(self, stitch_mode):
        # type: (StitchMode) -> Configuration
        self.stitch_mode = stitch_mode
        return self

    def set_hide_scrollbars(self, hide_scrollbars):
        # type: (bool) -> Configuration
        self.hide_scrollbars = hide_scrollbars
        return self

    def set_hide_caret(self, hide_caret):
        # type: (bool) -> Configuration
        self.hide_caret = hide_caret
        return self

    @overload  # noqa
    def add_browser(self, desktop_browser_info):
        # type: (DesktopBrowserInfo) -> Configuration
        pass

    @overload  # noqa
    def add_browser(self, ios_device_info):
        # type: (IosDeviceInfo) -> Configuration
        pass

    @overload  # noqa
    def add_browser(self, chrome_emulation_info):
        # type: (ChromeEmulationInfo) -> Configuration
        pass

    @overload  # noqa
    def add_browser(self, width, height, browser_type):
        # type: (int, int, BrowserType) -> Configuration
        pass

    def add_browser(self, *args):  # noqa
        if isinstance(args[0], RenderBrowserInfo):
            self._browsers_info.append(args[0])
        if isinstance(args[0], IosDeviceInfo):
            self._browsers_info.append(RenderBrowserInfo(ios_device_info=args[0]))
        elif isinstance(args[0], EmulationBaseInfo):
            self._browsers_info.append(RenderBrowserInfo(emulation_info=args[0]))
        elif (
            isinstance(args[0], int)
            and isinstance(args[1], int)
            and isinstance(args[2], BrowserType)
        ):
            self._browsers_info.append(
                RenderBrowserInfo(
                    RectangleSize(args[0], args[1]), args[2], self.baseline_env_name
                )
            )
        else:
            raise ValueError("Unsupported parameters")
        return self

    def add_browsers(self, *args):
        # type:(*Union[DesktopBrowserInfo,IosDeviceInfo,ChromeEmulationInfo])->Configuration
        for render_info in args:
            self.add_browser(render_info)
        return self

    def add_device_emulation(self, device_name, orientation=ScreenOrientation.PORTRAIT):
        # type: (DeviceName, ScreenOrientation) -> Configuration
        argument_guard.not_none(device_name)
        self.add_browser(ChromeEmulationInfo(device_name, orientation))
        return self

    @property
    def browsers_info(self):
        # type: () -> List[RenderBrowserInfo]
        if self._browsers_info:
            return self._browsers_info
        if self.viewport_size:
            browser_info = RenderBrowserInfo(
                viewport_size=self.viewport_size,
                browser_type=BrowserType.CHROME,
                baseline_env_name=self.baseline_env_name,
            )
            return [browser_info]
        return []
