from __future__ import absolute_import, unicode_literals

from typing import TYPE_CHECKING, Text

from AppiumLibrary import AppiumLibrary
from robot.api import logger as robot_logger
from robot.api.deco import keyword  # noqa
from SeleniumLibrary import SeleniumLibrary

from applitools.common.utils import cached_property
from applitools.selenium import ClassicRunner, VisualGridRunner

from .config_parser import SelectedRunner
from .errors import EyesLibraryValueError

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import AnyWebDriver, BySelector
    from applitools.selenium import Eyes

    from . import EyesLibrary
    from .custom_types import Locator

__all__ = ("ContextAware", "LibraryComponent", "keyword")


class ContextAware(object):
    def __init__(self, ctx):
        # type: (EyesLibrary) -> None
        """Base class exposing attributes from the common context.

        :param ctx: The library itself as a context object.
        :type ctx: SeleniumLibrary.SeleniumLibrary
        """
        self.ctx = ctx
        self.log = robot_logger

    def from_locator_to_supported_form(self, locator):
        # type: (Locator) -> BySelector
        return self.ctx._locator_converter.to_by_selector(locator)

    def from_locators_to_supported_form(self, locator):
        # type: (Locator) -> list[BySelector]
        """
        Returns [By.NAME, 'selector'] with Selenium and Appium locators or WebElement
        """
        if isinstance(locator, list):
            return [self.from_locator_to_supported_form(loc) for loc in locator]
        else:
            return [self.from_locator_to_supported_form(locator)]

    @property
    def driver(self):
        return self.ctx.driver

    @property
    def library(self):
        return self.ctx.current_library

    @property
    def drivers(self):
        return self.ctx._drivers

    @cached_property
    def defined_keywords(self):
        # type: () -> list[str]
        return list(self.ctx.keywords.keys())


class RobotWebRunner(ClassicRunner):
    BASE_AGENT_ID = "eyes.python.robotframework.selenium"


class RobotMobileNativeRunner(ClassicRunner):
    BASE_AGENT_ID = "eyes.python.robotframework.appium"


class RobotWebUFGRunner(VisualGridRunner):
    BASE_AGENT_ID = "eyes.python.robotframework.visual_grid"


class LibraryComponent(ContextAware):
    _selected_runner = None
    _log_level = None
    _selected_runner_to_eyes_runner = {
        SelectedRunner.web: RobotWebRunner,
        SelectedRunner.mobile_native: RobotMobileNativeRunner,
        SelectedRunner.web_ufg: RobotWebUFGRunner,
    }

    def to_by_selector(self, locator):
        return self.ctx._locator_converter.to_by_selector(locator)

    def info(self, msg, html=False):
        # type: (Text, bool) -> None
        self.log.info(msg, html)

    def debug(self, msg, html=False):
        self.log.debug(msg, html)

    def warn(self, msg, html=False):
        # type: (Text, bool) -> None
        self.log.warn(msg, html)

    def log_to_console(self, msg):
        self.log.console(msg)

    def log_source(self, loglevel="INFO"):
        # type: (Text) -> None
        self.ctx.log_source(loglevel)

    def register_eyes(self, eyes, alias=None):
        self.ctx.register_eyes(eyes, alias)

    def get_configuration(self):
        return self.ctx.configure.clone()

    @property
    def eyes_runner(self):
        # type: () -> VisualGridRunner | ClassicRunner
        if self.ctx.eyes_runner is None:
            raise RuntimeError(
                "Eyes runner is None. Need to parse configuration "
                "and initialize runner first"
            )
        return self.ctx.eyes_runner

    @property
    def selected_runner(self):
        # type: () -> SelectedRunner
        return self.ctx.selected_runner

    @property
    def current_eyes(self):
        # type: () -> Eyes
        return self.ctx.current_eyes

    def _create_eyes_runner_if_needed(self):
        # type: () -> None
        if self.ctx.eyes_runner is None:
            # TODO: probably need to add runner_options to Configuration class
            runner_options = self.ctx.configure.runner_options
            selected_runner = self._selected_runner_to_eyes_runner[
                self.ctx.selected_runner
            ]

            self.ctx.eyes_runner = (
                selected_runner(runner_options) if runner_options else selected_runner()
            )

    def fetch_driver(self):
        # type: () -> AnyWebDriver
        if isinstance(self.ctx.current_library, SeleniumLibrary):
            return self.ctx.current_library.driver
        elif isinstance(self.ctx.current_library, AppiumLibrary):
            return self.ctx.current_library._current_application()
        else:
            raise EyesLibraryValueError(
                "Not supported library. Should be `SeleniumLibrary` or `AppiumLibrary`"
            )
