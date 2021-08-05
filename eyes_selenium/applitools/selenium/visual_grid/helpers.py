from time import time
from typing import TYPE_CHECKING, Optional, Union

from applitools.common import (
    DiffsFoundError,
    EyesError,
    NewTestError,
    TestFailedError,
    TestResultContainer,
    TestResults,
    logger,
)
from applitools.common.utils import datetime_utils, iteritems

if TYPE_CHECKING:
    from typing import Callable, Dict, List

    from applitools.selenium.visual_grid import RunningTest


def wait_till_tests_completed(test_provider, timeout_ms):
    # type: (Union[Callable, List], Optional[int]) -> None
    def get_tests(provider):
        if isinstance(test_provider, list):
            return test_provider
        return test_provider()

    deadline = time() + datetime_utils.to_sec(timeout_ms) if timeout_ms else None
    while deadline is None or time() < deadline:
        states = list(set(t.state for t in get_tests(test_provider)))
        if not states:
            # probably some exception is happened during execution
            break
        if len(states) == 1 and states[0] == "completed":
            break
        datetime_utils.sleep(1500, msg="Waiting for state completed!")
    else:
        logger.warning("Wait till tests completed timeout exceeded", timeout=timeout_ms)
        raise EyesError("Tests didn't finish in {} ms".format(timeout_ms))


def collect_test_results(tests, should_raise_exception):
    # type: (Dict[RunningTest, TestResults], bool) -> List[TestResultContainer]
    all_results = []
    for test, test_result in iteritems(tests):
        if test.pending_exceptions:
            logger.error(
                "During test execution above exception raised. \n {:s}".join(
                    str(e) for e in test.pending_exceptions
                )
            )
        if test.has_checks:
            exception = None
        else:
            exception = TestFailedError("Test has no checks")
        if test_result:
            scenario_id_or_name = test_result.name
            app_id_or_name = test_result.app_name
            if test_result.is_unresolved and not test_result.is_new:
                exception = DiffsFoundError(
                    test_result, scenario_id_or_name, app_id_or_name
                )
            if test_result.is_new:
                exception = NewTestError(
                    test_result, scenario_id_or_name, app_id_or_name
                )
            if test_result.is_failed:
                exception = TestFailedError(
                    test_result, scenario_id_or_name, app_id_or_name
                )
        else:
            exception = TestFailedError("Test haven't finished correctly")
        all_results.append(
            TestResultContainer(test_result, test.browser_info, exception)
        )
        if exception and should_raise_exception:
            raise exception
    return all_results
