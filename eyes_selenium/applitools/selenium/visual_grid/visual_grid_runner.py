import concurrent
import itertools
import operator
import sys
import threading
import typing
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from applitools.common import TestResults, TestResultsSummary, logger
from applitools.common.utils import counted, datetime_utils, iteritems
from applitools.core import EyesRunner

from .helpers import collect_test_results, wait_till_tests_completed
from .resource_cache import ResourceCache

if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional

    from applitools.selenium.visual_grid import RunningTest, VGTask, VisualGridEyes


class VisualGridRunner(EyesRunner):
    def __init__(self, concurrent_sessions=None):
        # type: (Optional[int]) -> None
        super(VisualGridRunner, self).__init__()
        self._all_test_results = {}  # type: Dict[RunningTest, TestResults]

        kwargs = {}
        if sys.version_info[:2] >= (3, 6):
            kwargs["thread_name_prefix"] = "VGR-Executor"

        self.resource_cache = ResourceCache()  # type:ResourceCache
        self.put_cache = ResourceCache()  # type:ResourceCache
        self.all_eyes = []  # type: List[VisualGridEyes]
        self.still_running = True  # type: bool

        self._executor = ThreadPoolExecutor(max_workers=concurrent_sessions, **kwargs)
        self._future_to_task = ResourceCache()  # type:ResourceCache
        thread = threading.Thread(target=self._run, args=())
        thread.setName(self.__class__.__name__)
        thread.daemon = True
        thread.start()
        self._thread = thread

    def __del__(self):
        self._stop()

    def aggregate_result(self, test, test_result):
        # type: (RunningTest, TestResults) -> None
        logger.debug(
            "aggregate_result({}, {}) called".format(test.test_uuid, test_result)
        )
        self._all_test_results[test] = test_result

    def open(self, eyes):
        # type: (VisualGridEyes) -> None
        self.all_eyes.append(eyes)
        logger.debug("VisualGridRunner.open(%s)" % eyes)

    def _run(self):
        logger.debug("VisualGridRunner.run()")
        while self.still_running:
            try:
                task = self._task_queue.pop()
                logger.debug("VisualGridRunner got task %s" % task)
            except IndexError:
                datetime_utils.sleep(1000, msg="Waiting for task")
                continue
            future = self._executor.submit(task)
            self._future_to_task[future] = task

    def _stop(self):
        # type: () -> None
        logger.debug("VisualGridRunner.stop()")
        while sum(r.score for r in self._get_all_running_tests()) > 0:
            datetime_utils.sleep(500, msg="Waiting for finishing tests in stop")
        self.still_running = False
        for future in concurrent.futures.as_completed(self._future_to_task):
            task = self._future_to_task[future]
            try:
                future.result()
            except Exception as exc:
                logger.exception("%r generated an exception: %s" % (task, exc))
            else:
                logger.debug("%s task ran" % task)

        self.put_cache.executor.shutdown()
        self.resource_cache.executor.shutdown()
        self._executor.shutdown()
        self._thread.join()

    def _get_all_test_results_impl(self, should_raise_exception=True):
        # type: (bool) -> TestResultsSummary
        wait_till_tests_completed(self._get_all_running_tests)

        # finish processing of all tasks and shutdown threads
        self._stop()

        all_results = collect_test_results(
            self._all_test_results, should_raise_exception
        )
        return TestResultsSummary(all_results)

    @counted
    def _get_all_running_tests(self):
        # type: ()-> List[RunningTest]
        tests = list(itertools.chain.from_iterable(e.test_list for e in self.all_eyes))
        if not bool(self._get_all_running_tests.calls % 15):
            # print state every 15 call
            counter = Counter(t.state for t in tests)
            logger.info(
                "Current tests states: \n{}".format(
                    "\n".join(["\t{} - {}".format(t, c) for t, c in iteritems(counter)])
                )
            )
        return tests

    def _get_all_running_tests_by_score(self):
        # type: () -> List[RunningTest]
        return sorted(
            self._get_all_running_tests(),
            key=operator.attrgetter("score"),
            reverse=True,
        )

    @property
    def _task_queue(self):
        # type: () -> List[VGTask]
        tests_to_run = self._get_all_running_tests_by_score()
        if tests_to_run:
            test_to_run = tests_to_run[0]
            queue = test_to_run.queue
        else:
            queue = []
        return queue
