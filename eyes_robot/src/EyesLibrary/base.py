from copy import deepcopy
from typing import TYPE_CHECKING, Optional

import trafaret as trf
from robot.api import logger
from robot.api.deco import keyword  # noqa
from robot.libraries.BuiltIn import BuiltIn

from applitools.common import logger as applitools_logger
from applitools.selenium import ClassicRunner, Configuration, Eyes, VisualGridRunner

from .config import ConfigurationTrafaret, SelectedSDK, ToEnumTrafaret

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import AnyWebDriver

    from . import EyesLibrary

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

    @property
    def driver(self):
        return self.ctx.driver

    @property
    def drivers(self):
        return self.ctx._drivers


class LibraryComponent(ContextAware):
    _selected_sdk = None
    _log_level = None
    _eyes_runners = {
        SelectedSDK.appium: ClassicRunner,
        SelectedSDK.selenium: ClassicRunner,
        SelectedSDK.selenium_ufg: VisualGridRunner,
    }

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

    @property
    def selected_sdk(self):
        # type: () -> SelectedSDK
        if self._selected_sdk is None:
            raise RuntimeError("No SDK have been selected yet.")
        return self._selected_sdk

    def _create_eyes_runner_if_needed(self, selected_sdk=None):
        # type: (Optional[SelectedSDK]) -> None
        if self.ctx.eyes_runner is None:
            # TODO: add configs here
            selected_sdk = selected_sdk or self.selected_sdk
            self.ctx.eyes_runner = self._eyes_runners[selected_sdk]()

    def parse_configuration_and_initialize_runner(self):
        # type: () -> Configuration
        raw_config = BuiltIn().get_variable_value("&{applitools_conf}")
        raw_config_extra = BuiltIn().get_variable_value("&{applitools_extra_conf}", {})
        if raw_config is None:
            raise RuntimeError(
                "No applitools_conf variable present or incorrect. "
                "Check logs to see actuall error."
            )
        combined_raw_config = deepcopy(raw_config)
        combined_raw_config.update(raw_config_extra)

        self._selected_sdk = trf.Dict(
            runner=ToEnumTrafaret(SelectedSDK), ignore_extra="*"
        ).check(combined_raw_config)["runner"]
        self._log_level = trf.Dict(
            log_level=trf.Enum("VERBOSE", "INFO"), ignore_extra="*"
        ).check(combined_raw_config)["log_level"]

        self._create_eyes_runner_if_needed()
        return ConfigurationTrafaret().check(combined_raw_config)