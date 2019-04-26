from __future__ import absolute_import

import typing

from applitools.common.config import SeleniumConfiguration

from .selenium_eyes import SeleniumEyes
from .visual_grid import VisualGridEyes, VisualGridRunner

if typing.TYPE_CHECKING:
    from typing import Text, Optional, Union, Callable, Any
    from selenium.webdriver.remote.webdriver import WebDriver
    from applitools.common.utils.custom_types import AnyWebDriver, ViewPort
    from .webdriver import EyesWebDriver


class Eyes(object):
    EYES_COMMON = [
        "base_agent_id",
        "is_debug_screenshot_provided",
        "abort_if_not_closed",
        "original_frame_chain",
        "close",
        "viewport_size",
        "stitch_content",
        "device_pixel_ratio",
        "scale_ratio",
        "position_provider",
        "full_agent_id",
        "agent_setup",
        "add_property",
        "is_opened",
        "clear_properties",
        "check",
        "check_window",
        "check_region",
        "check_region_by_element",
        "check_region_by_selector",
        "check_region_in_frame_by_selector",
        "set_viewport_size_static",
        "get_viewport_size_static",
        "add_mouse_trigger_by_element",
        "add_text_trigger_by_element",
    ]
    DELEGATE_TO_CONFIG = SeleniumConfiguration.all_fields()

    _is_visual_grid_eyes = False  # type: bool
    _visual_grid_eyes = None  # type: VisualGridEyes
    _selenium_eyes = None  # type: SeleniumEyes
    _runner = None  # type: Optional[VisualGridRunner]
    _driver = None  # type: Optional[WebDriver]
    configuration = SeleniumConfiguration()  # type: SeleniumConfiguration

    def __init__(self, runner=None):
        # type: (Optional[Any]) -> None
        # backward compatibility with settings server_url
        if isinstance(runner, str):
            self.configuration.server_url = runner
            runner = None

        if runner is None:
            self._selenium_eyes = SeleniumEyes(self)
        elif isinstance(runner, VisualGridRunner):
            self._runner = runner
            self._visual_grid_eyes = VisualGridEyes(runner, self)
            self._is_visual_grid_eyes = True
        else:
            raise ValueError("Wrong runner")

    @property
    def driver(self):
        # type: () -> EyesWebDriver
        return self._current_eyes.driver

    @property
    def _current_eyes(self):
        # type: () -> Union[SeleniumEyes, VisualGridEyes]
        if self._is_visual_grid_eyes:
            return self._visual_grid_eyes
        else:
            return self._selenium_eyes

    @property
    def send_dom(self):
        # type: () -> bool
        if not self._is_visual_grid_eyes:
            return self.configuration.send_dom
        return False

    def open(self, driver, app_name, test_name, viewport_size=None):
        # type: (AnyWebDriver, Text, Text, Optional[ViewPort]) -> EyesWebDriver
        if viewport_size is None:
            viewport_size = SeleniumEyes.get_viewport_size_static(driver)
        self.configuration.app_name = app_name
        self.configuration.test_name = test_name
        self.configuration.viewport_size = viewport_size  # type: ignore

        self._driver = driver

        if self._is_visual_grid_eyes:
            return self._visual_grid_eyes.open(driver)
        else:
            return self._selenium_eyes.open(driver)

    def __getattr__(self, name):
        # type: (str) -> Union[Callable, bool]
        if name in self.DELEGATE_TO_CONFIG:
            return getattr(self.configuration, name)
        if name in self.EYES_COMMON:
            return getattr(self._current_eyes, name)
        raise AttributeError("{} has not attr {}".format(self.__class__.__name__, name))

    def __setattr__(self, name, value):
        # type: (str, Any) -> None
        if name in self.DELEGATE_TO_CONFIG:
            setattr(self.configuration, name, value)

        if name in self.EYES_COMMON:
            setattr(self._current_eyes, name, value)
        else:
            super(Eyes, self).__setattr__(name, value)
