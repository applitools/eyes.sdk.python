from typing import TYPE_CHECKING, Optional

from robot.api import logger
from robot.api.deco import keyword  # noqa
from robot.libraries.BuiltIn import BuiltIn

from applitools.common.utils import cached_property
from applitools.selenium import ClassicRunner, Eyes, VisualGridRunner
from applitools.selenium.validators import is_webelement

from .config_parser import SelectedRunner

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import AnyWebDriver, BySelector

    from . import EyesLibrary
    from .custom_types import Locator

__all__ = ("ContextAware", "LibraryComponent", "keyword")


class ContextAware:
    def __init__(self, ctx):
        # type: (EyesLibrary) -> None
        """Base class exposing attributes from the common context.

        :param ctx: The library itself as a context object.
        :type ctx: SeleniumLibrary.SeleniumLibrary
        """
        self.ctx = ctx
        # TODO: combine with `robot.logger`
        # self.log = applitools_logger.bind(class_=self.__class__.__name__)
        self.log = logger

    def find_element(self, locator):
        """Returns web element with Selenium and Appium locators"""
        return self.ctx._element_finder.find(locator)

    def get_by_selector_or_webelement(self, locator):
        # type: ( Locator) -> BySelector
        if is_webelement(locator):
            return locator
        return self.ctx._element_finder.convert_to_by_selector(locator)

    def get_by_selectors_or_webelements(self, locator):
        # type: (Locator) -> list[BySelector]
        """
        Returns [By.NAME, 'selector'] with Selenium and Appium locators or WebElement
        """
        if isinstance(locator, list):
            return [self.get_by_selector_or_webelement(loc) for loc in locator]
        else:
            return [self.get_by_selector_or_webelement(locator)]

    @property
    def driver(self):
        return self.ctx.driver

    @property
    def drivers(self):
        return self.ctx._drivers

    @cached_property
    def defined_keywords(self):
        # type: () -> list[str]
        return list(self.ctx.keywords.keys())


class LibraryComponent(ContextAware):
    _selected_runner = None
    _log_level = None
    _eyes_runners = {
        SelectedRunner.appium: ClassicRunner,
        SelectedRunner.selenium: ClassicRunner,
        SelectedRunner.selenium_ufg: VisualGridRunner,
    }

    def __init__(self, *args, **kwargs):
        super(LibraryComponent, self).__init__(*args, **kwargs)
        libraries = BuiltIn().get_library_instance(all=True)
        self._libraries = {
            SelectedRunner.appium: libraries.get("AppiumLibrary"),
            SelectedRunner.selenium: libraries.get("SeleniumLibrary"),
            SelectedRunner.selenium_ufg: libraries.get("SeleniumLibrary"),
        }

    def convert_to_by_selector(self, locator):
        return self.ctx._element_finder.convert_to_by_selector(locator)

    def info(self, msg: str, html: bool = False):
        self.log.info(msg, html)

    def debug(self, msg, html=False):
        self.log.debug(msg, html)

    def warn(self, msg: str, html: bool = False):
        self.log.warn(msg, html)

    def log_source(self, loglevel: str = "INFO"):
        self.ctx.log_source(loglevel)

    def register_eyes(self, eyes, alias=None):
        self.ctx.register_eyes(eyes, alias)

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
    def current_eyes(self):
        # type: () -> Eyes
        return self.ctx.current_eyes

    def _create_eyes_runner_if_needed(self, selected_sdk=None):
        # type: (Optional[SelectedRunner]) -> None
        if self.ctx.eyes_runner is None:
            # TODO: add configs for runner
            selected_sdk = selected_sdk or self.ctx.selected_runner
            # TODO: probably need to add runner_options to Configuration class
            runner_options = getattr(self.ctx.configure, "runner_options", {})
            self.ctx.eyes_runner = self._eyes_runners[selected_sdk](**runner_options)

    def fetch_driver(self):
        # type: () -> AnyWebDriver
        libraries = BuiltIn().get_library_instance(all=True)
        selenium_library = libraries.get("SeleniumLibrary")
        appium_library = libraries.get("AppiumLibrary")
        if selenium_library is None and appium_library is None:
            raise RuntimeError("Should be used SeleniumLibrary or AppiumLibrary")
        elif selenium_library and appium_library:
            raise RuntimeError(
                "Not possible to use both SeleniumLibrary and AppiumLibrary"
            )
        else:
            if selenium_library:
                return selenium_library.driver
            elif appium_library:
                return appium_library._current_application()
