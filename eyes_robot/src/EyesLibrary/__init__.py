import logging
import os
import traceback
import typing
from typing import TYPE_CHECKING

import structlog
from robot.api import logger as robot_logger
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError
from robot.output.pyloggingconf import RobotHandler
from robotlibcore import DynamicCore

from applitools.common import logger as applitools_logger
from applitools.common.utils.compat import raise_from
from applitools.common.utils.converters import str2bool
from applitools.selenium import ClassicRunner, Configuration, Eyes, VisualGridRunner

from .__version__ import __version__
from .config_parser import (
    ConfigurationTrafaret,
    SelectedRunner,
    try_parse_configuration,
    try_parse_runner,
)
from .element_finder import ElementFinder
from .errors import EyesLibraryConfigError, EyesLibraryError
from .eyes_cache import EyesCache
from .keywords import (
    CheckKeywords,
    CheckSettingsKeywords,
    ConfigurationKeywords,
    SessionKeywords,
    TargetKeywords,
)
from .keywords.session import RunnerKeywords
from .library_listener import LibraryListener

if TYPE_CHECKING:
    from typing import TYPE_CHECKING, Literal, Optional, Text

    from applitools.common.utils.custom_types import AnyWebDriver


EyesT = typing.TypeVar("EyesT", bound=Eyes)


def get_suite_path():
    suite_source = BuiltIn().get_variable_value("${SUITE_SOURCE}")
    if os.path.isdir(suite_source):
        return suite_source
    return os.path.dirname(suite_source)


def is_test_run():
    try:
        BuiltIn()._get_context()
        return True
    except RobotNotRunningError:
        # run without test suite, probably `libdoc` generation
        return False


def validate_config(configuration):
    if configuration.api_key is None:
        raise EyesLibraryConfigError(
            "API key not set! Log in to https://applitools.com to obtain "
            "your API Key and set it to `applitools.yaml` or `APPLITOOLS_API_KEY`."
        )


class _RobotLogger(object):
    """
    A simple logger class to redirect logs to Robot Framework logger.
    """

    def __init__(self):
        logger = logging.getLogger("RobotFramework")
        self.level = logger.getEffectiveLevel()

    def configure(self, std_logger):
        # type: (logging.Logger) -> None
        handler = RobotHandler()
        handler.setLevel(self.level)
        handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                structlog.dev.ConsoleRenderer(), applitools_logger._pre_chain
            )
        )
        std_logger.addHandler(handler)


class EyesLibrary(DynamicCore):
    """
    EyesLibrary is a visual verification library for [http://robotframework.org/|Robot Framework]. that uses
    [https://applitools.com/docs/api/eyes-sdk/index-gen/classindex-selenium-python_sdk4.html|Applitools Eyes SDK Python] and
    [http://robotframework.org/SeleniumLibrary/SeleniumLibrary.html|SeleniumLibrary] /
    [http://serhatbolsu.github.io/robotframework-appiumlibrary/AppiumLibrary.html|AppiumLibrary].

    = Table of contents =
    - `Preconditions`
    - `Writing tests`
    - `Importing`
    - `Shortcuts`
    - `Keywords`

    = Preconditions =
    To run tests, you need to have the Applitools API key. If you have an Applitools account,
    you could fetch it from [https://eyes.applitools.com/app/admin/api-keys|dashboard],
    or you could create the [https://applitools.com/sign-up/|free account].
    You may want to read [https://applitools.com/docs|Applitools documentation] to understand better how Eyes works.

    Before running tests, you must initialize `applitools.yaml` configuration script in root of test suite:
        | python -m EyesLibrary init-config |

    Add your *API KEY* `applitools.yaml` or in *APPLITOOLS_API_KEY* env variable and import EyesLibrary into your Robot test suite:
        | Library | EyesLibrary | runner=web | config=path/to/applitools.yaml |

    = Writing tests =
    When writing the tests, the following structure must be adopted:

    1. *Eyes Open*

    A browser or application must be running when opening the session.
    To open a browser/application, consult the documentation for [http://robotframework.org/SeleniumLibrary/SeleniumLibrary.html|SeleniumLibrary]
    and/or [http://serhatbolsu.github.io/robotframework-appiumlibrary/AppiumLibrary.html|AppiumLibrary].

    Afterwards, the session may be opened. See `Eyes Open`.

    2. *Visual Checks*

    Between opening and closing the session, you can run your visual checks.

    See `Eyes Check Window`, `Eyes Check Region By Element`, `Eyes Check Region By Selector`, `Eyes Check Region By Coordinates`,
    `Eyes Check Frame By Element`, `Eyes Check Frame By Name`, `Eyes Check Frame By Index` and `Eyes Check Frame By Selector`.

    You can also verify if there's an open session with `Is Eyes Open`.

    3. *Eyes Close Async*

    See `Eyes Close Async`.

    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_VERSION = __version__
    eyes_runner = None  # type: Optional[VisualGridRunner, ClassicRunner]
    driver = None  # type: Optional[AnyWebDriver]
    raw_config = None  # type: Optional[dict]
    _selected_runner = None  # type: Optional[SelectedRunner]
    library_name_by_runner = {
        SelectedRunner.web: "SeleniumLibrary",
        SelectedRunner.web_ufg: "SeleniumLibrary",
        SelectedRunner.mobile_native: "AppiumLibrary",
    }

    def __init__(
        self,
        runner=None,  # type: Text
        config=None,  # type: Text
        run_on_failure="Eyes Abort Async",
    ):
        # type: (...) -> None
        """
        Initialize the EyesLibrary
            | =Arguments=      | =Description=  |
            | runner           | Specify one of `web`, `web_ufg`, or `mobile_native` runners (by default `web`)  |
            | config           | Path to applitools.yaml (if no specify, trying to find it in test suite dir)  |
            | run_on_failure   | Specify keyword to run in case of failure (By default `Eyes Abort Async`)  |

        """
        # skip loading of dynamic libraries during doc generation
        if config is None:
            # try to find `applitools.yaml` in test directory
            robot_logger.warn(
                "No `config` set. Trying to find `applitools.yaml` in current path"
            )
            config = "applitools.yaml"

        if runner is None:
            runner = SelectedRunner.web
            robot_logger.warn("No `runner` set. Using `selenium` runner.")

        self.run_on_failure_keyword = run_on_failure

        self._running_on_failure_keyword = False
        self._eyes_registry = EyesCache()
        self._running_keyword = None

        self._selected_runner = try_parse_runner(runner)

        if is_test_run():
            applitools_logger.set_logger(_RobotLogger())  # type: ignore
            self._configuration = Configuration()
            self.current_library = self._try_get_library(self._selected_runner)
            suite_source = get_suite_path()
            # parse config only if set path explicitly
            self._configuration = try_parse_configuration(
                config, self._selected_runner, self._configuration, suite_source
            )
            validate_config(self._configuration)
            self.ROBOT_LIBRARY_LISTENER = LibraryListener(self)
            self._element_finder = ElementFinder(self)
        else:
            # hide objects that uses dynamic loading for generation of documentation
            self.current_library = None

        keywords = [
            RunnerKeywords(self),
            SessionKeywords(self),
            CheckKeywords(self),
            TargetKeywords(self),
            CheckSettingsKeywords(self),
            ConfigurationKeywords(self),
        ]

        DynamicCore.__init__(self, keywords)

    def _try_get_library(self, runner):
        # type: (SelectedRunner) -> typing.ForwardRef
        """Check if `SeleniumLibrary` or `AppiumLibrary` was loaded"""
        library_name = self.library_name_by_runner[runner]
        try:
            return BuiltIn().get_library_instance(name=library_name)
        except RuntimeError as e:
            raise_from(
                RuntimeError(
                    "Specified runner: `{runner}` should be used with `{lib}` library. "
                    "Please, make sure that `{lib}` was properly imported".format(
                        runner=runner.value, lib=library_name
                    )
                ),
                e,
            )

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
            robot_logger.warn(
                "Keyword '{}' could not be run on failure: {}".format(
                    self.run_on_failure_keyword, err
                )
            )
        finally:
            self._running_on_failure_keyword = False
            raise_from(
                EyesLibraryError("Failed to run EyesLibrary\n{}".format(trb_text)),
                origin_exc,
            )

    def register_eyes(self, eyes, alias):
        """Add's a `Eyes` to the library EyesCache."""
        return self._eyes_registry.register(eyes, alias)

    @property
    def current_eyes(self):
        # type: () -> Eyes
        if not self._eyes_registry.current:
            raise RuntimeError("No opened Eyes.")
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
