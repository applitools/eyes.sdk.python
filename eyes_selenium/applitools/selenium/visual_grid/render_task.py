import typing

import attr

from applitools.common import EyesError, RenderRequest, RenderStatus, logger
from applitools.common.utils import datetime_utils
from applitools.core import ServerConnector

from .vg_task import VGTask

if typing.TYPE_CHECKING:
    from typing import Callable, List

    from applitools.common import RenderStatusResults
    from applitools.selenium.visual_grid import EyesConnector, RunningTest


@attr.s(hash=False)
class RenderTask(VGTask):
    MAX_FAILS_COUNT = 5
    MAX_ITERATIONS = 2400  # poll_render_status for 1 hour

    server_connector = attr.ib(repr=False)  # type: ServerConnector
    render_requests = attr.ib(hash=False, repr=False)  # type: List[RenderRequest]
    running_tests = attr.ib(hash=False, factory=list)  # type: List[RunningTest]
    func_to_run = attr.ib(default=None, hash=False, repr=False)  # type: Callable

    def __attrs_post_init__(self):
        # type: () -> None
        self.func_to_run = self.perform  # type: Callable

    def perform(self):  # noqa
        # type: () -> List[RenderStatusResults]

        requests = self.render_requests
        fetch_fails = 0
        render_requests = None
        while True:
            try:
                render_requests = self.server_connector.render(*requests)
            except Exception:
                logger.exception("During rendering for requests {}".format(requests))
                fetch_fails += 1
                datetime_utils.sleep(
                    1500, msg="/render throws exception... sleeping for 1.5s"
                )
            if fetch_fails > self.MAX_FAILS_COUNT:
                raise EyesError(
                    "Render is failed. Max count retries reached for {}".format(
                        requests
                    )
                )
            if not render_requests:
                logger.error("running_renders is null")
                continue

            for i, running_render in enumerate(render_requests):
                requests[i].render_id = running_render.render_id
                need_more_resources = (
                    running_render.render_status == RenderStatus.NEED_MORE_RESOURCE
                )
                if need_more_resources or running_render.need_more_dom:
                    raise EyesError("Some resources wasn't uploaded")
            still_running = fetch_fails > self.MAX_FAILS_COUNT
            if not still_running:
                break

        return self.poll_render_status(requests)

    def poll_render_status(self, requests):
        # type: (List[RenderRequest]) -> List[RenderStatusResults]
        logger.debug("poll_render_status call with Requests {}".format(requests))
        iterations = 0
        statuses = []  # type: List[RenderStatusResults]
        fails_count = 0
        finished = False
        while True:
            if finished:
                break
            while True:
                try:
                    statuses = self.server_connector.render_status_by_id(
                        *[rq.render_id for rq in requests]
                    )
                except Exception as e:
                    logger.exception(e)
                    datetime_utils.sleep(
                        1000, msg="/render-status throws exception... sleeping for 1s"
                    )
                    fails_count += 1
                finally:
                    iterations += 1
                    datetime_utils.sleep(1500, msg="Rendering...")
                if iterations > self.MAX_ITERATIONS:
                    raise EyesError(
                        "Max iterations in poll_render_status has been reached "
                        "for render_id: \n {}".format(
                            "\n".join(s.render_id for s in statuses)
                        )
                    )
                if statuses or 0 < fails_count < 3:
                    break
            finished = bool(
                statuses
                and (
                    all(s.status != RenderStatus.RENDERING for s in statuses)
                    or iterations > self.MAX_ITERATIONS
                    or False
                )
            )
        return statuses

    def add_running_test(self, running_test):
        # type: (RunningTest) -> int
        if running_test in self.running_tests:
            raise EyesError(
                "The running test {} already exists in the render "
                "task".format(running_test)
            )
        self.running_tests.append(running_test)
        return len(self.running_tests) - 1
