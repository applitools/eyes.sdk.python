import typing

import attr

from applitools.common import Region, logger
from transitions import Machine

from .vg_task import RenderTask, VGTask

if typing.TYPE_CHECKING:
    from typing import List, Optional, Dict, Any
    from applitools.common.visual_grid import RenderStatusResults
    from applitools.common import (
        TestResults,
        SeleniumConfiguration,
        VisualGridSelector,
        RenderBrowserInfo,
    )
    from applitools.selenium.fluent import SeleniumCheckSettings
    from .visual_grid_runner import VisualGridRunner
    from .eyes_connector import EyesConnector

NEW = "new"
NOT_RENDERED = "not_rendered"
RENDERED = "rendered"
OPENED = "opened"
COMPLETED = "completed"
TESTED = "tested"

STATES = [NEW, NOT_RENDERED, OPENED, RENDERED, COMPLETED, TESTED]
TRANSITIONS = [
    {"trigger": "becomes_not_rendered", "source": NEW, "dest": NOT_RENDERED},
    {"trigger": "becomes_opened", "source": RENDERED, "dest": OPENED},
    {"trigger": "becomes_rendered", "source": NOT_RENDERED, "dest": RENDERED},
    {
        "trigger": "becomes_tested",
        "source": [NEW, NOT_RENDERED, OPENED],
        "dest": TESTED,
    },
    {
        "trigger": "becomes_completed",
        "source": [NOT_RENDERED, RENDERED, OPENED, TESTED],
        "dest": COMPLETED,
    },
]


@attr.s(hash=True)
class RunningTest(object):
    eyes = attr.ib(hash=False, repr=False)  # type: EyesConnector
    configuration = attr.ib(hash=False, repr=False)  # type: SeleniumConfiguration
    browser_info = attr.ib()  # type: RenderBrowserInfo
    # listener = attr.ib()  # type:
    region_selectors = attr.ib(
        init=False, factory=list, hash=False
    )  # type: List[VisualGridSelector]

    tasks_list = attr.ib(init=False, factory=list, hash=False)
    task_to_future_mapping = attr.ib(init=False, factory=dict, hash=False)

    def __attrs_post_init__(self):
        # type: () -> None
        self._initialize_vars()
        self._initialize_state_machine()
        self.open()

    def _initialize_vars(self):
        # type: () -> None
        self.open_queue = []  # type: List[VGTask]
        self.task_queue = []  # type: List[VGTask]
        self.render_queue = []  # type: List[RenderTask]
        self.close_queue = []  # type: List[VGTask]
        self.watch_open = {}  # type: Dict[VGTask, bool]
        self.watch_task = {}  # type: Dict[VGTask, bool]
        self.watch_render = {}  # type: Dict[RenderTask, bool]
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

    @property
    def queue(self):
        # type: () -> List
        if self.state == NEW:
            return []
        elif self.state == NOT_RENDERED:
            return self.render_queue
        elif self.state == RENDERED:
            return self.open_queue
        elif self.state == OPENED:
            if self.task_lock is None and self.task_queue:
                self.task_lock = self.task_queue[-1]
                return self.task_queue
            else:
                return self.task_queue
        elif self.state == TESTED:
            return self.close_queue
        elif self.state == COMPLETED:
            return []

    @property
    def score(self):
        # type: () -> int
        if self.state == NEW:
            return 0
        elif self.state == NOT_RENDERED:
            return len(self.render_queue) * 10
        elif self.state == RENDERED:
            return len(self.open_queue)
        elif self.state == OPENED:
            return len(self.task_queue)
        elif self.state == TESTED:
            return len(self.close_queue)
        elif self.state == COMPLETED:
            return 0

    def open(self):
        # type: () -> None
        open_task = VGTask(
            "open {}".format(self.browser_info),
            lambda: self.eyes.open(self.configuration),
        )
        logger.debug("RunningTest %s" % open_task.name)

        def on_task_succeeded(test_result):
            # type: (Optional[Any]) -> None
            logger.debug("open_task_succeeded: task.uuid: {}".format(open_task.uuid))
            self.watch_open[open_task] = True
            if self.all_tasks_completed(self.watch_open):
                self.becomes_opened()

        open_task.on_task_succeeded(on_task_succeeded)
        open_task.on_task_error(lambda e: self.pending_exceptions.append(e))
        self.open_queue.append(open_task)
        self.watch_open[open_task] = False

    def check(
        self,
        tag,  # type: str
        check_settings,  # type: SeleniumCheckSettings
        script_result,  # type: str
        visual_grid_manager,  # type: VisualGridRunner
        dom_url_mod=None,  # type: Optional[Any]
    ):
        # type: (...) -> None
        render_task = self._render_task(
            dom_url_mod, script_result, tag, visual_grid_manager
        )

        check_task = VGTask(
            "perform check {} {}".format(tag, check_settings),
            lambda: self.eyes.check(tag, check_settings, render_task.uuid),
        )

        def check_task_completed():
            # type: () -> None
            logger.debug("check_task_completed: task.uuid: {}".format(check_task.uuid))
            self.watch_task[check_task] = True
            if self.task_lock and self.task_lock.uuid == check_task.uuid:
                self.task_lock = None
            if self.all_tasks_completed(self.watch_task):
                self.becomes_tested()

        check_task.on_task_completed(check_task_completed)
        self.task_queue.insert(0, check_task)
        self.watch_task[check_task] = False

    def _render_task(self, dom_url_mod, script_result, tag, visual_grid_manager):
        # type: (Optional[Any], str, str, VisualGridRunner) -> RenderTask
        render_task = RenderTask(
            name="RunningTest.render {} - {}".format(
                self.configuration.short_description, tag
            ),
            script=script_result,
            running_test=self,
            resource_cache=visual_grid_manager.resource_cache,
            put_cache=visual_grid_manager.put_cache,
            rendering_info=visual_grid_manager.render_info(self.eyes),
            eyes_connector=self.eyes,
            dom_url_mod=dom_url_mod,
        )
        logger.debug("RunningTest %s" % render_task.name)

        def render_task_succeeded(render_status):
            # type: (RenderStatusResults) -> None
            logger.debug(
                "render_task_succeeded: task.uuid: {}".format(render_task.uuid)
            )
            if render_status:
                self.eyes.render_status_for_task(render_task.uuid, render_status)
            self.watch_render[render_task] = True
            if self.all_tasks_completed(self.watch_render):
                self.becomes_rendered()

        render_task.on_task_succeeded(render_task_succeeded)
        render_task.on_task_error(lambda e: self.becomes_completed())
        self.render_queue.append(render_task)
        self.watch_render[render_task] = False
        return render_task

    def close(self):
        # type: () -> Optional[Any]
        if self.state == NEW:
            self.becomes_completed()
            return None

        close_task = VGTask(
            "close {}".format(self.browser_info), lambda: self.eyes.close(False)
        )
        logger.debug("RunningTest %s" % close_task.name)
        close_task.on_task_succeeded(
            lambda test_result: setattr(self, "test_result", test_result)
        )
        close_task.on_task_error(lambda e: self.pending_exceptions.append(e))

        def on_task_completed():
            # type: () -> None
            logger.debug("close_task_completed: task.uuid: {}".format(close_task.uuid))
            self.watch_close[close_task] = True
            if self.all_tasks_completed(self.watch_close):
                self.becomes_completed()

        close_task.on_task_completed(on_task_completed)
        self.close_queue.append(close_task)
        self.watch_close[close_task] = False

    def all_tasks_completed(self, watch):
        # type: (Dict) -> bool
        if self.state == "completed":
            return True
        return all(state for state in watch.values())
