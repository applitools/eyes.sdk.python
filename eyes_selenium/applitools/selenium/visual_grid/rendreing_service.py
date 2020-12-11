from threading import Condition, Thread

from applitools.common import EyesError, RenderStatus, logger
from applitools.common.utils import datetime_utils

MAX_FAILS_COUNT = 5
MAX_ITERATIONS = 2400  # poll_render_status for 1 hour


class RenderingService(object):
    def __init__(self):
        self._server_connector = None
        self._shutdown = False
        self._render_tasks = []
        self._have_render_tasks = Condition()
        self._status_tasks = []
        self._have_status_tasks = Condition()
        self._render_request_thread = Thread(target=self._run_render_requests)
        self._render_status_thread = Thread(target=self._run_render_status_requests)
        self._render_request_thread.start()
        self._render_status_thread.start()

    def render(self, render_task):
        if self._server_connector is None:
            self._server_connector = render_task.server_connector
        with self._have_render_tasks:
            self._render_tasks.append(render_task)
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
            with self._have_render_tasks:
                while not (self._shutdown or self._render_tasks):
                    self._have_render_tasks.wait()
                if self._shutdown:
                    break
                render_tasks, self._render_tasks = self._render_tasks, []
            render_requests = sum((t.render_requests for t in render_tasks), [])
            _send_render_requests(self._server_connector, render_requests)
            with self._have_status_tasks:
                self._status_tasks.extend(render_tasks)
                self._have_status_tasks.notify()

    def _run_render_status_requests(self):
        status_tasks = []
        while True:
            with self._have_status_tasks:
                while not (self._shutdown or status_tasks or self._status_tasks):
                    self._have_status_tasks.wait()
                if self._shutdown:
                    break
                new_tasks, self._status_tasks = self._status_tasks, []
            status_tasks.extend(new_tasks)
            render_requests = sum((t.render_requests for t in status_tasks), [])
            statuses = _poll_render_status(self._server_connector, render_requests)
            rendering = []
            for status, task in zip(statuses, status_tasks):
                if status.status == RenderStatus.RENDERING:
                    rendering.append(task)
                else:
                    task.on_success(status)
            status_tasks = rendering
            if status_tasks:
                datetime_utils.sleep(1000, "Render status polling delay")


def _send_render_requests(server_connector, requests):
    fetch_fails = 0
    render_requests = None
    while True:
        try:
            render_requests = server_connector.render(*requests)
        except Exception:
            logger.exception("During rendering for requests {}".format(requests))
            fetch_fails += 1
            datetime_utils.sleep(
                1500, msg="/render throws exception... sleeping for 1.5s"
            )
        if fetch_fails > MAX_FAILS_COUNT:
            raise EyesError(
                "Render is failed. Max count retries reached for {}".format(requests)
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
        still_running = fetch_fails > MAX_FAILS_COUNT
        if not still_running:
            break


def _poll_render_status(server_connector, requests):
    logger.debug("poll_render_status call with Requests {}".format(requests))
    statuses = []
    fails_count = 0
    while True:
        try:
            return server_connector.render_status_by_id(
                *[rq.render_id for rq in requests]
            )
        except Exception as e:
            logger.exception(e)
            datetime_utils.sleep(
                1000, msg="/render-status throws exception... sleeping for 1s"
            )
            fails_count += 1
            if fails_count > MAX_FAILS_COUNT:
                raise EyesError(
                    "Max fails count in poll_render_status has been reached "
                    "for render_id: \n {}".format(
                        "\n".join(s.render_id for s in statuses)
                    )
                )
