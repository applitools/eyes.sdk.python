from abc import abstractmethod
from typing import TYPE_CHECKING

from applitools.common import TestResultsSummary, logger
from applitools.common.config import DEFAULT_ALL_TEST_RESULTS_TIMEOUT
from applitools.common.utils import ABC, iteritems

if TYPE_CHECKING:
    from typing import Optional


class EyesRunner(ABC):
    def __init__(self):
        self.logger = logger.bind(runner_id=id(self))

    @abstractmethod
    def _get_all_test_results_impl(self, should_raise_exception, timeout):
        pass

    def get_all_test_results(
        self, should_raise_exception=True, timeout=DEFAULT_ALL_TEST_RESULTS_TIMEOUT
    ):
        # type: (bool, Optional[int]) -> TestResultsSummary
        self.logger.debug(
            "get_all_test_results called", should_raise_exception=should_raise_exception
        )
        summary = self._get_all_test_results_impl(should_raise_exception, timeout)
        self.logger.debug(str(summary))
        return summary
