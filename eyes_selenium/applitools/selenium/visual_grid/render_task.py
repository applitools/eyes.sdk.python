import typing
from itertools import chain
from threading import Lock, RLock

import attr

from applitools.common import (
    EyesError,
    RenderInfo,
    RenderRequest,
    RenderStatus,
    RGridDom,
    VGResource,
    VisualGridSelector,
    logger,
)
from applitools.common.utils import datetime_utils, urljoin, urlparse
from applitools.selenium import css_parser

from .vg_task import VGTask

if typing.TYPE_CHECKING:
    from typing import Callable, Dict, Any, Text, List, Optional
    from applitools.common import RenderStatusResults, Region
    from applitools.selenium.visual_grid import RunningTest, EyesConnector


@attr.s(hash=True)
class RenderTask(VGTask):
    MAX_FAILS_COUNT = 5
    MAX_ITERATIONS = 100

    script = attr.ib(hash=False, repr=False)  # type: Dict[str, Any]
    running_test = attr.ib()  # type: RunningTest
    resource_cache = attr.ib(hash=False, repr=False)
    put_cache = attr.ib(hash=False, repr=False)
    eyes_connector = attr.ib(hash=False, repr=False)  # type: EyesConnector
    rendering_info = attr.ib()
    region_selectors = attr.ib(
        hash=False, factory=list
    )  # type: List[List[VisualGridSelector]]
    size_mode = attr.ib(default=None)
    region_to_check = attr.ib(hash=False, default=None)  # type: Region
    script_hooks = attr.ib(hash=False, default=None)  # type: Optional[Dict]
    agent_id = attr.ib(default=None)  # type: Optional[Text]
    selector = attr.ib(hash=False, default=None)  # type: Optional[VisualGridSelector]
    func_to_run = attr.ib(default=None, hash=False, repr=False)  # type: Callable
    render_status = attr.ib(
        init=False, default=None, hash=False, repr=False
    )  # type:Optional[RenderStatusResults]

    def __attrs_post_init__(self):
        # type: () -> None
        self.func_to_run = self.perform  # type: Callable
        self.all_blobs = []  # type: List[VGResource]
        self.request_resources = {}  # type: Dict[Text, VGResource]
        self.resource_urls = []  # type: List[Text]
        self.discovered_resources_lock = RLock()

    def perform(self):
        # type: () -> RenderStatusResults

        def get_and_put_resource(url):
            # type: (str) -> VGResource
            resource = self.request_resources.get(url)
            self.eyes_connector.render_put_resource(running_render, resource)
            return resource

        requests = []
        rq = self.prepare_data_for_rg(self.script)
        requests.append(rq)
        fetch_fails = 0
        render_requests = None
        while True:

            try:
                render_requests = self.eyes_connector.render(*requests)
            except Exception as e:
                logger.exception(e)
                fetch_fails += 1
                datetime_utils.sleep(1500)
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

            if need_more_resources:
                for url in running_render.need_more_resources:
                    self.put_cache.fetch_and_store(url, get_and_put_resource)

            if need_more_dom:
                self.eyes_connector.render_put_resource(running_render, dom_resource)

            if not still_running:
                break

        statuses = self.poll_render_status(rq)
        if statuses and statuses[0].status == RenderStatus.ERROR:
            raise EyesError(
                "Render failed for {} with the message: {}".format(
                    statuses[0].status, statuses[0].error
                )
            )
        return statuses[0]

    def prepare_data_for_rg(self, data):
        # type: (Dict) -> RenderRequest
        self.request_resources = {}
        dom = self.parse_frame_dom_resources(data)
        return self.prepare_rg_requests(self.running_test, dom, self.request_resources)

    def prepare_rg_requests(self, running_test, dom, request_resources):
        # type: (RunningTest, RGridDom, Dict) -> RenderRequest
        if self.size_mode == "region" and self.region_to_check is None:
            raise EyesError("Region to check should be present")
        if self.size_mode == "selector" and not isinstance(
            self.selector, VisualGridSelector
        ):
            raise EyesError("Selector should be present")

        region = None
        if self.region_to_check:
            region = dict(
                x=self.region_to_check.x,
                y=self.region_to_check.y,
                width=self.region_to_check.width,
                height=self.region_to_check.height,
            )
        r_info = RenderInfo(
            width=running_test.browser_info.width,
            height=running_test.browser_info.height,
            size_mode=self.size_mode,
            selector=self.selector,
            region=region,
            emulation_info=running_test.browser_info.emulation_info,
        )
        return RenderRequest(
            webhook=self.rendering_info.results_url,
            agent_id=self.agent_id,
            url=dom.url,
            dom=dom,
            resources=request_resources,
            render_info=r_info,
            browser_name=running_test.browser_info.browser_type,
            platform=running_test.browser_info.platform,
            script_hooks=self.script_hooks,
            selectors_to_find_regions_for=list(chain(*self.region_selectors)),
            send_dom=running_test.configuration.send_dom,
        )

    def parse_frame_dom_resources(self, data):
        # type: (Dict) -> RGridDom
        base_url = data["url"]
        resource_urls = data.get("resourceUrls", [])
        blobs = data.get("blobs", [])
        frames = data.get("frames", [])
        discovered_resources_urls = []

        def handle_resources(content_type, content):
            if content_type == "text/css":
                urls_from_css = css_parser.get_urls_from_css_resource(content)
                for discovered_url in urls_from_css:
                    target_url = _apply_base_url(discovered_url, base_url)
                    with self.discovered_resources_lock:
                        discovered_resources_urls.append(target_url)

        def get_resource(link):
            # type: (Text) -> VGResource
            response = self.eyes_connector.download_resource(link)
            return VGResource.from_response(link, response, on_created=handle_resources)

        for f_data in frames:
            f_data["url"] = _apply_base_url(f_data["url"], base_url)
            self.request_resources[f_data["url"]] = self.parse_frame_dom_resources(
                f_data
            ).resource

        for blob in blobs:
            resource = VGResource.from_blob(blob, on_created=handle_resources)
            if resource.url.rstrip("#") == base_url:
                continue

            self.all_blobs.append(resource)
            self.request_resources[resource.url] = resource

        for r_url in set(resource_urls):
            self.resource_cache.fetch_and_store(r_url, get_resource)
        for r_url in discovered_resources_urls:
            self.resource_cache.fetch_and_store(r_url, get_resource)
        self.request_resources.update(self.resource_cache)
        return RGridDom(
            url=base_url, dom_nodes=data["cdt"], resources=self.request_resources
        )

    def poll_render_status(self, render_request):
        # type: (RenderRequest) -> List[RenderStatusResults]
        iterations = 0
        statuses = []  # type: List[RenderStatusResults]
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
                    datetime_utils.sleep(1000)
                    fails_count += 1
                finally:
                    iterations += 1
                    datetime_utils.sleep(500)
                if statuses or 0 < fails_count < 3:
                    break
            finished = bool(
                statuses
                and statuses[0] is not None
                and (
                    statuses[0].status != RenderStatus.RENDERING
                    or iterations > self.MAX_ITERATIONS
                    or False
                )
            )
        self.render_status = statuses[0]
        if statuses[0].status == RenderStatus.ERROR:
            raise EyesError(
                "Got error during rendering: \n\t{}".format(statuses[0].error)
            )
        return statuses


def _apply_base_url(discovered_url, base_url):
    url = urlparse(discovered_url)
    if url.scheme in ["http", "https"] and url.netloc:
        return discovered_url
    return urljoin(base_url, discovered_url)
