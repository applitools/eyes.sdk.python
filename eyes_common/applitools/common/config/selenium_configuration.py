from typing import List

import attr

from applitools.common.geometry import RectangleSize
from applitools.common.utils import argument_guard
from applitools.common.visual_grid import (
    ChromeEmulationInfo,
    RenderBrowserInfo,
    ScreenOrientation,
)

from .configuration import Configuration
from .misc import BrowserType, StitchMode

__all__ = ("SeleniumConfiguration",)


@attr.s
class SeleniumConfiguration(Configuration):
    DEFAULT_WAIT_BEFORE_SCREENSHOTS_MS = 1000  # ms

    force_full_page_screenshot = attr.ib(default=False)  # type: bool
    wait_before_screenshots = attr.ib(
        default=DEFAULT_WAIT_BEFORE_SCREENSHOTS_MS
    )  # type: int  # ms
    stitch_mode = attr.ib(default=StitchMode.Scroll)  # type: StitchMode
    hide_scrollbars = attr.ib(default=False)  # type: bool
    hide_caret = attr.ib(default=False)  # type: bool

    # Rendering Configuration
    is_throw_exception_on = False
    is_rendering_config = False
    _browsers_info = attr.ib(init=False, factory=list)  # type: List[RenderBrowserInfo]

    def add_browser(self, arg1, arg2=None, arg3=None):
        if isinstance(arg1, RenderBrowserInfo):
            self._browsers_info.append(arg1)
        elif (
            isinstance(arg1, int)
            and isinstance(arg2, int)
            and isinstance(arg3, BrowserType)
        ):
            self._browsers_info.append(
                RenderBrowserInfo(
                    RectangleSize(arg1, arg2), arg3, self.baseline_env_name
                )
            )
        else:
            raise ValueError("Unsupported parameters")
        return self

    def add_device_emulation(self, device_name, orientation=ScreenOrientation.PORTRAIT):
        argument_guard.not_none(device_name)
        emu = ChromeEmulationInfo(device_name, orientation)
        self.add_browser(RenderBrowserInfo(emulation_info=emu))
        return self

    @property
    def browsers_info(self):
        if self._browsers_info:
            return self._browsers_info
        browser_info = RenderBrowserInfo(
            viewport_size=self.viewport_size,
            browser_type=BrowserType.CHROME,
            baseline_env_name=self.baseline_env_name,
        )
        return [browser_info]

    @staticmethod
    def all_fields():
        return list(attr.fields_dict(SeleniumConfiguration).keys())
