import typing
from typing import TYPE_CHECKING, Optional

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from robotlibcore import DynamicCore
from SeleniumLibrary import RunOnFailureKeywords

from applitools.selenium import ClassicRunner, Configuration, Eyes, VisualGridRunner

from .eyes_cache import EyesCache
from .keywords import CheckKeywords, SessionKeywords, TargetKeywords
from .keywords.session import RunnerKeywords

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import AnyWebDriver

__version__ = "0.1.0"

EyesT = typing.TypeVar("EyesT", bound=Eyes)


class EyesLibrary(DynamicCore):
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_VERSION = __version__
    eyes_runner = None  # type: Optional[VisualGridRunner, ClassicRunner]
    config = Configuration(app_name="Test App")  # type: Configuration
    driver = None  # type: Optional[AnyWebDriver]

    def __init__(
        self,
        run_on_failure="Eyes Abort",
    ):
        self._eyes_registry = EyesCache()
        self._running_keyword = None
        self._running_on_failure_keyword = False
        self.run_on_failure_keyword = RunOnFailureKeywords.resolve_keyword(
            run_on_failure
        )

        keywords = [
            RunnerKeywords(self),
            SessionKeywords(self),
            CheckKeywords(self),
            TargetKeywords(self),
        ]

        DynamicCore.__init__(self, keywords)

    def run_keyword(self, name: str, args: tuple, kwargs: dict):
        try:
            return DynamicCore.run_keyword(self, name, args, kwargs)
        except Exception:
            self.failure_occurred()

    def failure_occurred(self):
        """Method that is executed when a SeleniumLibrary keyword fails.

        By default, executes the registered run-on-failure keyword.
        Libraries extending SeleniumLibrary can overwrite this hook
        method if they want to provide custom functionality instead.
        """
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

    def register_eyes(self, eyes, alias):
        """Add's a `Eyes` to the library EyesCache."""
        return self._eyes_registry.register(eyes, alias)

    @property
    def current_eyes(self):
        # type: () -> Eyes
        if not self._eyes_registry.current:
            raise RuntimeError("No Eyes is open.")
        return self._eyes_registry.current
