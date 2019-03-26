from __future__ import absolute_import

import typing

import attr

from applitools.common import TestResults, logger
from applitools.common.config import SeleniumConfiguration
from applitools.common.visualgridclient.services import EyesRunner, VisualGridRunner

from .rendering import VisualGridEyes
from .selenium_eyes import SeleniumEyes

if typing.TYPE_CHECKING:
    from concurrent.futures import Future
    from typing import List, Text, Optional
    from selenium.webdriver.remote.webdriver import WebDriver
    from applitools.common.utils.custom_types import AnyWebDriver, ViewPort
    from .webdriver import EyesWebDriver


class Eyes(object):
    EYES_COMMON = [
        "api_key",
        "server_url",
        "check",
        "abort_if_not_closed",
        "viewport_size",
        "stitch_content",
        "scale_ratio",
        "position_provider",
        "full_agent_id",
        "add_property",
        "clear_properties",
    ]
    DELEGATE_TO_CONFIG = list(attr.fields_dict(SeleniumConfiguration).keys())

    _is_visual_grid_eyes = False  # type: bool
    _visual_grid_eyes = None  # type: VisualGridEyes
    _selenium_eyes = None  # type: SeleniumEyes
    _runner = None  # type: EyesRunner
    _config = SeleniumConfiguration()  # type: SeleniumConfiguration
    _driver = None  # type: WebDriver
    _rotation = None  # # type: ImageRotation

    def __init__(self, runner=None):
        if runner is None:
            self._selenium_eyes = SeleniumEyes(self._config)
        else:
            self._runner = runner
            if isinstance(runner, VisualGridRunner):
                self._visual_grid_eyes = VisualGridEyes(runner, self._config)
                self._is_visual_grid_eyes = True
            else:
                # runner is SeleniumRunner
                self._selenium_eyes = SeleniumEyes(self._config)
                runner.add_eyes(self)

    @property
    def _current_eyes(self):
        if self._is_visual_grid_eyes:
            return self._visual_grid_eyes
        else:
            return self._selenium_eyes

    @property
    def send_dom(self):
        # type: () -> bool
        if not self._is_visual_grid_eyes:
            return self._config.send_dom
        return False

    def open(self, driver, app_name, test_name, viewport_size=None):
        # type: (AnyWebDriver, Text, Text, Optional[ViewPort]) -> EyesWebDriver
        if viewport_size is None:
            viewport_size = SeleniumEyes.get_viewport_size_static(driver)
        self._config.app_name = app_name
        self._config.test_name = test_name
        self._config.viewport_size = viewport_size

        self._driver = driver

        if self._is_visual_grid_eyes:
            return self._visual_grid_eyes.open(driver)
        else:
            return self._selenium_eyes.open(driver)

    def close(self):
        if self._is_visual_grid_eyes:
            futures = self._visual_grid_eyes.close()  # type: List[Future]
            if futures:
                try:
                    return futures[0].result()
                except Exception as e:
                    logger.exception(e)
        else:
            result = self._selenium_eyes.close()  # type: TestResults
            if self._runner:
                self._runner.test_result = result
            return result

    def __getattr__(self, name):
        if name in self.DELEGATE_TO_CONFIG:
            return getattr(self._config, name)
        if name in self.EYES_COMMON:
            return getattr(self._current_eyes, name)

    def __setattr__(self, name, value):
        if name in self.DELEGATE_TO_CONFIG:
            setattr(self._config, name, value)

        if name in self.EYES_COMMON:
            setattr(self._current_eyes, name, value)
        else:
            super(Eyes, self).__setattr__(name, value)
