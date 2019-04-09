import itertools
import operator
import threading
import typing
from concurrent.futures.thread import ThreadPoolExecutor
from time import sleep

from applitools.common import logger

if typing.TYPE_CHECKING:
    from typing import Optional, List, Dict, Text
    from applitools.common import RenderingInfo, VGResource
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
        self.executor = ThreadPoolExecutor(max_workers=concurrent_sessions)

        self._rendering_info = None  # type: Optional[RenderingInfo]
        self.resource_cache = {}  # type: Dict[Text, VGResource]
        self.put_cache = {}  # type: Dict[Text, VGResource]
        self.all_eyes = []  # type: List[VisualGridEyes]
        self.test_result = None
        self.still_running = True
        thread = threading.Thread(target=self.run, args=())
        thread.setName(self.__class__.__name__)
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
        logger.info("opened")

    def run(self):
        # type: () -> None
        logger.debug("run")
        while self.still_running:
            try:
                task = self.task_queue.pop()
            except IndexError:
                sleep(1)
                continue
            # TODO: add parallelism
            task()

    def stop(self):
        # type: () -> None
        logger.debug("stop")
        while sum(r.score for r in self.all_running_tests) > 0:
            sleep(0.5)
        self.still_running = False
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
        return sorted(self.all_running_tests, key=operator.attrgetter("score"))

    @property
    def task_queue(self):
        # type: () -> List[VGTask]
        tests_to_run = self.all_running_tests_by_score
        if tests_to_run:
            test_to_run = tests_to_run[0]
            queue = test_to_run.queue if test_to_run.queue else []
        else:
            queue = []
        return queue
