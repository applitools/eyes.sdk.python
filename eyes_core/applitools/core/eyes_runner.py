from abc import abstractmethod

from applitools.common import TestResultsSummary, logger
from applitools.common.utils import ABC, iteritems


class EyesRunner(ABC):
    def __init__(self):
        self._batch_server_connectors = {}

    @abstractmethod
    def get_all_test_results_impl(self, should_raise_exception):
        pass

    def get_all_test_results(self, should_raise_exception=True):
        # type: (bool) -> TestResultsSummary
        return self.get_all_test_results_impl(should_raise_exception)
