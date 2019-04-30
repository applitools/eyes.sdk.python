import concurrent
import itertools
import operator
import threading
import typing
from concurrent.futures import ThreadPoolExecutor
from time import sleep

from applitools.common import logger
from applitools.selenium.visual_grid.resource_cache import ResourceCache

if typing.TYPE_CHECKING:
    from typing import Optional, List
    from applitools.common import RenderingInfo
    from applitools.selenium.visual_grid import (
        RunningTest,
        VisualGridEyes,
        EyesConnector,
        VGTask,
    )


class VisualGridRunner(object):
    def __init__(self, concurrent_sessions=None):
        # type: (Optional[int]) -> None
        self.concurrent_sessions = concurrent_sessions
        self.executor = ThreadPoolExecutor(
            max_workers=concurrent_sessions, thread_name_prefix="VGR-Executor"
        )
        self._rendering_info = None  # type: Optional[RenderingInfo]
        self.resource_cache = ResourceCache()
        self.put_cache = ResourceCache()
        self.all_eyes = []  # type: List[VisualGridEyes]
        self.test_result = None
        self.still_running = True
        self.future_to_task = ResourceCache()
        thread = threading.Thread(target=self.run, args=())
        thread.setName(self.__class__.__name__)
        thread.daemon = True
        thread.start()
        self.thread = thread

    def render_info(self, eyes_connector):
        # type: (EyesConnector) -> RenderingInfo
        if self._rendering_info is None:
            self._rendering_info = eyes_connector.render_info()
        return self._rendering_info

    def open(self, eyes):
        # type: (VisualGridEyes) -> None
        self.all_eyes.append(eyes)
        self._rendering_info = eyes.rendering_info
        logger.debug("VisualGridRunner.open(%s)" % eyes)

    def run(self):
        logger.debug("VisualGridRunner.run()")
        while self.still_running:
            try:
                task = self.task_queue.pop()
                logger.debug("VisualGridRunner got task %s" % task)
            except IndexError:
                sleep(1)
                continue
            future = self.executor.submit(lambda task: task(), task)
            self.future_to_task[future] = task

    def stop(self):
        # type: () -> None
        logger.debug("VisualGridRunner.stop()")
        while sum(r.score for r in self.all_running_tests) > 0:
            sleep(0.5)
        self.still_running = False
        for future in concurrent.futures.as_completed(self.future_to_task):
            task = self.future_to_task[future]
            try:
                future.result()
            except Exception as exc:
                logger.exception("%r generated an exception: %s" % (task, exc))
            else:
                logger.debug("%s task ran" % task)

        self.put_cache.executor.shutdown()
        self.resource_cache.executor.shutdown()
        self.executor.shutdown()
        self.thread.join()

    # def get_all_test_results(self):
    #     # type: () -> List[TestResults]
    #     while not any(e.is_opened for e in self.all_eyes):
    #         sleep(0.5)
    #     return list(
    #         itertools.chain.from_iterable(
    #             test.test_result
    #             for e in self.all_eyes
    #             for test in e.test_list
    #             if e.test_list
    #         )
    #     )

    @property
    def all_running_tests(self):
        # type: ()-> List[RunningTest]
        return list(itertools.chain.from_iterable(e.test_list for e in self.all_eyes))

    @property
    def all_running_tests_by_score(self):
        # type: () -> List[RunningTest]
        return sorted(
            self.all_running_tests, key=operator.attrgetter("score"), reverse=True
        )

    @property
    def task_queue(self):
        # type: () -> List[VGTask]
        tests_to_run = self.all_running_tests_by_score
        if tests_to_run:
            test_to_run = tests_to_run[0]
            queue = test_to_run.queue
        else:
            queue = []
        return queue
