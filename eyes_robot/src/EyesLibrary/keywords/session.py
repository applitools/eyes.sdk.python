from typing import TYPE_CHECKING, Optional, Text

from robot.libraries.BuiltIn import BuiltIn

from applitools.selenium import Eyes

if TYPE_CHECKING:
    from applitools.selenium import EyesWebDriver
    from applitools.common import TestResults, TestResultsSummary
    from applitools.common.utils.custom_types import ViewPort

from ..base import LibraryComponent, keyword


class RunnerKeywords(LibraryComponent):
    @keyword("Eyes Create Runner")
    def create_runner(self, type):
        self._create_eyes_runner_if_needed()

    @keyword("Eyes Get All Test Results")
    def get_all_tests_results(self):
        # type: () -> TestResultsSummary
        results = self.eyes_runner.get_all_test_results()
        self.info("Running tests result: {}".format(results))
        return results


class SessionKeywords(LibraryComponent):
    @keyword("Eyes Open")
    def open(self, app_name=None, test_name=None, viewport_size=None):
        # type: (Optional[Text],Optional[Text],Optional[ViewPort])->EyesWebDriver
        # Should be called before actual open
        config = self.parse_configuration_and_initialize_runner()

        if app_name:
            config.app_name = app_name
        if test_name:
            config.test_name = test_name
        if viewport_size:
            config.viewport_size = viewport_size
        eyes = Eyes(self.eyes_runner)
        eyes.set_configuration(config)
        self.register_eyes(eyes)
        if not eyes.configure.app_name:
            if app_name:
                eyes.configure.app_name = app_name
            else:
                raise ValueError("app_name should be provided")
        if not eyes.configure.test_name:
            if test_name:
                eyes.configure.test_name = test_name
            else:
                eyes.configure.test_name = BuiltIn().get_variable_value("${TEST NAME}")
        return eyes.open(self.fetch_driver())

    @keyword("Eyes Close")
    def close(self):
        # type: () -> Optional[TestResults]
        return self.current_eyes.close_async()

    @keyword("Eyes Abort")
    def abort(self):
        # type: () -> Optional[TestResults]
        return self.current_eyes.abort_async()