from __future__ import absolute_import, unicode_literals

import typing
from concurrent.futures import TimeoutError

from applitools.common import (
    DiffsFoundError,
    EyesError,
    NewTestError,
    TestFailedError,
    TestResultContainer,
    TestResultsSummary,
    logger,
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
    CHECK_WINDOW_FULLY_ARG_DEFAULT = None

    def __init__(self, manager_type, concurrency=None, is_legacy=None):
        # type: (ManagerType, Optional[int], Optional[bool]) -> None
        self.logger = logger.bind(runner=id(self))
        self._commands = CommandExecutor.create(self.BASE_AGENT_ID, __version__)
        self._ref = self._commands.core_make_manager(
            manager_type, concurrency, is_legacy
        )

    @classmethod
    def get_server_info(cls):
        with CommandExecutor.create(cls.BASE_AGENT_ID, __version__) as cmd:
            result = cmd.server_get_info()
            return demarshal_server_info(result)

    def get_all_test_results(
        self, should_raise_exception=True, timeout=DEFAULT_ALL_TEST_RESULTS_TIMEOUT
    ):
        # type: (bool, Optional[int]) -> TestResultsSummary
        if not self._commands:
            self.logger.error("Test results are already retrieved")
            return TestResultsSummary([])
        try:
            if self._ref:
                try:
                    results = self._commands.manager_close_all_eyes(self._ref, timeout)
                except TimeoutError:
                    self.logger.warning(
                        "Tests completion timeout exceeded", timeout=timeout
                    )
                    raise EyesError("Tests didn't finish in {} seconds".format(timeout))
                # We don't have server_url, api_key and proxy settings in runner
                # USDK should return them back as a part of TestResults
                structured_results = demarshal_test_results(results, None)
                for r in structured_results:
                    log_session_results_and_raise_exception(
                        self.logger, should_raise_exception, r
                    )
            else:
                structured_results = []
            return TestResultsSummary(
                [
                    TestResultContainer(result, None, None)
                    for result in structured_results
                ]
            )
        finally:
            self._ref = None
            self._commands.close()


class RunnerOptions(object):
    concurrency = 5

    def test_concurrency(self, value):
        # type: (int) -> RunnerOptions
        self.concurrency = value
        return self


class VisualGridRunner(EyesRunner):
    AUTO_CLOSE_MODE_SYNC = False
    CHECK_WINDOW_FULLY_ARG_DEFAULT = True

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


def log_session_results_and_raise_exception(logger, raise_ex, results):
    logger.info("close({}): {}".format(raise_ex, results))
    results_url = results.url
    scenario_id_or_name = results.name
    app_id_or_name = results.app_name
    if results.steps == 0:
        logger.info("--- Test has no checks. \n\tSee details at {}".format(results_url))
        if raise_ex:
            raise TestFailedError(results, scenario_id_or_name, app_id_or_name)
    elif results.is_unresolved:
        if results.is_new:
            logger.info(
                "--- New test ended. \n\tPlease approve the new baseline at {}".format(
                    results_url
                )
            )
            if raise_ex:
                raise NewTestError(results, scenario_id_or_name, app_id_or_name)
        else:
            logger.info(
                "--- Differences are found. \n\tSee details at {}".format(results_url)
            )
            if raise_ex:
                raise DiffsFoundError(results, scenario_id_or_name, app_id_or_name)
    elif results.is_failed:
        logger.info("--- Failed test ended. \n\tSee details at {}".format(results_url))
        if raise_ex:
            raise TestFailedError(results, scenario_id_or_name, app_id_or_name)
    else:
        logger.info("--- Test passed. \n\tSee details at {}".format(results_url))
