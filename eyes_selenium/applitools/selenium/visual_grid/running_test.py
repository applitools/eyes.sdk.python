import itertools
import typing
from collections import defaultdict

import attr
from transitions import Machine

from applitools.common import Region, RenderRequest, RenderStatus, logger

from .render_task import RenderTask
from .resource_collection_task import ResourceCollectionTask
from .vg_task import VGTask

if typing.TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, Optional, Text

    from applitools.common import (
        RenderBrowserInfo,
        RenderStatusResults,
        TestResults,
        VisualGridSelector,
    )
    from applitools.common.selenium import Configuration
    from applitools.selenium.fluent import SeleniumCheckSettings

    from .eyes_connector import EyesConnector
    from .visual_grid_runner import VisualGridRunner

NEW = "new"
NOT_OPENED = "not_opened"
OPENED = "opened"
RENDERED = "rendered"
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
        "source": [NEW, NOT_OPENED, RENDERED, OPENED, TESTED],
        "dest": COMPLETED,
    },
]


@attr.s(hash=False, str=False)
class RunningTestCheck(VGTask):
    running_test = attr.ib(hash=False, repr=False)  # type: RunningTest

    check_settings = attr.ib(hash=False)  # type: SeleniumCheckSettings
    render_request = attr.ib()  # type: RenderRequest
    region_selectors = attr.ib(hash=False)  # type: List[List[VisualGridSelector]]
    source = attr.ib()  # type: Text

    regions = attr.ib(init=False, factory=list, hash=False)
    func_to_run = attr.ib(default=None, hash=False, repr=False)  # type: Callable

    def __attrs_post_init__(self):
        # type: () -> None
        self.func_to_run = self.perform  # type: Callable

    def __hash__(self):
        return hash(self.name + self.uuid)

    def perform(self):
        short_description = "{} of {}".format(
            self.running_test.configuration.test_name,
            self.running_test.configuration.app_name,
        )
        tag = self.check_settings.values.name

        render_task = self._render_task(tag, short_description)

        def check_run():
            logger.debug("check_run: render_task.uuid: {}".format(render_task.uuid))
            self.running_test.eyes.check(
                self.check_settings,
                render_task.uuid,
                self.region_selectors,
                self.regions,
                self.source,
            )

        check_task = VGTask(
            "perform check {} {}".format(tag, self.check_settings), check_run
        )

        def check_task_completed():
            # type: () -> None
            logger.debug("check_task_completed: task.uuid: {}".format(check_task.uuid))
            if self.running_test.all_tasks_completed(
                self.running_test.watch_running_test_check_close
            ):
                self.running_test.becomes_tested()

        def check_task_error(e):
            logger.debug("check_task_error: task.uuid: {}".format(check_task.uuid))
            self.running_test.pending_exceptions.append(e)

        check_task.on_task_completed(check_task_completed)
        check_task.on_task_error(check_task_error)

        return render_task(), check_task()

    def _render_task(self, tag, short_description):

        render_task = RenderTask(
            name="RunningTest.render {} - {}".format(short_description, tag),
            server_connector=self.running_test.eyes,
            render_requests=[self.render_request],
        )

        def render_task_succeeded(render_statuses):
            # type: (List[RenderStatusResults]) -> None
            logger.debug(
                "render_task_succeeded: task.uuid: {}".format(render_task.uuid)
            )
            render_status = render_statuses[0]

            if render_status:
                self.running_test.eyes.render_status_for_task(
                    render_task.uuid, render_status
                )
                if render_status.status == RenderStatus.RENDERED:
                    for vgr in render_status.selector_regions:
                        if vgr.error:
                            logger.error(vgr.error)
                        else:
                            self.regions.append(vgr.to_region())
                    logger.debug(
                        "render_task_succeeded: uuid: {}\n\tregions {}".format(
                            render_task.uuid, self.regions
                        )
                    )
                elif render_status and render_status.status == RenderStatus.ERROR:
                    del self.running_test.running_test_check_queue[:]
                    del self.running_test.open_queue[:]
                    del self.running_test.close_queue[:]
                    self.watch_open = {}
                    self.watch_task = {}
                    self.watch_close = {}
                    self.running_test.abort()
                    if self.running_test.all_tasks_completed(
                        self.running_test.watch_running_test_check_close
                    ):
                        self.running_test.becomes_tested()
            else:
                logger.error(
                    "Wrong render status! Render returned status {}".format(
                        render_status
                    )
                )
                self.running_test.becomes_completed()

        def render_task_error(e):
            logger.debug(
                "render_task_error: task.uuid: {}\n{}".format(render_task.uuid, str(e))
            )
            self.running_test.pending_exceptions.append(e)
            self.running_test.becomes_completed()

        render_task.on_task_succeeded(render_task_succeeded)
        render_task.on_task_error(render_task_error)
        return render_task


@attr.s(hash=True, str=False)
class RunningTest(object):
    eyes = attr.ib(hash=False, repr=False)  # type: EyesConnector
    configuration = attr.ib(hash=False, repr=False)  # type: Configuration
    browser_info = attr.ib()  # type: RenderBrowserInfo

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
        self._initialize_vars()
        self._initialize_state_machine()
        self.open()

    def _initialize_vars(self):
        # type: () -> None
        self.open_queue = []  # type: List[VGTask]
        self.running_test_check_queue = []  # type: List[RunningTestCheck]
        self.close_queue = []  # type: List[VGTask]
        self.watch_open = {}  # type: Dict[VGTask, bool]
        self.watch_running_test_check_close = {}  # type: Dict[RunningTestCheck, bool]
        self.watch_close = {}  # type: Dict[VGTask, bool]
        self.task_lock = None  # type: Optional[VGTask]
        self.test_result = None  # type: Optional[TestResults]
        self.pending_exceptions = []  # type: List[Exception]

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
        # type: () -> List
        if self.state == NEW:
            return []
        elif self.state == NOT_OPENED:
            return self.open_queue
        elif self.state == OPENED:
            if self.task_lock:
                return []
            elif self.running_test_check_queue:
                self.task_lock = self.running_test_check_queue[-1]
                return self.running_test_check_queue
        elif self.state == TESTED:
            return self.close_queue
        elif self.state == COMPLETED:
            return []
        else:
            raise TypeError("Unsupported state")

    @property
    def score(self):
        # type: () -> int
        if self.state == NEW:
            return 0
        elif self.state == NOT_OPENED:
            return len(self.open_queue)
        elif self.state == OPENED:
            return len(self.running_test_check_queue)
        elif self.state == TESTED:
            return len(self.close_queue)
        elif self.state == COMPLETED:
            return 0
        else:
            raise TypeError("Unsupported state")

    def open(self):
        # type: () -> None
        open_task = VGTask(
            "open {}".format(self.browser_info),
            lambda: self.eyes.open(self.configuration),
        )
        logger.debug("RunningTest %s" % open_task.name)

        def open_task_succeeded(test_result):
            # type: (Optional[Any]) -> None
            logger.debug("open_task_succeeded: task.uuid: {}".format(open_task.uuid))
            self.watch_open[open_task] = True
            if self.all_tasks_completed(self.watch_open):
                self.becomes_opened()

        def open_task_error(e):
            logger.debug(
                "open_task_error: task.uuid: {}\n{}".format(open_task.uuid, str(e))
            )
            self.pending_exceptions.append(e)
            self.becomes_completed()

        open_task.on_task_succeeded(open_task_succeeded)
        open_task.on_task_error(open_task_error)
        self.open_queue.append(open_task)
        self.watch_open[open_task] = False

    def check(
        self,
        check_settings,  # type: SeleniumCheckSettings
        visual_grid_manager,  # type: VisualGridRunner
        region_selectors,  # type: Dict
        render_request,  # type: RenderRequest
        source,  # type: Optional[Text]
    ):
        # type: (...) -> None
        logger.debug("RunningTest %s" % check_settings)
        running_test_check_task = RunningTestCheck(
            "RunningTestCheck({})".format(check_settings.values.name),
            self,
            check_settings,
            render_request,
            region_selectors,
            source,
        )

        def check_task_completed():
            # type: () -> None
            logger.debug(
                "check_task_completed: task.uuid: {}".format(
                    running_test_check_task.uuid
                )
            )
            self.watch_running_test_check_close[running_test_check_task] = True
            if self.task_lock and self.task_lock.uuid == running_test_check_task.uuid:
                self.task_lock = None
            if self.all_tasks_completed(self.watch_running_test_check_close):
                self.becomes_tested()

        def check_task_error(e):
            logger.debug(
                "check_task_error: task.uuid: {}".format(running_test_check_task.uuid)
            )
            self.pending_exceptions.append(e)

        running_test_check_task.on_task_completed(check_task_completed)
        running_test_check_task.on_task_error(check_task_error)

        self.running_test_check_queue.insert(0, running_test_check_task)
        self.watch_running_test_check_close[running_test_check_task] = False

    def close(self):
        # type: () -> Optional[Any]
        if self.state == NEW:
            self.becomes_completed()
            return None
        elif self.state in [NOT_OPENED, RENDERED, OPENED, TESTED]:
            close_task = VGTask(
                "close {}".format(self.browser_info), lambda: self.eyes.close(False)
            )
            logger.debug("RunningTest %s" % close_task.name)

            def close_task_succeeded(test_result):
                logger.debug(
                    "close_task_succeeded: task.uuid: {}".format(close_task.uuid)
                )
                self.test_result = test_result
                if callable(self.on_results):
                    self.on_results(test=self, test_result=test_result)

            def close_task_completed():
                # type: () -> None
                logger.debug(
                    "close_task_completed: task.uuid: {}".format(close_task.uuid)
                )
                self.watch_close[close_task] = True
                if self.all_tasks_completed(self.watch_close):
                    self.becomes_completed()

            def close_task_error(e):
                logger.debug(
                    "close_task_error: task.uuid: {}\n{}".format(
                        close_task.uuid, str(e)
                    )
                )
                self.pending_exceptions.append(e)

            close_task.on_task_succeeded(close_task_succeeded)
            close_task.on_task_completed(close_task_completed)
            close_task.on_task_error(close_task_error)
            self.close_queue.append(close_task)
            self.watch_close[close_task] = False

    def abort(self):
        # skip call of abort() in tests where close() already called
        if self.close_queue or self.state == COMPLETED:
            return None

        def ensure_and_abort():
            self.eyes._ensure_running_session()
            return self.eyes.abort()

        abort_task = VGTask("abort {}".format(self.browser_info), ensure_and_abort)
        logger.debug("RunningTest %s" % abort_task.name)

        def abort_task_succeeded(test_result):
            logger.debug("abort_task_succeeded: task.uuid: {}".format(abort_task.uuid))
            self.test_result = test_result
            if callable(self.on_results):
                self.on_results(test=self, test_result=test_result)

        def abort_task_completed():
            # type: () -> None
            logger.debug("abort_task_completed: task.uuid: {}".format(abort_task.uuid))
            self.watch_close[abort_task] = True
            if self.all_tasks_completed(self.watch_close):
                self.becomes_completed()

        def abort_task_error(e):
            logger.debug(
                "abort_task_error: task.uuid: {}\n{}".format(abort_task.uuid, str(e))
            )
            self.pending_exceptions.append(e)

        abort_task.on_task_succeeded(abort_task_succeeded)
        abort_task.on_task_completed(abort_task_completed)
        abort_task.on_task_error(abort_task_error)

        self.close_queue.append(abort_task)
        self.watch_close[abort_task] = False

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
