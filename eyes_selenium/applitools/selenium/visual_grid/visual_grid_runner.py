import concurrent
import itertools
import sys
import threading
import typing
from collections import Counter, deque
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from time import time

import attr

from applitools.common import TestResults, TestResultsSummary, logger
from applitools.common.client_event import ClientEvent, TraceLevel
from applitools.common.utils import datetime_utils, json_utils
from applitools.common.utils.compat import Queue
from applitools.core import EyesRunner
from applitools.selenium.visual_grid.rendreing_service import RenderingService
from applitools.selenium.visual_grid.running_test import COMPLETED

from .helpers import collect_test_results, wait_till_tests_completed
from .resource_cache import PutCache, ResourceCache

if typing.TYPE_CHECKING:
    from typing import Dict, List, Text, Union

    from applitools.core import ServerConnector
    from applitools.selenium.visual_grid import RunningTest, VGTask, VisualGridEyes


class RunnerOptions(object):
    def __init__(self):
        self._test_concurrency = _TestConcurrency()

    def test_concurrency(self, value):
        # type: (int) -> RunnerOptions
        self._test_concurrency = _TestConcurrency(
            _TestConcurrency.Kind.TEST_CONCURRENCY, value
        )
        return self

    def get_test_concurrency(self):
        # type: () -> _TestConcurrency
        return self._test_concurrency


@attr.s
class _TestConcurrency(object):
    class Kind(Enum):
        DEFAULT = "defaultConcurrency"
        TEST_CONCURRENCY = "testConcurrency"
        LEGACY = "concurrency"

    LEGACY_FACTOR = 5
    kind = attr.ib(default=Kind.DEFAULT)  # type: Text
    value = attr.ib(default=5)  # type: int


class _ResourceCollectionService(object):
    def __init__(self):
        self._queue = Queue()
        self._thread = threading.Thread(target=self._resource_collection, args=())
        self._thread.daemon = True
        self._thread.setName(self.__class__.__name__)
        self._thread.start()

    def _resource_collection(self):
        while True:
            task = self._queue.get()
            if task is None:
                break
            task()

    def add_task(self, task):
        self._queue.put(task)

    def shutdown(self):
        self._queue.put(None)


class VisualGridRunner(EyesRunner):
    def __init__(self, options_or_concurrency=RunnerOptions()):
        # type: (Union[RunnerOptions, int]) -> None
        if isinstance(options_or_concurrency, int):
            self._concurrency = _TestConcurrency(
                _TestConcurrency.Kind.LEGACY,
                options_or_concurrency * _TestConcurrency.LEGACY_FACTOR,
            )
        else:
            self._concurrency = options_or_concurrency.get_test_concurrency()

        super(VisualGridRunner, self).__init__()
        self._runner_started_log_sent = False
        self._last_states_logging_time = time()
        self._all_test_results = {}  # type: Dict[RunningTest, TestResults]

        kwargs = {}
        if sys.version_info[:2] >= (3, 6):
            kwargs["thread_name_prefix"] = "VGR-Executor"

        self.resource_cache = ResourceCache()  # type:ResourceCache
        self.put_cache = PutCache()  # type: PutCache
        self.all_eyes = []  # type: List[VisualGridEyes]
        self.still_running = True  # type: bool

        self._executor = ThreadPoolExecutor(
            max_workers=self._concurrency.value, **kwargs
        )
        self._future_to_task = ResourceCache()  # type:ResourceCache
        self._parallel_tests = []  # type: List[RunningTest]
        thread = threading.Thread(target=self._run, args=())
        thread.setName(self.__class__.__name__)
        thread.daemon = True
        thread.start()
        self._thread = thread

        self._resource_collection_service = _ResourceCollectionService()
        self.rendering_service = RenderingService()

    def add_resource_collection_task(self, task):
        self._resource_collection_service.add_task(task)

    def __del__(self):
        self._stop()

    def aggregate_result(self, test, test_result):
        # type: (RunningTest, TestResults) -> None
        self.logger.debug(
            "aggregate_result called", test_id=test.test_uuid, test_result=test_result
        )
        self._all_test_results[test] = test_result

    def open(self, eyes):
        # type: (VisualGridEyes) -> None
        self.all_eyes.append(eyes)
        self.logger.debug("VisualGridRunner.open()", eyes_id=id(eyes))
        if not self._runner_started_log_sent:
            self._runner_started_log_sent = True
            self._send_runner_started_log_message(eyes.server_connector)

    def _current_parallel_tests(self):
        concurrent_sessions = self._concurrency.value
        parallel_tests = [
            test for test in self._parallel_tests if test.state != COMPLETED
        ]
        tests_left = len(parallel_tests)
        if tests_left < concurrent_sessions:
            tests_to_add = concurrent_sessions - tests_left
            parallel_tests += self._get_n_not_completed_tests(tests_to_add)
            self._parallel_tests = parallel_tests
        return self._parallel_tests

    def _run(self):
        self.logger.debug("VisualGridRunner.run()")
        for test_queue in self._get_parallel_tests_by_round_robin():
            try:
                task = test_queue.popleft()
                self.logger.debug("VisualGridRunner got task", task=task)
            except IndexError:
                datetime_utils.sleep(10, msg="Waiting for task", verbose=False)
                continue
            future = self._executor.submit(task)
            self._future_to_task[future] = task
        self.logger.debug("VisualGridRunner.run() done")

    def _stop(self):
        # type: () -> None
        while any(r.state != COMPLETED for r in self._get_all_running_tests()):
            datetime_utils.sleep(500, msg="Waiting for finishing tests in stop")
        self.still_running = False
        for future in concurrent.futures.as_completed(self._future_to_task):
            task = self._future_to_task[future]
            try:
                future.result()
            except Exception:
                self.logger.exception("Task generated an exception", task=task)

        self.put_cache.shutdown()
        self._resource_collection_service.shutdown()
        self.resource_cache.executor.shutdown()
        self._executor.shutdown()
        self._thread.join()
        self.rendering_service.shutdown()

    def _get_all_test_results_impl(self, should_raise_exception=True):
        # type: (bool) -> TestResultsSummary
        wait_till_tests_completed(self._get_all_running_tests)

        # finish processing of all tasks and shutdown threads
        self._stop()

        all_results = collect_test_results(
            self._all_test_results, should_raise_exception
        )
        return TestResultsSummary(all_results)

    def _get_all_running_tests(self):
        # type: ()-> List[RunningTest]
        tests = list(itertools.chain.from_iterable(e.test_list for e in self.all_eyes))
        if time() - self._last_states_logging_time > 15:
            self._last_states_logging_time = time()
            # print states every 15 seconds
            counter = Counter(t.state for t in tests)
            self.logger.info("Current tests states", **counter)
        return tests

    def _get_n_not_completed_tests(self, n):
        all_tests = self._get_all_running_tests()
        not_opened = [
            test
            for test in all_tests
            if test.state != COMPLETED and test not in self._parallel_tests
        ]
        return not_opened[:n]

    def _get_parallel_tests_by_round_robin(self):
        # type: () -> List[VGTask]
        done = False
        next_test = 0
        while not done:
            current_tests = self._current_parallel_tests()
            if current_tests:
                index = next_test % len(current_tests)
                yield current_tests[index].queue
                next_test += 1
            else:
                if self.still_running:
                    yield deque()
                else:
                    done = True

    def _send_runner_started_log_message(self, server_connector):
        # type: (ServerConnector) -> None
        message = {
            "type": "runnerStarted",
            self._concurrency.kind.value: self._concurrency.value,
            # ... other properties like node version, os, architecture, etc.
        }
        server_connector.send_logs(
            ClientEvent(TraceLevel.Notice, json_utils.to_json(message))
        )
