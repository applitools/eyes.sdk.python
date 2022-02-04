from __future__ import absolute_import, print_function, unicode_literals

import typing
from concurrent.futures import TimeoutError

from applitools.common import (
    DiffsFoundError,
    EyesError,
    NewTestError,
    TestFailedError,
    TestResultContainer,
    TestResultsSummary,
)
from applitools.common.config import DEFAULT_ALL_TEST_RESULTS_TIMEOUT

from .__version__ import __version__
from .command_executor import CommandExecutor, ManagerType
from .universal_sdk_types import demarshal_server_info, demarshal_test_results

if typing.TYPE_CHECKING:
    from typing import Optional, Union


class EyesRunner(object):
    AUTO_CLOSE_MODE_SYNC = True
    BASE_AGENT_ID = "eyes.sdk.python"

    def __init__(self, manager_type, concurrency=None, is_legacy=None):
        # type: (ManagerType, Optional[int], Optional[bool]) -> None
        self._commands = CommandExecutor.get_instance(self.BASE_AGENT_ID, __version__)
        self._ref = self._commands.core_make_manager(
            manager_type, concurrency, is_legacy
        )

    @classmethod
    def get_server_info(cls):
        cmd = CommandExecutor.get_instance(cls.BASE_AGENT_ID, __version__)
        result = cmd.server_get_info()
        return demarshal_server_info(result)

    def get_all_test_results(
        self, should_raise_exception=True, timeout=DEFAULT_ALL_TEST_RESULTS_TIMEOUT
    ):
        # type: (bool, Optional[int]) -> TestResultsSummary
        try:
            results = self._commands.manager_close_all_eyes(self._ref, timeout)
        except TimeoutError:
            raise EyesError("Tests didn't finish in {} seconds".format(timeout))
        # We don't have server_url, api_key and proxy settings in runner
        # USDK should return them back as a part of TestResults
        structured_results = demarshal_test_results(results, None)
        for r in structured_results:
            log_session_results_and_raise_exception(should_raise_exception, r)
        return TestResultsSummary(
            [TestResultContainer(result, None, None) for result in structured_results]
        )


class RunnerOptions(object):
    concurrency = 5

    def test_concurrency(self, value):
        # type: (int) -> RunnerOptions
        self.concurrency = value
        return self


class VisualGridRunner(EyesRunner):
    AUTO_CLOSE_MODE_SYNC = False

    def __init__(self, options_or_concurrency=RunnerOptions()):
        # type: (Union[RunnerOptions, int]) -> None
        if isinstance(options_or_concurrency, int):
            concurrency = options_or_concurrency * 5  # legacy factor
            is_legacy = True
        else:
            concurrency = options_or_concurrency.concurrency
            is_legacy = False
        super(VisualGridRunner, self).__init__(ManagerType.VG, concurrency, is_legacy)


class ClassicRunner(EyesRunner):
    def __init__(self):
        super(ClassicRunner, self).__init__(ManagerType.CLASSIC)


def log_session_results_and_raise_exception(raise_ex, results):
    results_url = results.url
    scenario_id_or_name = results.name
    app_id_or_name = results.app_name
    if results.steps == 0:
        print("--- Test has no checks. \n\tSee details at ", results_url)
        if raise_ex:
            raise TestFailedError(results, scenario_id_or_name, app_id_or_name)
    elif results.is_unresolved:
        if results.is_new:
            print(
                "--- New test ended. \n\tPlease approve the new baseline at",
                results_url,
            )
            if raise_ex:
                raise NewTestError(results, scenario_id_or_name, app_id_or_name)
        else:
            print("--- Differences are found. \n\tSee details at", results_url)
            if raise_ex:
                raise DiffsFoundError(results, scenario_id_or_name, app_id_or_name)
    elif results.is_failed:
        print("--- Failed test ended. \n\tSee details at", results_url)
        if raise_ex:
            raise TestFailedError(results, scenario_id_or_name, app_id_or_name)
    else:
        print("--- Test passed. \n\tSee details at", results_url)
