from copy import deepcopy

from typing import TYPE_CHECKING, List, overload, Union, Text, Optional

import attr

from applitools.common.config import Configuration as ConfigurationBase
from applitools.common.utils import argument_guard
from applitools.common.ultrafastgrid import (
    ChromeEmulationInfo,
    RenderBrowserInfo,
    IRenderBrowserInfo,
    ScreenOrientation,
    IosDeviceInfo,
    DesktopBrowserInfo,
    VisualGridOption,
)
from applitools.common.validators import is_list_or_tuple
from applitools.common.utils.compat import raise_from
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
    _browsers_info = attr.ib(init=False, factory=list)  # type: List[IRenderBrowserInfo]
    visual_grid_options = attr.ib(
        default=None
    )  # type: Optional[List[VisualGridOption]]

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

    def set_visual_grid_options(self, *options):
        # type: (*VisualGridOption) -> Configuration
        argument_guard.are_(options, VisualGridOption)
        self.visual_grid_options = list(options)
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

    @overload  # noqa
    def add_browser(self, width, height, browser_type, baseline_env_name):
        # type: (int, int, BrowserType, Text) -> Configuration
        pass

    def add_browser(self, *args):  # noqa
        if isinstance(args[0], IRenderBrowserInfo):
            self._browsers_info.append(args[0])
        elif (
            isinstance(args[0], int)
            and isinstance(args[1], int)
            and isinstance(args[2], BrowserType)
        ):
            if len(args) == 4:
                baseline_env_name = args[3]
            else:
                baseline_env_name = self.baseline_env_name
            self._browsers_info.append(
                DesktopBrowserInfo(args[0], args[1], args[2], baseline_env_name)
            )
        else:
            raise TypeError(
                "Unsupported parameter: \n\ttype: {} \n\tvalue: {}".format(
                    type(args), args
                )
            )
        return self

    @overload
    def add_browsers(self, renders_info):
        # type:(List[Union[DesktopBrowserInfo,IosDeviceInfo,ChromeEmulationInfo]])->Configuration  # noqa
        pass

    @overload
    def add_browsers(self, renders_info):
        # type:(*Union[DesktopBrowserInfo,IosDeviceInfo,ChromeEmulationInfo])->Configuration
        pass

    def add_browsers(self, *renders_info):
        if len(renders_info) == 1 and is_list_or_tuple(renders_info[0]):
            renders_info = renders_info[0]

        for render_info in renders_info:
            try:
                self.add_browser(render_info)
            except TypeError as e:
                raise_from(TypeError("Wrong argument in .add_browsers()"), e)
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
            browser_info = DesktopBrowserInfo(
                width=self.viewport_size["width"],
                height=self.viewport_size["height"],
                browser_type=BrowserType.CHROME,
                baseline_env_name=self.baseline_env_name,
            )
            return [browser_info]
        return []

    def clone(self):
        # type: () -> Configuration
        # TODO: Remove this huck when get rid of Python2
        conf = super(Configuration, self).clone()
        conf._browsers_info = deepcopy(self._browsers_info)
        conf.visual_grid_options = deepcopy(self.visual_grid_options)
        return conf
