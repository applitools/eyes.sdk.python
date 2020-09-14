from typing import TYPE_CHECKING

from applitools.common import TestResultContainer, TestResultsSummary
from applitools.core import EyesBase, EyesRunner

if TYPE_CHECKING:
    from typing import List, Optional

    from applitools.common import TestResults


class ClassicRunner(EyesRunner):
    def __init__(self):
        super(ClassicRunner, self).__init__()
        self._all_test_result = []  # type: List[TestResults]
        self.exception = None  # type: Optional[Exception]

    def _get_all_test_results_impl(self, should_raise_exception=True):
        # type: (bool) -> TestResultsSummary
        if should_raise_exception and self.exception:
            raise self.exception
        result = []
        for test_result in self._all_test_result:
            result.append(TestResultContainer(test_result, None, None))
            EyesBase.log_session_results_and_raise_exception(
                should_raise_exception, test_result
            )
        return TestResultsSummary(result)

    def aggregate_result(self, test_result):
        # type: (TestResults) -> None
        self._all_test_result.append(test_result)
