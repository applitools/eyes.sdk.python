import itertools
import typing
import uuid
from collections import deque

import attr
from transitions import Machine

from applitools.common import RenderStatus, logger

from .vg_task import VGTask

if typing.TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Text

    from structlog import BoundLogger

    from applitools.common import (
        RenderBrowserInfo,
        RenderStatusResults,
        TestResults,
        VisualGridSelector,
    )
    from applitools.common.selenium import Configuration
    from applitools.selenium.fluent import SeleniumCheckSettings
    from applitools.selenium.visual_grid.rendreing_service import RenderingService

    from .eyes_connector import EyesConnector

NEW = "new"
NOT_OPENED = "not_opened"
OPENED = "opened"
COMPLETED = "completed"
TESTED = "tested"

STATES = [NEW, OPENED, NOT_OPENED, COMPLETED, TESTED]
TRANSITIONS = [
    {"trigger": "becomes_not_opened", "source": NEW, "dest": NOT_OPENED},
    {"trigger": "becomes_opened", "source": NOT_OPENED, "dest": OPENED},
    {
        "trigger": "becomes_tested",
        "source": [NEW, NOT_OPENED, OPENED],
        "dest": TESTED,
    },
    {
        "trigger": "becomes_completed",
        "source": [NEW, NOT_OPENED, OPENED, TESTED],
        "dest": COMPLETED,
    },
]

END_OF_CHECKS = object()


@attr.s(hash=False, str=False)
class RunningTestCheck(object):
    name = attr.ib()  # type: Text
    uuid = attr.ib(init=False, repr=False, factory=lambda: str(uuid.uuid4()))
    running_test = attr.ib(repr=False)  # type: RunningTest

    check_settings = attr.ib()  # type: SeleniumCheckSettings
    region_selectors = attr.ib()  # type: List[List[VisualGridSelector]]
    source = attr.ib()  # type: Text

    logger = attr.ib(init=False, repr=False)  # type: BoundLogger
    regions = attr.ib(init=False, factory=list)
    queue = attr.ib(init=False, factory=deque)

    def set_render_request(self, render_request):
        short_description = "{} of {}".format(
            self.running_test.configuration.test_name,
            self.running_test.configuration.app_name,
        )
        tag = self.check_settings.values.name
        render_task = self._render_task(tag, short_description, render_request)
        self.queue = deque([render_task])

    def __attrs_post_init__(self):
        self.logger = self.running_test.logger.bind(running_test_check=self)

    def __hash__(self):
        return hash(self.name + self.uuid)

    def _render_task(self, tag, short_description, render_request):
        def render_task_succeeded(render_status):
            # type: (List[RenderStatusResults]) -> None
            self.logger.debug("render_task_succeeded", task_uuid=render_task.uuid)
            if render_status:
                self.running_test.eyes.render_status_for_task(
                    render_task.uuid, render_status
                )
                if render_status.status == RenderStatus.RENDERED:
                    for vgr in render_status.selector_regions:
                        if vgr.error:
                            self.logger.error("Region error", vgr_error=vgr.error)
                        else:
                            self.regions.append(vgr.to_region())
                    self.logger.debug(
                        "render_task_succeeded rendered",
                        task_uuid=render_task.uuid,
                        regions=self.regions,
                    )
                    # schedule check task
                    self.queue.append(self._check_task(render_task, tag))
                elif render_status and render_status.status == RenderStatus.ERROR:
                    self.running_test.task_queue.clear()
                    self.running_test.open_queue.clear()
                    self.running_test.close_queue.clear()
                    self.running_test.watch_open = {}
                    self.running_test.watch_task = {}
                    self.running_test.watch_close = {}

                    self.running_test.abort()
                    self.running_test.becomes_tested()
            else:
                self.logger.error("Wrong render status", render_status=render_status)
                self.running_test.becomes_completed()

        def render_task_error(e):
            self.logger.debug(
                "render_task_error", task_uuid=render_task.uuid, exc_info=e
            )
            self.running_test.pending_exceptions.append(e)
            self.running_test.becomes_completed()

        render_task = VGTask(
            "RunningTest.render {} - {}".format(short_description, tag),
            lambda: self.running_test.rendering_service.render(
                render_request, render_task_succeeded, render_task_error
            ),
            self.logger,
        )
        return render_task

    def _check_task(self, render_task, tag):
        def check_run():
            self.logger.debug("check_run", task_uuid=render_task.uuid)
            self.running_test.eyes.check(
                self.check_settings,
                render_task.uuid,
                self.region_selectors,
                self.regions,
                self.source,
            )

        check_task = VGTask(
            "perform check {} {}".format(tag, self.check_settings),
            check_run,
            self.logger,
        )

        def check_task_completed():
            # type: () -> None
            self.logger.debug("check_task_completed", task_uuid=check_task.uuid)
            if (
                self.running_test.task_lock
                and self.running_test.task_lock.uuid == self.uuid
            ):
                self.running_test.task_lock = None

            self.running_test.watch_task[self] = True
            self.running_test.maybe_becomes_tested()

        def check_task_error(e):
            self.logger.debug("check_task_error", task_uuid=check_task.uuid)
            self.running_test.pending_exceptions.append(e)
            self.running_test.becomes_completed()

        check_task.on_task_completed(check_task_completed)
        check_task.on_task_error(check_task_error)
        return check_task


@attr.s(hash=True, str=False)
class RunningTest(object):
    eyes = attr.ib(hash=False, repr=False)  # type: EyesConnector
    configuration = attr.ib(hash=False, repr=False)  # type: Configuration
    browser_info = attr.ib()  # type: RenderBrowserInfo
    rendering_service = attr.ib(hash=False, repr=False)  # type: RenderingService
    logger = attr.ib(hash=False, repr=False)  # type: BoundLogger

    tasks_list = attr.ib(init=False, factory=list, hash=False)
    test_uuid = attr.ib(init=False)
    on_results = attr.ib(init=False, hash=False)
    state = attr.ib(init=False, hash=False)

    def __str__(self):
        return "RunningTest: state={} uuid={}".format(
            self.state, format(self.test_uuid)
        )

    def __attrs_post_init__(self):
        # type: () -> None
        self.logger = self.logger.bind(running_test=self)
        self._initialize_vars()
        self._initialize_state_machine()
        self.open()

    def _initialize_vars(self):
        # type: () -> None
        self.open_queue = deque()  # type: deque[VGTask]
        self.task_queue = deque()  # type: deque[RunningTestCheck]
        self.close_queue = deque()  # type: deque[VGTask]
        self.watch_open = {}  # type: Dict[VGTask, bool]
        self.watch_task = {}  # type: Dict[RunningTestCheck, bool]
        self.watch_close = {}  # type: Dict[VGTask, bool]
        self.task_lock = None  # type: Optional[VGTask]
        self.test_result = None  # type: Optional[TestResults]
        self.pending_exceptions = deque()  # type: deque[Exception]

    def _initialize_state_machine(self):
        # type: () -> None
        machine = Machine(
            model=self,
            states=STATES,
            transitions=TRANSITIONS,
            initial=NEW,
            send_event=True,
            queued=True,
        )
        self.machine = machine

    def on_results_received(self, func):
        self.on_results = func

    @property
    def queue(self):
        # type: () -> deque[VGTask]
        if self.state == NEW:
            return deque()
        elif self.state == NOT_OPENED:
            return self.open_queue
        elif self.state == OPENED:
            if self.task_lock:
                return self.task_lock.queue
            elif self.task_queue:
                item = self.task_queue.popleft()
                if item is END_OF_CHECKS:
                    # all checks are done and test is finished
                    return self.close_queue
                else:
                    self.task_lock = item
                    return self.task_lock.queue
            return deque()
        elif self.state == TESTED:
            return self.close_queue
        elif self.state == COMPLETED:
            return deque()
        else:
            raise TypeError("Unsupported state")

    def open(self):
        # type: () -> None
        open_task = VGTask(
            "open {}".format(self.browser_info),
            lambda: self.eyes.open(self.configuration),
            self.logger,
        )
        self.logger.debug("RunningTest VGTask created", task_name=open_task.name)

        def open_task_succeeded(test_result):
            # type: (Optional[Any]) -> None
            self.logger.debug("open_task_succeeded")
            self.watch_open[open_task] = True
            if self.all_tasks_completed(self.watch_open):
                if self.state == TESTED:
                    self.logger.debug("open_task_succeeded: test session was aborted")
                    return
                self.becomes_opened()

        def open_task_error(e):
            self.logger.debug("open_task_error", exc_info=e)
            self.pending_exceptions.append(e)
            self.becomes_completed()

        open_task.on_task_succeeded(open_task_succeeded)
        open_task.on_task_error(open_task_error)
        self.open_queue.append(open_task)
        self.watch_open[open_task] = False

    def check(
        self,
        check_settings,  # type: SeleniumCheckSettings
        region_selectors,  # type: List[List[VisualGridSelector]]
        source,  # type: Optional[Text]
    ):
        # type: (...) -> RunningTestCheck
        self.logger.debug("RunningTest.check", check_settings=check_settings)
        running_test_check_task = RunningTestCheck(
            "RunningTestCheck({})".format(check_settings.values.name),
            self,
            check_settings,
            region_selectors,
            source,
        )

        self.task_queue.append(running_test_check_task)
        self.watch_task[running_test_check_task] = False
        return running_test_check_task

    def close(self):
        # type: () -> Optional[Any]
        if self.state == NEW:
            self.becomes_completed()
            return None
        elif self.state in [NOT_OPENED, OPENED, TESTED]:
            close_task = VGTask(
                "close {}".format(self.browser_info),
                lambda: self.eyes.is_open and self.eyes.close(False),
                self.logger,
            )
            self.logger.debug("RunningTest VGTask", task_name=close_task.name)

            def close_task_succeeded(test_result):
                self.logger.debug("close_task_succeeded")
                # abort() could add test_result already
                if self.test_result is None and test_result:
                    self.test_result = test_result
                    if callable(self.on_results):
                        self.on_results(test=self, test_result=test_result)

            def close_task_completed():
                # type: () -> None
                self.logger.debug("close_task_completed")
                self.watch_close[close_task] = True
                if self.all_tasks_completed(self.watch_close):
                    self.becomes_completed()

            def close_task_error(e):
                self.logger.debug("close_task_error", exc_info=e)
                self.pending_exceptions.append(e)

            close_task.on_task_succeeded(close_task_succeeded)
            close_task.on_task_completed(close_task_completed)
            close_task.on_task_error(close_task_error)
            self.close_queue.append(close_task)
            self.watch_close[close_task] = False
            self.task_queue.append(END_OF_CHECKS)

    def abort(self):
        # skip call of abort() in tests where close() already called
        if self.close_queue or self.state == COMPLETED:
            return None

        def ensure_and_abort():
            if not self.eyes.is_open:
                # open new session if no opened
                self.eyes._ensure_running_session()
            return self.eyes.abort()

        abort_task = VGTask(
            "abort {}".format(self.browser_info), ensure_and_abort, self.logger
        )
        self.logger.debug("RunningTest VGTask created", task_name=abort_task.name)

        def abort_task_succeeded(test_result):
            self.logger.debug("abort_task_succeeded", task_uuid=abort_task.uuid)
            self.test_result = test_result
            if callable(self.on_results):
                self.on_results(test=self, test_result=test_result)

        def abort_task_completed():
            # type: () -> None
            self.logger.debug("abort_task_completed", task_uuid=abort_task.uuid)
            self.watch_close[abort_task] = True
            if self.all_tasks_completed(self.watch_close):
                self.becomes_completed()

        def abort_task_error(e):
            self.logger.debug("abort_task_error", task_uuid=abort_task.uuid, exc_info=e)
            self.pending_exceptions.append(e)

        abort_task.on_task_succeeded(abort_task_succeeded)
        abort_task.on_task_completed(abort_task_completed)
        abort_task.on_task_error(abort_task_error)

        self.close_queue.append(abort_task)
        self.watch_close[abort_task] = False
        self.task_queue.append(END_OF_CHECKS)

    def all_tasks_completed(self, watch):
        # type: (Dict) -> bool
        if self.state == "completed":
            return True
        return all(watch.values())

    @staticmethod
    def _options_dict(configuration_options, check_settings_options):
        return {
            o.key: o.value
            for o in itertools.chain(
                configuration_options or (), check_settings_options or ()
            )
        }

    def maybe_becomes_tested(self):
        if self.close_queue and self.all_tasks_completed(self.watch_task):
            self.becomes_tested()

    @property
    def has_checks(self):
        return bool(self.watch_task)
