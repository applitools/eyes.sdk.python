import abc

import attr

from applitools.common.utils import ABC


class EyesRunner(ABC):
    def __init__(self, server_url):
        self.server_url = server_url

    @abc.abstractmethod
    def get_all_test_results(self, should_throw_exception=False):
        pass


@attr.s
class TestResultContainer(object):
    _test_results = attr.ib()
    _exception = attr.ib()


class SeleniumGridRunner(EyesRunner):
    eyes = None
    _test_result = None

    def add_eyes(self, eyes):
        self.eyes = eyes

    def set_tests_results(self, result):
        self._test_result = result
        return result

    def get_all_test_results(self, should_throw_exception=False):
        result = [TestResultContainer(self._test_result, None)]
        return result


class VisualGridRunner(EyesRunner):
    pass
