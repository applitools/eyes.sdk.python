from abc import abstractmethod

from applitools.common import TestResultsSummary, logger
from applitools.common.utils import ABC, iteritems


class EyesRunner(ABC):
    def __init__(self):
        self._batch_server_connectors = {}

    @abstractmethod
    def get_all_test_results_impl(self, should_raise_exception=True):
        pass

    def get_all_test_results(self, should_raise_exception):
        # type: (bool) -> TestResultsSummary
        try:
            return self.get_all_test_results_impl(should_raise_exception)
        finally:
            self._delete_all_batches()

    def _delete_all_batches(self):
        for batch, connector in iteritems(self._batch_server_connectors):
            try:
                connector.close_batch(batch)
            except Exception as e:
                logger.exception(e)

    def add_batch(self, batch_id, batch_closer):
        if batch_id not in self._batch_server_connectors:
            self._batch_server_connectors[batch_id] = batch_closer
