import json
import time
import typing
import uuid
from concurrent.futures.thread import ThreadPoolExecutor
from threading import RLock

import attr

from applitools.common import EyesError, logger
from applitools.common.utils.general_utils import set_query_parameter
from applitools.common.visual_grid import (
    RenderInfo,
    RenderRequest,
    RenderStatus,
    RGridDom,
    VGResource,
)

from .eyes_connector import EyesConnector

if typing.TYPE_CHECKING:
    from typing import Any, List, Dict
    from applitools.common.visual_grid import RenderStatusResults, RunningRender

if typing.TYPE_CHECKING:
    from typing import Callable, Text

    from .running_test import RunningTest


@attr.s(hash=True)
class VGTask(object):
    name = attr.ib()  # type: Text
    func_to_run = attr.ib(hash=False, repr=False)  # type: Callable
    uuid = attr.ib(init=False, repr=False, factory=lambda: str(uuid.uuid4()))

    callback = None
    error_callback = None
    complete_callback = None

    def on_task_succeeded(self, code):
        # type: (Callable) -> VGTask
        self.callback = code
        return self

    def on_task_error(self, code):
        # type: (Callable) -> VGTask
        self.error_callback = code
        return self

    def on_task_completed(self, code):
        # type: (Callable) -> VGTask
        self.complete_callback = code
        return self

    def __call__(self):
        # type: () -> None
        try:
            res = None
            if callable(self.func_to_run):
                res = self.func_to_run()
            if callable(self.callback):
                self.callback(res)
        except Exception as e:
            logger.error("Failed to execute task!")
            logger.exception(e)
            if callable(self.error_callback):
                self.error_callback(e)
        finally:
            if callable(self.complete_callback):
                self.complete_callback()


@attr.s(hash=True)
class RenderTask(VGTask):
    MAX_FAILS_COUNT = 5
    MAX_ITERATIONS = 100

    script = attr.ib(repr=False)
    running_test = attr.ib()  # type: RunningTest
    resource_cache = attr.ib(hash=False, repr=False)
    put_cache = attr.ib(hash=False, repr=False)
    eyes_connector = attr.ib(hash=False, repr=False)  # type: EyesConnector
    rendering_info = attr.ib()
    dom_url_mod = attr.ib(repr=False)
    func_to_run = attr.ib(default=None, hash=False, repr=False)  # type: Callable

    def __attrs_post_init__(self):
        # type: () -> None
        self.func_to_run = self.perform
        self.all_blobs = []
        self.request_resources = {}
        self.resource_urls = []
        self.result = None

    def perform(self):
        # type: () -> RenderStatusResults
        requests = []
        rq = self.prepare_data_for_rg(self.script_data)
        requests.append(rq)
        fetch_fails = 0
        render_requests = None
        while True:

            try:
                render_requests = self.eyes_connector.render(*requests)
            except Exception as e:
                logger.exception(e)
                fetch_fails += 1
                time.sleep(1.5)
            if not render_requests:
                continue

            running_render = render_requests[0]
            rq.render_id = running_render.render_id
            need_more_dom = running_render.need_more_dom
            need_more_resources = (
                running_render.render_status == RenderStatus.NEED_MORE_RESOURCE
            )
            still_running = (
                need_more_resources
                or need_more_dom
                or fetch_fails > self.MAX_FAILS_COUNT
            )

            dom_resource = rq.dom.resource

            cache_key = dom_resource.url
            if self.dom_url_mod:
                cache_key = set_query_parameter(cache_key, "modifier", self.dom_url_mod)

            if need_more_resources:
                self._process_resources(running_render)

            if need_more_dom:
                self.eyes_connector.render_put_resource(running_render, dom_resource)

            if not still_running:
                break

        statuses = self.poll_render_status(rq)
        if statuses and statuses[0].status == "error":
            raise EyesError(
                "Render failed for {} with the message: {}".format(
                    statuses[0].status, statuses[0].error
                )
            )
        self.result = statuses[0]
        return self.result

    def _process_resources(self, running_render):
        # type: (RunningRender) -> None
        lock = RLock()

        def get_resource(url):
            # type: (str) -> VGResource
            with lock:
                cached_resource = self.request_resources.get(url)
            if not cached_resource:
                response = self.eyes_connector.download_resource(url)
                cached_resource = VGResource.from_response(url, response)
                with lock:
                    self.request_resources[url] = cached_resource
            self.eyes_connector.render_put_resource(running_render, cached_resource)
            return cached_resource

        with ThreadPoolExecutor() as executor:
            futures = executor.map(get_resource, running_render.need_more_resources)
            for i, resource in enumerate(futures):
                logger.debug("Got {} - {}".format(i, resource))

    @property
    def script_data(self):
        # type: () -> Dict[str, Any]
        return json.loads(self.script)

    def prepare_data_for_rg(self, data):
        # type: (dict) -> RenderRequest
        resource_urls = data.get("resourceUrls", [])
        blobs = data.get("blobs", [])

        for blob in blobs:
            resource = VGResource.from_blob(blob)
            self.all_blobs.append(resource)
            self.request_resources[resource.url] = resource

        def get_resource(link):
            # type: (str) -> VGResource
            response = self.eyes_connector.download_resource(link)
            return VGResource.from_response(link, response)

        with ThreadPoolExecutor() as executor:
            futures = executor.map(get_resource, resource_urls)
            for i, resource in enumerate(futures):
                self.resource_cache[resource.url] = resource
                logger.debug("Got {} - {}".format(i, resource))

        self.request_resources.update(self.resource_cache)

        # TODO: Add proper RenderInfo params
        r_info = RenderInfo(
            width=self.running_test.browser_info.width,
            height=self.running_test.browser_info.height,
            size_mode=self.running_test.browser_info.size_mode,
            emulation_info=self.running_test.browser_info.emulation_info,
        )
        url = self.script_data["url"]
        dom = RGridDom(
            url=url, dom_nodes=self.script_data["cdt"], resources=self.request_resources
        )
        return RenderRequest(
            webhook=self.rendering_info.results_url,
            url=url,
            dom=dom,
            resources=self.request_resources,
            render_info=r_info,
            browser_name=self.running_test.browser_info.browser_type,
            platform=self.running_test.browser_info.platform,
            script_hooks={},
            selectors_to_find_regions_for=[],
            send_dom=self.running_test.configuration.send_dom,
            task=None,
        )

    def poll_render_status(self, render_request):
        # type: (RenderRequest) -> List[RenderStatusResults]
        iterations = 0
        statuses = []
        if not render_request.render_id:
            raise EyesError("RenderStatus: Got empty renderId!")
        fails_count = 0
        finished = False
        while True:
            if finished:
                break
            while True:
                try:
                    statuses = self.eyes_connector.render_status_by_id(
                        render_request.render_id
                    )
                except Exception as e:
                    logger.exception(e)
                    time.sleep(1)
                    fails_count += 1
                finally:
                    iterations += 1
                    time.sleep(0.5)
                if statuses or 0 < fails_count < 3:
                    break
            finished = statuses and (
                statuses[0].status == "error"
                or statuses[0].status == "rendered"
                or iterations > self.MAX_ITERATIONS
                or False
            )
        return statuses
