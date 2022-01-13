import os
import traceback
import typing
from typing import TYPE_CHECKING, Dict, Union

from robot.api import logger as robot_logger
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError
from robotlibcore import DynamicCore
from six import raise_from
from six import string_types as basestring

from applitools.common import BatchInfo
from applitools.common.utils import argument_guard
from applitools.selenium import ClassicRunner, Eyes, VisualGridRunner
from applitools.selenium.eyes import EyesRunner

from .__version__ import __version__
from .config import RobotConfiguration
from .config_parser import (
    ConfigurationTrafaret,
    SelectedRunner,
    try_parse_configuration,
    try_parse_runner,
)
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
from .locator_converter import LocatorConverter

if TYPE_CHECKING:
    from typing import TYPE_CHECKING, Optional, Text

    from applitools.common.utils.custom_types import AnyWebDriver


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


class EyesLibrary(DynamicCore):
    """
    EyesLibrary is a visual verification library for [http://robotframework.org/|Robot Framework] that uses
    [https://applitools.com/docs/api/eyes-sdk/index-gen/classindex-selenium-python_sdk4.html|Applitools Eyes SDK Python] and
    [http://robotframework.org/SeleniumLibrary/SeleniumLibrary.html|SeleniumLibrary] /
    [http://serhatbolsu.github.io/robotframework-appiumlibrary/AppiumLibrary.html|AppiumLibrary].

    = Table of contents =
    - `Preconditions`
    - `Configuration`
    - `Writing tests`
    - `Importing`
    - `Keywords`

    = Preconditions =
    To run tests, you need to have the Applitools API key. If you have an Applitools account,
    you could fetch it from [https://eyes.applitools.com/app/admin/api-keys|dashboard],
    or you could create the [https://applitools.com/sign-up/|free account].
    You may want to read [https://applitools.com/docs|Applitools documentation] to understand better how Eyes works.

    = Configuration =
    EyesLibrary stores configuration file inside `applitools.yaml` config file.
     Detailed info you can find in [https://applitools.com/docs/api/robot/robot-configuration-file.html|configuration docs]

    The general options provide defaults for all run types. The other sections are for specific types of run and define their own configuration values. By default, they inherit the general options, but they can override any configuration if necessary.

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
    _eyes_runner = None  # type: Optional[VisualGridRunner, ClassicRunner]
    driver = None  # type: Optional[AnyWebDriver]
    _selected_runner = None  # type: Optional[SelectedRunner]
    supported_library_names_by_runner = {
        SelectedRunner.web: ("SeleniumLibrary", "AppiumLibrary"),
        SelectedRunner.web_ufg: ("SeleniumLibrary",),
        SelectedRunner.mobile_native: ("AppiumLibrary",),
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
            robot_logger.warn("No `runner` set. Using `web` runner.")

        robot_logger.console(
            "Running test suite with `{}` runner and `{}` config".format(runner, config)
        )

        self.run_on_failure_keyword = run_on_failure

        self._running_on_failure_keyword = False
        self._eyes_registry = EyesCache()
        self._batch_registry = {}  # type: Dict[Text, BatchInfo]
        self._running_keyword = None
        self._configuration = None

        self._selected_runner = try_parse_runner(runner)

        if is_test_run():
            self.current_library = self._try_get_library(self._selected_runner)
            suite_path = get_suite_path()
            self._configuration = try_parse_configuration(
                config, self._selected_runner, RobotConfiguration(), suite_path
            )
            validate_config(self._configuration)
            self.ROBOT_LIBRARY_LISTENER = LibraryListener(self)
            self._locator_converter = LocatorConverter(self)
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

    @property
    def eyes_runner(self):
        # type: () -> EyesRunner
        return self._eyes_runner

    @eyes_runner.setter
    def eyes_runner(self, runner):
        # type: (EyesRunner) -> None
        argument_guard.is_a(runner, (ClassicRunner, VisualGridRunner))
        self._eyes_runner = runner

    def clean_eyes_runner(self):
        self._eyes_runner = None

    def _try_get_library(self, runner):
        # type: (SelectedRunner) -> typing.ForwardRef
        """Check if supported library was loaded"""
        library_names = self.supported_library_names_by_runner[runner]
        supported_library = None
        failed_to_import = []
        for library_name in library_names:
            try:
                supported_library = BuiltIn().get_library_instance(name=library_name)
                robot_logger.console(
                    "Using library `{}` as backend".format(library_name)
                )
                break
            except RuntimeError:
                failed_to_import.append(library_name)

        if supported_library is None:
            raise EyesLibraryError(
                "Failed to find libraries {} for runner: {} in your test suite".format(
                    library_names, runner
                )
            )
        return supported_library

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

    def register_or_get_batch(self, batch):
        # type: (Union[basestring, BatchInfo]) -> BatchInfo
        if isinstance(batch, basestring):
            return self._batch_registry.setdefault(batch, BatchInfo(batch))
        elif isinstance(batch, BatchInfo):
            return self._batch_registry.setdefault(batch.id, batch)
        else:
            raise ValueError("Not supported `batch` value")

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
