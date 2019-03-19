from __future__ import absolute_import

import typing

from applitools.common.visualgridclient.services import EyesRunner, VisualGridRunner
from applitools.selenium.configuration import SeleniumConfiguration
from applitools.selenium.rendering import VisualGridEyes
from applitools.selenium.selenium_eyes import SeleniumEyes

if typing.TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver


class Eyes(object):
    EYES_BASE_SETTABLE_ATTRS = [
        "is_disabled",
        "agent_id",
        "failure_reports",
        "default_match_settings",
        "batch",
        "host_os",
        "host_app",
        "baseline_branch_name",
        "save_new_tests",
        "save_failed_tests",
        "branch_name",
        "parent_branch_name",
        "fail_on_new_test",
        "send_dom",
        "scale_ratio",
        "match_level",
        "match_timeout",
        "api_key",
        "server_url",
        "stitch_mode",
    ]
    SELENIUM_EYES_SETTABLE_ATTRS = [
        "hide_caret",
        "force_full_page_screenshot",
        "hide_scrollbars",
    ]
    SETTABLE_ATTRS = EYES_BASE_SETTABLE_ATTRS + SELENIUM_EYES_SETTABLE_ATTRS
    _is_visual_grid_eyes = False  # type: bool
    _visual_grid_eyes = None  # type: VisualGridEyes
    _selenium_eyes = None  # type: SeleniumEyes
    _runner = None  # type: EyesRunner
    _configuration = None  # type: SeleniumConfiguration
    _global_configuration = None  # type: SeleniumConfiguration
    _driver = None  # type: WebDriver
    _rotation = None  # # type: ImageRotation

    def __init__(self, runner=None):
        if runner is None:
            self._selenium_eyes = SeleniumEyes()
        else:
            self._runner = runner
            if isinstance(runner, VisualGridRunner):
                self._visual_grid_eyes = VisualGridRunner(runner)
                self._is_visual_grid_eyes = True
            else:
                # runner is SeleniumRunner
                self._selenium_eyes = SeleniumEyes()
                runner.add_eyes(self)

    @property
    def _delegate(self):
        if self._is_visual_grid_eyes:
            return self._visual_grid_eyes
        else:
            return self._selenium_eyes

    # # def open(self, webdriver, selenium_configuration):
    # def open(self, driver, app_name, test_name, viewport_size=None):
    #     if viewport_size is None:
    #         viewport_size = SeleniumEyes.get_viewport_size(driver)
    #     self._driver = driver
    #     if self._is_visual_grid_eyes:
    #         return self._visual_grid_eyes.open(driver, selenium_config)
    #     else:
    #         return self._selenium_eyes.open(driver, app_name, test_name, viewport_size)

    def __getattr__(self, name):
        return getattr(self._delegate, name)

    def __setattr__(self, name, value):
        if name in self.SETTABLE_ATTRS:
            setattr(self._delegate, name, value)
        else:
            super(Eyes, self).__setattr__(name, value)
