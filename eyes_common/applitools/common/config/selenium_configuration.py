from typing import List

import attr

from applitools.common.utils import argument_guard
from applitools.common.visualgridclient.model import (
    EmulationDevice,
    EmulationInfo,
    RenderBrowserInfo,
)

from .configuration import Configuration
from .misc import BrowserType, StitchMode

__all__ = ("SeleniumConfiguration",)


@attr.s
class SeleniumConfiguration(Configuration):
    DEFAULT_WAIT_BEFORE_SCREENSHOTS = 100

    force_full_page_screenshot = attr.ib(default=False)  # type: bool
    wait_before_screenshots = attr.ib(
        default=DEFAULT_WAIT_BEFORE_SCREENSHOTS
    )  # type: int
    stitch_mode = attr.ib(default=StitchMode.Scroll)  # type: StitchMode
    hide_scrollbars = attr.ib(default=False)  # type: bool
    hide_caret = attr.ib(default=False)  # type: bool

    # Rendering Configuration
    is_throw_exception_on = False
    is_rendering_config = False
    _browsers_info = attr.ib(init=False, factory=list)  # type: List[RenderBrowserInfo]

    # TODO: add browser and browsers with width and height
    def add_browsers(self, *browsers_info):
        argument_guard.are_(browsers_info, RenderBrowserInfo)
        self._browsers_info.extend(browsers_info)
        return self

    def add_browser(self, browser_info):
        argument_guard.is_a(browser_info, RenderBrowserInfo)
        self._browsers_info.append(browser_info)
        return self

    # TODO: add add_device_emulation with baseline_env_name and width,height init
    def add_device_emulation(self, emulation_device):
        argument_guard.is_in(emulation_device, [EmulationDevice, EmulationInfo])
        browser_info = RenderBrowserInfo(
            emulation_device, baseline_env_name=self.baseline_env_name
        )
        self._browsers_info.append(browser_info)
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
