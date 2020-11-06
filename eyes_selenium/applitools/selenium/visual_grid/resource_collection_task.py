import typing
from collections import deque
from itertools import chain

import attr

from applitools.common import (
    EyesError,
    RenderInfo,
    RenderRequest,
    RGridDom,
    VGResource,
    VisualGridSelector,
    logger,
)
from applitools.common.utils import apply_base_url, iteritems
from applitools.common.utils.converters import str2bool
from applitools.common.utils.general_utils import get_env_with_prefix
from applitools.selenium.parsers import collect_urls_from_

from .vg_task import VGTask

if typing.TYPE_CHECKING:
    from typing import (
        Any,
        Callable,
        Dict,
        Iterable,
        List,
        NoReturn,
        Optional,
        Text,
        Tuple,
    )

    from applitools.common import Region, RenderingInfo
    from applitools.core import ServerConnector
    from applitools.selenium.visual_grid import (
        EyesConnector,
        ResourceCache,
        RunningTest,
    )


@attr.s(hash=True)
class ResourceCollectionTask(VGTask):
    MAX_FAILS_COUNT = 5
    MAX_ITERATIONS = 2400  # poll_render_status for 1 hour

    script = attr.ib(hash=False, repr=False)  # type: Dict[str, Any]
    resource_cache = attr.ib(hash=False, repr=False)  # type: ResourceCache
    put_cache = attr.ib(hash=False, repr=False)
    server_connector = attr.ib(hash=False, repr=False)  # type: ServerConnector
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
    running_tests = attr.ib(hash=False, factory=list)  # type: List[RunningTest]
    request_options = attr.ib(hash=False, factory=dict)  # type: Dict[str, Any]
    is_force_put_needed = attr.ib(
        default=str2bool(get_env_with_prefix("APPLITOOLS_UFG_FORCE_PUT_RESOURCES"))
    )  # type: bool

    def __attrs_post_init__(self):
        # type: () -> None
        self.full_request_resources = {}  # type: Dict[Text, VGResource]
        self.func_to_run = lambda: self.prepare_data_for_rg(
            self.script
        )  # type: Callable

    def prepare_data_for_rg(self, data):
        # type: (Dict) -> List[RenderRequest]
        dom = self.parse_frame_dom_resources(data)
        render_requests = self.prepare_rg_requests(dom, self.full_request_resources)
        logger.debug(
            "exit - returning render_request array of length: {}".format(
                len(render_requests)
            )
        )
        render_request = list(render_requests.values())[0]
        logger.debug("Uploading missing resources")
        self.check_resources_status_and_upload(
            render_request.dom, render_request.resources
        )
        return render_requests

    def check_resources_status_and_upload(self, dom, resource_map):
        cached_request_resources = self.full_request_resources.copy()

        def get_and_put_resource(url):
            # type: (str) -> VGResource
            logger.debug("get_and_put_resource({}) call".format(url))
            resource = cached_request_resources.get(url)
            self.server_connector.render_put_resource("NONE", resource)
            return resource

        hash_to_resource_url = {}
        for url, resource in iteritems(resource_map):
            if url in self.put_cache:
                continue
            hash_to_resource_url[resource.hash] = url

        if dom.url not in self.put_cache:
            hash_to_resource_url[dom.resource.hash] = dom.url
            cached_request_resources[dom.url] = dom.resource

        resources_hashes = []
        for resource_url in hash_to_resource_url.values():
            resource = cached_request_resources[resource_url]
            if resource.error_status_code:
                continue
            resources_hashes.append(
                {"hashFormat": resource.hash_format, "hash": resource.hash}
            )
        result = self.server_connector.check_resource_status(None, *resources_hashes)

        for hash_obj, exists in zip(resources_hashes, result):
            if exists or not self.is_force_put_needed:
                continue
            hash_ = hash_obj["hash"]
            resource_url = hash_to_resource_url[hash_]
            self.put_cache.fetch_and_store(resource_url, get_and_put_resource)
        self.put_cache.process_all()

    def prepare_rg_requests(self, dom, request_resources):
        # type: (RGridDom, Dict) -> Dict[RunningTest,RenderRequest]
        if self.size_mode == "region" and self.region_to_check is None:
            raise EyesError("Region to check should be present")
        if self.size_mode == "selector" and not isinstance(
            self.selector, VisualGridSelector
        ):
            raise EyesError("Selector should be present")
        requests = {}
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

            requests[running_test] = RenderRequest(
                webhook=self.rendering_info.results_url,
                agent_id=self.agent_id,
                url=dom.url,
                stitching_service=self.rendering_info.stitching_service_url,
                dom=dom,
                resources=request_resources,
                render_info=r_info,
                renderer=running_test.eyes.renderer,
                browser_name=running_test.browser_info.browser,
                platform_name=running_test.browser_info.platform,
                script_hooks=self.script_hooks,
                selectors_to_find_regions_for=list(chain(*self.region_selectors)),
                send_dom=running_test.configuration.send_dom,
                options=self.request_options,
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
            self.server_connector,
            self.resource_cache,
            find_child_resource_urls,
        )
        frame_request_resources.update(resources_and_their_children)
        self.full_request_resources.update(frame_request_resources)
        return RGridDom(
            url=base_url, dom_nodes=data["cdt"], resources=frame_request_resources
        )


def fetch_resources_recursively(
    urls,  # type: Iterable[Text]
    eyes_connector,  # type: ServerConnector
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
