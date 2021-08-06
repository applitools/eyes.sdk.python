import typing
from copy import deepcopy
from threading import Condition, Thread
from time import time

import attr

from applitools.common import EyesError, RenderStatus, logger
from applitools.common.utils import datetime_utils

if typing.TYPE_CHECKING:
    from typing import Callable, List, Text

    from applitools.common import RenderRequest, RenderStatusResults
    from applitools.core import ServerConnector


MAX_STATUS_CHECK_SECONDS = 60 * 60


class RenderingService(object):
    def __init__(self):
        self._server_connector = None  # type: ServerConnector
        self._shutdown = False
        self._render_tasks = []  # type: List[_Render]
        self._have_render_tasks = Condition()
        self._status_tasks = []  # type: List[_Status]
        self._have_status_tasks = Condition()
        self._render_request_thread = Thread(target=self._run_render_requests)
        self._render_request_thread.daemon = True
        self._render_status_thread = Thread(target=self._run_render_status_requests)
        self._render_status_thread.daemon = True
        self._render_request_thread.start()
        self._render_status_thread.start()

    def maybe_set_server_connector(self, server_connector):
        # type: (ServerConnector) -> None
        if not self._server_connector:
            self._server_connector = server_connector

    def render(self, render_request, on_success, on_error):
        # type: (RenderRequest, Callable, Callable) -> None
        with self._have_render_tasks:
            self._render_tasks.append(_Render(render_request, on_success, on_error))
            self._have_render_tasks.notify()

    def shutdown(self):
        self._shutdown = True
        with self._have_render_tasks:
            self._have_render_tasks.notify()
        with self._have_status_tasks:
            self._have_status_tasks.notify()
        self._render_request_thread.join()
        self._render_status_thread.join()

    def _run_render_requests(self):
        while True:
            try:
                with self._have_render_tasks:
                    while not (self._shutdown or self._render_tasks):
                        self._have_render_tasks.wait()
                    if self._shutdown:
                        break
                    render_tasks, self._render_tasks = self._render_tasks, []
                requests = [r.request for r in render_tasks]
                logger.debug("render call with requests: {}".format(requests))
                try:
                    responses = self._server_connector.render(*requests)
                except Exception as e:
                    for task in render_tasks:
                        task.on_error(e)
                    continue
                statuses = []
                for task, running_render in zip(render_tasks, responses):
                    if running_render.render_status == RenderStatus.RENDERING:
                        statuses.append(
                            _Status(
                                running_render.render_id, task.on_success, task.on_error
                            )
                        )
                    else:
                        task.on_error(
                            EyesError("Unexpected render response", running_render)
                        )
                with self._have_status_tasks:
                    self._status_tasks.extend(statuses)
                    self._have_status_tasks.notify()
            except Exception:
                logger.exception("Render request batching thread failure")

    def _run_render_status_requests(self):
        status_tasks = []
        while True:
            try:
                with self._have_status_tasks:
                    while not (self._shutdown or status_tasks or self._status_tasks):
                        self._have_status_tasks.wait()
                    if self._shutdown:
                        break
                    new_tasks, self._status_tasks = self._status_tasks, []
                status_tasks.extend(new_tasks)
                status_tasks = self._check_render_status_batch(status_tasks)
                if status_tasks:
                    datetime_utils.sleep(1000, "Render status polling delay")
            except Exception:
                logger.exception("Rendering status batching thread failure")

    def _check_render_status_batch(self, status_tasks):
        ids = [t.render_id for t in status_tasks]
        logger.debug("render_status_by_id call with ids: {}".format(ids))
        try:
            statuses = self._server_connector.render_status_by_id(*ids)
        except Exception as e:
            for task in status_tasks:
                task.on_error(e)
            return []
        rendering = []
        logger.debug("Received render status response", statuses_count=len(statuses))
        status_by_render_id = {s.render_id: s for s in statuses}
        current_time = time()
        for task in status_tasks:
            status = status_by_render_id.get(task.render_id)
            if status is None:
                logger.warning(
                    "Missing render id in RenderStatus response",
                    render_id=task.render_id,
                )
            if status is None or status.status == RenderStatus.RENDERING:
                if current_time > task.timeout_time:
                    task.on_error(EyesError("Render time out"))
                else:
                    rendering.append(task)
            else:
                task.on_success(status)
        return rendering


@attr.s
class _Render(object):
    request = attr.ib()  # type: RenderRequest
    on_success = attr.ib()  # type: Callable[[RenderStatusResults], None]
    on_error = attr.ib()  # type: Callable[[Exception], None]


@attr.s
class _Status(object):
    render_id = attr.ib()  # type: Text
    on_success = attr.ib()  # type: Callable[[RenderStatusResults], None]
    on_error = attr.ib()  # type: Callable[[Exception], None]
    timeout_time = attr.ib(
        factory=lambda: time() + MAX_STATUS_CHECK_SECONDS
    )  # type: int
