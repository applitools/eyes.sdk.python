import typing
from collections import Iterable, deque
from functools import partial
from itertools import chain

import attr

from applitools.common import (
    EyesError,
    RenderInfo,
    RenderRequest,
    RenderStatus,
    RGridDom,
    RunningRender,
    VGResource,
    VisualGridSelector,
    logger,
)
from applitools.common.utils import apply_base_url, datetime_utils
from applitools.common.utils.converters import str2bool
from applitools.common.utils.general_utils import get_env_with_prefix
from applitools.selenium.parsers import collect_urls_from_

from .vg_task import VGTask

if typing.TYPE_CHECKING:
    from typing import Any, Callable, Dict, List, NoReturn, Optional, Text, Tuple

    from applitools.common import Region, RenderingInfo, RenderStatusResults
    from applitools.selenium.visual_grid import (
        EyesConnector,
        ResourceCache,
        RunningTest,
    )


@attr.s(hash=True)
class RenderTask(VGTask):
    MAX_FAILS_COUNT = 5
    MAX_ITERATIONS = 2400  # poll_render_status for 1 hour

    script = attr.ib(hash=False, repr=False)  # type: Dict[str, Any]
    resource_cache = attr.ib(hash=False, repr=False)  # type: ResourceCache
    put_cache = attr.ib(hash=False, repr=False)
    eyes_connector = attr.ib(hash=False, repr=False)  # type: EyesConnector
    rendering_info = attr.ib()  # type: RenderingInfo
    region_selectors = attr.ib(
        hash=False, factory=list
    )  # type: List[List[VisualGridSelector]]
    size_mode = attr.ib(default=None)
    region_to_check = attr.ib(hash=False, default=None)  # type: Region
    script_hooks = attr.ib(hash=False, default=None)  # type: Optional[Dict]
    agent_id = attr.ib(default=None)  # type: Optional[Text]
    selector = attr.ib(hash=False, default=None)  # type: Optional[VisualGridSelector]
    func_to_run = attr.ib(default=None, hash=False, repr=False)  # type: Callable
    running_tests = attr.ib(
        init=False, hash=False, factory=list
    )  # type: List[RunningTest]
    is_force_put_needed = attr.ib(
        default=str2bool(get_env_with_prefix("APPLITOOLS_UFG_FORCE_PUT_RESOURCES"))
    )  # type: bool
    request_options = attr.ib(hash=False, factory=dict)  # type: Dict[str, Any]

    def __attrs_post_init__(self):
        # type: () -> None
        self.func_to_run = self.perform  # type: Callable
        self.full_request_resources = {}  # type: Dict[Text, VGResource]

    def perform(self):  # noqa
        # type: () -> List[RenderStatusResults]

        def get_and_put_resource(url, running_render):
            # type: (str, RunningRender) -> VGResource
            logger.debug(
                "get_and_put_resource({0}, render_id={1}) call".format(
                    url, running_render.render_id
                )
            )
            resource = self.full_request_resources.get(url)
            self.eyes_connector.render_put_resource(running_render.render_id, resource)
            return resource

        requests = self.prepare_data_for_rg(self.script)
        fetch_fails = 0
        render_requests = None
        already_force_putted = False
        while True:
            try:
                self.put_cache.process_all()
                render_requests = self.eyes_connector.render(*requests)
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
            need_more_dom = need_more_resources = False
            for i, running_render in enumerate(render_requests):
                requests[i].render_id = running_render.render_id
                need_more_dom = running_render.need_more_dom
                need_more_resources = (
                    running_render.render_status == RenderStatus.NEED_MORE_RESOURCE
                )
                get_and_put_resource_wtih_render = partial(
                    get_and_put_resource, running_render=running_render
                )
                dom_resource = requests[i].dom.resource

                if self.is_force_put_needed and not already_force_putted:
                    for url in self.full_request_resources:
                        self.put_cache.fetch_and_store(
                            url, get_and_put_resource_wtih_render, force=True
                        )
                    already_force_putted = True

                if need_more_resources:
                    for url in running_render.need_more_resources:
                        self.put_cache.fetch_and_store(
                            url, get_and_put_resource_wtih_render
                        )

                if need_more_dom:
                    self.eyes_connector.render_put_resource(
                        running_render.render_id, dom_resource
                    )
            still_running = (
                need_more_resources
                or need_more_dom
                or fetch_fails > self.MAX_FAILS_COUNT
            )
            if not still_running:
                break

        return self.poll_render_status(requests)

    def prepare_data_for_rg(self, data):
        # type: (Dict) -> List[RenderRequest]
        self.full_request_resources = {}
        dom = self.parse_frame_dom_resources(data)
        return self.prepare_rg_requests(dom, self.full_request_resources)

    def prepare_rg_requests(self, dom, request_resources):
        # type: (RGridDom, Dict) -> List[RenderRequest]
        if self.size_mode == "region" and self.region_to_check is None:
            raise EyesError("Region to check should be present")
        if self.size_mode == "selector" and not isinstance(
            self.selector, VisualGridSelector
        ):
            raise EyesError("Selector should be present")

        requests = []
        region = None
        for running_test in self.running_tests:
            if self.region_to_check:
                region = dict(
                    x=self.region_to_check.x,
                    y=self.region_to_check.y,
                    width=self.region_to_check.width,
                    height=self.region_to_check.height,
                )
            r_info = RenderInfo.from_(
                size_mode=self.size_mode,
                selector=self.selector,
                region=region,
                render_browser_info=running_test.browser_info,
            )

            requests.append(
                RenderRequest(
                    webhook=self.rendering_info.results_url,
                    agent_id=self.agent_id,
                    url=dom.url,
                    stitching_service=self.rendering_info.stitching_service_url,
                    dom=dom,
                    resources=request_resources,
                    render_info=r_info,
                    browser_name=running_test.browser_info.browser,
                    platform_name=running_test.browser_info.platform,
                    script_hooks=self.script_hooks,
                    selectors_to_find_regions_for=list(chain(*self.region_selectors)),
                    send_dom=running_test.configuration.send_dom,
                    options=self.request_options,
                )
            )
        return requests

    def parse_frame_dom_resources(self, data):  # noqa
        # type: (Dict) -> RGridDom
        base_url = data["url"]
        resource_urls = data.get("resourceUrls", [])
        all_blobs = data.get("blobs", [])
        frames = data.get("frames", [])
        logger.debug(
            """
        parse_frame_dom_resources() call

        base_url: {base_url}
        count blobs: {blobs_num}
        count resource urls: {resource_urls_num}
        count frames: {frames_num}

        """.format(
                base_url=base_url,
                blobs_num=len(all_blobs),
                resource_urls_num=len(resource_urls),
                frames_num=len(frames),
            )
        )

        def find_child_resource_urls(content_type, content, resource_url):
            # type: (Optional[Text], bytes, Text) -> NoReturn
            logger.debug(
                "find_child_resource_urls({0}, {1}) call".format(
                    content_type, resource_url
                )
            )
            if not content_type:
                logger.debug("content_type is empty. Skip handling of resources")
                return []
            return [
                apply_base_url(url, base_url, resource_url)
                for url in collect_urls_from_(content_type, content)
            ]

        frame_request_resources = {}
        for f_data in frames:
            f_data["url"] = apply_base_url(f_data["url"], base_url)
            frame_request_resources[f_data["url"]] = self.parse_frame_dom_resources(
                f_data
            ).resource

        urls_to_fetch = set(resource_urls)
        for blob in all_blobs:
            resource = VGResource.from_blob(blob, find_child_resource_urls)
            if resource.url.rstrip("#") == base_url:
                continue
            frame_request_resources[resource.url] = resource
            urls_to_fetch |= set(resource.child_resource_urls)

        resources_and_their_children = fetch_resources_recursively(
            urls_to_fetch,
            self.eyes_connector,
            self.resource_cache,
            find_child_resource_urls,
        )
        frame_request_resources.update(resources_and_their_children)
        self.full_request_resources.update(frame_request_resources)
        return RGridDom(
            url=base_url, dom_nodes=data["cdt"], resources=frame_request_resources
        )

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
                    statuses = self.eyes_connector.render_status_by_id(
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


def fetch_resources_recursively(
    urls,  # type: Iterable[Text]
    eyes_connector,  # type: EyesConnector
    resource_cache,  # type: ResourceCache
    find_child_resource_urls,  # type: Callable[[Text, bytes, Text],List[Text]]
):
    # type: (...) -> Iterable[Tuple[Text, VGResource]]
    def get_resource(link):
        logger.debug("get_resource({0}) call".format(link))
        response = eyes_connector.download_resource(link)
        return VGResource.from_response(link, response, find_child_resource_urls)

    def schedule_fetch(urls):
        for url in urls:
            if url not in seen_urls:
                seen_urls.add(url)
                downloading = resource_cache.fetch_and_store(url, get_resource)
                if downloading:  # going to take time, add to the queue end
                    fetched_urls_deque.appendleft(url)
                else:  # resource is already in cache, add to the queue front
                    fetched_urls_deque.append(url)

    fetched_urls_deque = deque()
    seen_urls = set()
    schedule_fetch(urls)
    while fetched_urls_deque:
        url = fetched_urls_deque.pop()
        resource = resource_cache[url]
        if resource is None:
            logger.debug("No response for {}".format(url))
        else:
            schedule_fetch(resource.child_resource_urls)
            yield url, resource
