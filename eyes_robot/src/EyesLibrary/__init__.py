import traceback
import typing
from typing import TYPE_CHECKING, Optional, Text

import yaml
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from robotlibcore import DynamicCore

from applitools.common.utils.compat import raise_from
from applitools.selenium import ClassicRunner, Configuration, Eyes, VisualGridRunner

from .__version__ import __version__
from .config_parser import ConfigurationTrafaret, SelectedRunner
from .element_finder import ElementFinder
from .eyes_cache import EyesCache
from .keywords import (
    CheckKeywords,
    CheckSettingsKeywords,
    ConfigurationKeywords,
    SessionKeywords,
    TargetKeywords,
)
from .keywords.session import RunnerKeywords

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import AnyWebDriver


EyesT = typing.TypeVar("EyesT", bound=Eyes)


class EyesLibError(Exception):
    pass


class EyesLibrary(DynamicCore):
    """
    EyesLibrary is a visual verification library for [http://robotframework.org/|Robot Framework]. that uses
    [https://applitools.com/docs/api/eyes-sdk/index-gen/classindex-selenium-python_sdk4.html|Applitools Eyes SDK Python] and
    [http://robotframework.org/SeleniumLibrary/SeleniumLibrary.html|SeleniumLibrary] /
    [http://serhatbolsu.github.io/robotframework-appiumlibrary/AppiumLibrary.html|AppiumLibrary].

    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_VERSION = __version__
    eyes_runner = None  # type: Optional[VisualGridRunner, ClassicRunner]
    driver = None  # type: Optional[AnyWebDriver]
    raw_config = None  # type: Optional[dict]
    _selected_runner = None  # type: Optional[SelectedRunner]
    _log_level = None  # type: Optional[Text]

    def __init__(
        self,
        runner=None,  # type: Optional[Text]
        config=None,  # type: Optional[Text]
        log_level=None,  # type: Optional[Text]
        run_on_failure="Eyes Abort",
    ):
        # type: (Text, Text, Text, Text) -> None
        self._eyes_registry = EyesCache()
        self._running_keyword = None
        self._running_on_failure_keyword = False
        self.run_on_failure_keyword = run_on_failure
        self._element_finder = ElementFinder(self)
        self._log_level = log_level
        self._configuration = Configuration()

        if config:
            if isinstance(config, dict):
                self.raw_config = config
            else:
                with open(config, "r") as f:
                    self.raw_config = yaml.safe_load(f.read())

            self._selected_runner = SelectedRunner(runner)
            self._configuration = self.update_configuration(
                self._selected_runner, self.raw_config, self._configuration
            )

        keywords = [
            RunnerKeywords(self),
            SessionKeywords(self),
            CheckKeywords(self),
            TargetKeywords(self),
            CheckSettingsKeywords(self),
            ConfigurationKeywords(self),
        ]

        DynamicCore.__init__(self, keywords)

    def run_keyword(self, name, *args, **kwargs):
        try:
            return DynamicCore.run_keyword(self, name, *args, **kwargs)
        except Exception as e:
            trb_text = traceback.format_exc()
            self.failure_occurred(e, trb_text)

    def failure_occurred(self, origin_exc, trb_text):
        """Method that is executed when a keyword fails."""
        if self._running_on_failure_keyword or not self.run_on_failure_keyword:
            return
        try:
            self._running_on_failure_keyword = True
            if self.run_on_failure_keyword.lower() == "eyes abort":
                self.current_eyes.abort_async()
            else:
                BuiltIn().run_keyword(self.run_on_failure_keyword)
        except Exception as err:
            logger.warn(
                "Keyword '{}' could not be run on failure: {}".format(
                    self.run_on_failure_keyword, err
                )
            )
        finally:
            self._running_on_failure_keyword = False
            raise_from(
                EyesLibError("Failed to run EyesLibrary\n{}".format(trb_text)),
                origin_exc,
            )

    def register_eyes(self, eyes, alias):
        """Add's a `Eyes` to the library EyesCache."""
        return self._eyes_registry.register(eyes, alias)

    @property
    def current_eyes(self):
        # type: () -> Eyes
        if not self._eyes_registry.current:
            raise RuntimeError("No Eyes is open.")
        return self._eyes_registry.current

    @property
    def selected_runner(self):
        # type: () -> SelectedRunner
        if self._selected_runner is None:
            raise RuntimeError("No runner have been selected yet.")
        return self._selected_runner

    @property
    def configure(self):
        return self._configuration

    def update_configuration(self, selected_runner, raw_config, configuration):
        # type: (SelectedRunner, dict, Configuration) -> Configuration
        return ConfigurationTrafaret(selected_runner, configuration).check(raw_config)
