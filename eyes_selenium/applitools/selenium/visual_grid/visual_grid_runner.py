import concurrent
import itertools
import operator
import sys
import threading
import typing
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

from applitools.common import (
    DiffsFoundError,
    NewTestError,
    TestFailedError,
    TestResultContainer,
    TestResults,
    TestResultsSummary,
    logger,
)
from applitools.common.utils import datetime_utils, iteritems
from applitools.core import EyesRunner

from .resource_cache import ResourceCache

if typing.TYPE_CHECKING:
    from typing import Optional, List, Dict
    from applitools.common import RenderingInfo
    from applitools.selenium.visual_grid import (
        RunningTest,
        VisualGridEyes,
        EyesConnector,
        VGTask,
    )


class VisualGridRunner(EyesRunner):
    def __init__(self, concurrent_sessions=None):
        # type: (Optional[int]) -> None
        super(VisualGridRunner, self).__init__()
        self._all_test_results = {}  # type: Dict[RunningTest, TestResults]

        kwargs = {}
        if sys.version_info >= (3, 6):
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
            future = self._executor.submit(lambda task: task(), task)
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
        while True:
            states = [t.state for t in self._get_all_running_tests()]
            if not states:
                # probably some exception is happened during execution
                break
            counter = Counter(states)
            logger.debug("Current test states: \n {}".format(counter))
            states = list(set(states))
            if len(states) == 1 and states[0] == "completed":
                break
            datetime_utils.sleep(
                1500, msg="Waiting for state completed in get_all_test_results_impl",
            )
        # finish processing of all tasks and shutdown threads
        self._stop()

        all_results = []
        for test, test_result in iteritems(self._all_test_results):
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
                exception = NewTestError(
                    test_result, scenario_id_or_name, app_id_or_name
                )
            if test_result and test_result.is_failed:
                exception = TestFailedError(
                    test_result, scenario_id_or_name, app_id_or_name
                )
            all_results.append(
                TestResultContainer(test_result, test.browser_info, exception)
            )
            if exception and should_raise_exception:
                raise exception
        return TestResultsSummary(all_results)

    def _get_all_running_tests(self):
        # type: ()-> List[RunningTest]
        return list(itertools.chain.from_iterable(e.test_list for e in self.all_eyes))

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
