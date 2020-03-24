from typing import TYPE_CHECKING, Union
from collections import Counter

from applitools.common import (
    logger,
    TestFailedError,
    DiffsFoundError,
    NewTestError,
    TestResultContainer,
    TestResults,
)
from applitools.common.utils import datetime_utils, iteritems

if TYPE_CHECKING:
    from typing import List, Dict, Callable
    from applitools.selenium.visual_grid import RunningTest


def wait_till_tests_completed(test_provider):
    # type: (Union[Callable, List]) -> None
    def get_tests(provider):
        if isinstance(test_provider, list):
            return test_provider
        return test_provider()

    while True:
        states = [t.state for t in get_tests(test_provider)]
        if not states:
            # probably some exception is happened during execution
            break
        counter = Counter(states)
        logger.info("Current test states: \n {}".format(counter))
        states = list(set(states))
        if len(states) == 1 and states[0] == "completed":
            break
        datetime_utils.sleep(
            1500, msg="Waiting for state completed!",
        )


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
        exception = None
        if test.test_result is None:
            exception = TestFailedError("Test haven't finished correctly")
        scenario_id_or_name = test_result.name
        app_id_or_name = test_result.app_name
        if test_result and test_result.is_unresolved and not test_result.is_new:
            exception = DiffsFoundError(
                test_result, scenario_id_or_name, app_id_or_name
            )
        if test_result and test_result.is_new:
            exception = NewTestError(test_result, scenario_id_or_name, app_id_or_name)
        if test_result and test_result.is_failed:
            exception = TestFailedError(
                test_result, scenario_id_or_name, app_id_or_name
            )
        all_results.append(
            TestResultContainer(test_result, test.browser_info, exception)
        )
        if exception and should_raise_exception:
            raise exception
    return all_results
