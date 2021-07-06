import itertools
import typing
import uuid
from bisect import bisect_right
from copy import deepcopy

import attr

from applitools.common import EyesError, RectangleSize, TestResults, deprecated
from applitools.common.ultrafastgrid import (
    DesktopBrowserInfo,
    JobInfo,
    RenderBrowserInfo,
    RenderInfo,
    RenderRequest,
    VisualGridSelector,
    device_sizes_db,
)
from applitools.common.utils import argument_guard
from applitools.common.utils.compat import raise_from
from applitools.common.utils.datetime_utils import sleep
from applitools.common.utils.general_utils import random_alphanum
from applitools.core import CheckSettings, GetRegion, ServerConnector
from applitools.selenium import eyes_selenium_utils
from applitools.selenium.__version__ import __version__
from applitools.selenium.fluent import SeleniumCheckSettings
from applitools.selenium.visual_grid import dom_snapshot_script

from .eyes_connector import EyesConnector
from .helpers import collect_test_results, wait_till_tests_completed
from .resource_collection_task import ResourceCollectionTask
from .running_test import TESTED, RunningTest
from .visual_grid_runner import VisualGridRunner

if typing.TYPE_CHECKING:
    from typing import Dict, Generator, List, Optional, Text, Union

    from applitools.common.utils.custom_types import AnyWebElement
    from applitools.selenium import Configuration, Eyes, EyesWebDriver

    from .running_test import RunningTestCheck

GET_ELEMENT_XPATH_JS = """
var el = arguments[0];
var xpath = '';
do {
var parent = el.parentElement;
var index = 1;
if (parent !== null) {
var children = parent.children;
for (var childIdx in children) {
var child = children[childIdx];
if (child === el) break;
if (child.tagName === el.tagName) index++;
}
}
xpath = '/' + el.tagName + '[' + index + ']' + xpath;
el = parent;
} while (el !== null);
return '/' + xpath;"""

DOM_EXTRACTION_TIMEOUT = 10 * 60 * 1000
VIEWPORT_RESIZE_DELAY = 300


@attr.s
class WebElementRegion(object):
    region_provider = attr.ib()  # type: Union[Text, GetRegion]
    _webelement = attr.ib()  # type: AnyWebElement

    @property
    def webelement(self):
        return eyes_selenium_utils.get_underlying_webelement(self._webelement)


class VisualGridEyes(object):
    vg_manager = None  # type: VisualGridRunner
    _config_provider = None
    _is_opened = False
    _driver = None
    rendering_info = None
    is_check_timer_timeout = False

    def __init__(self, config_provider, runner):
        # type: (Eyes, VisualGridRunner)-> None
        self._config_provider = config_provider
        self._elements = []
        argument_guard.not_none(runner)
        self.vg_manager = runner  # type: VisualGridRunner
        self.test_list = []  # type: List[RunningTest]
        self._test_uuid = None
        self.server_connector = ServerConnector()  # type: ServerConnector
        self.resource_collection_queue = []  # type: List[ResourceCollectionTask]
        self.logger = runner.logger.bind(eyes_id=id(self))

    @property
    def is_open(self):
        return self._is_opened

    @property
    def driver(self):
        return self._driver

    @property
    def configure(self):
        # type: () -> Configuration
        return self._config_provider.configure

    @property
    def base_agent_id(self):
        # type: () -> Text
        """
        Must return version of SDK. (e.g. selenium, visualgrid) in next format:
            "eyes.{package}.python/{lib_version}"
        """
        return "eyes.selenium.visualgrid.python/{version}".format(version=__version__)

    @property
    def full_agent_id(self):
        # type: () -> Text
        """
        Gets the agent id, which identifies the current library using the SDK.

        """
        agent_id = self.configure.agent_id
        if agent_id is None:
            return self.base_agent_id
        return "{} [{}]".format(agent_id, self.base_agent_id)

    def _job_info_for_browser_info(self, browser_infos):
        # type: (List[RenderBrowserInfo]) -> Generator[RenderBrowserInfo, JobInfo]
        render_requests = [
            RenderRequest(
                render_info=RenderInfo.from_(
                    size_mode=None,
                    region=None,
                    selector=None,
                    render_browser_info=b_info,
                ),
                platform_name=b_info.platform,
                browser_name=b_info.browser,
            )
            for b_info in browser_infos
        ]

        job_infos = self.server_connector.job_info(render_requests)
        for b_info, job_info in zip(browser_infos, job_infos):
            yield b_info, job_info

    def open(self, driver):
        # type: (EyesWebDriver) -> EyesWebDriver
        self._test_uuid = uuid.uuid4()
        argument_guard.not_none(driver)
        self.logger.debug("VisualGridEyes.open()", config=self.configure)

        self._driver = driver
        self._set_viewport_size()
        self.server_connector.update_config(
            self.configure,
            self.full_agent_id,
            ua_string=self.driver.user_agent.origin_ua_string,
        )
        self.server_connector.render_info()
        self.vg_manager.rendering_service.maybe_set_server_connector(
            self.server_connector
        )
        device_sizes_db.maybe_set_server_connector(self.server_connector)

        for browser_info, job_info in self._job_info_for_browser_info(
            self.configure.browsers_info
        ):
            test = RunningTest(
                self._create_vgeyes_connector(browser_info, job_info),
                self.configure.clone(),
                browser_info,
                self.vg_manager.rendering_service,
                self.logger,
            )
            test.on_results_received(self.vg_manager.aggregate_result)
            test.test_uuid = self._test_uuid
            self.test_list.append(test)
            test.becomes_not_opened()
        self._is_opened = True
        self.vg_manager.open(self)
        self.logger.info("VisualGridEyes opening", tests_count=len(self.test_list))
        return driver

    def get_script_result(self, dont_fetch_resources):
        # type: (bool) -> Dict
        self.logger.debug(
            "get_script_result call", dont_fetch_resources=dont_fetch_resources
        )
        try:
            return dom_snapshot_script.create_dom_snapshot(
                self.driver,
                self.logger,
                dont_fetch_resources,
                None,
                DOM_EXTRACTION_TIMEOUT,
                self.configure.enable_cross_origin_rendering,
                not self.configure.dont_use_cookies,
            )
        except dom_snapshot_script.DomSnapshotFailure as e:
            raise_from(EyesError("Failed to capture dom snapshot"), e)

    @staticmethod
    def _options_dict(configuration_options, check_settings_options):
        return {
            o.key: o.value
            for o in itertools.chain(
                configuration_options or (), check_settings_options or ()
            )
        }

    def check(self, check_settings):
        # type: (SeleniumCheckSettings) -> None
        argument_guard.is_a(check_settings, CheckSettings)
        name = check_settings.values.name
        self.logger.debug(
            "VisualGridEyes.check", name=name, check_settings=check_settings
        )
        self._try_set_target_selector(check_settings)

        self.configure.send_dom = check_settings.values.send_dom

        check_settings = self._update_check_settings(check_settings)
        self.logger.info("check begin", name=name)

        region_xpaths = self.get_region_xpaths(check_settings)
        self.logger.info("check region xpaths", region_xpaths=region_xpaths)
        breakpoints = self._effective_layout_breakpoints(self.configure, check_settings)
        dont_fetch_resources = self._effective_disable_browser_fetching(
            self.configure, check_settings
        )
        running_tests = [
            test for test in self.test_list if self._test_uuid == test.test_uuid
        ]
        for width, tests in _group_tests_by_width(running_tests, breakpoints).items():
            try:
                self._capture_dom_and_schedule_resource_collection_and_checks(
                    width, check_settings, dont_fetch_resources, region_xpaths, tests
                )
            except Exception:
                self.logger.exception("Check failure")
                for test in tests:
                    if test.state != TESTED:
                        # already aborted or closed
                        test.abort()
                        test.becomes_tested()
            self.logger.info("added check tasks", check_settings=check_settings)
        self._set_viewport_size()

    def _capture_dom_and_schedule_resource_collection_and_checks(
        self, width, check_settings, dont_fetch_resources, region_xpaths, running_tests
    ):
        if width:
            try:
                requested = RectangleSize(width, self.configure.viewport_size.height)
                with self.driver.switch_to.frames_and_back([]):
                    eyes_selenium_utils.set_viewport_size(self.driver, requested)
                sleep(VIEWPORT_RESIZE_DELAY, "Waiting after viewport resize")
            except EyesError:
                actual = eyes_selenium_utils.get_viewport_size(self.driver)
                self.logger.warning(
                    "Failed to resize browser window. "
                    "Running browser in headless mode might prevent this error.",
                    requested=requested,
                    actual=actual,
                )
        script_result = self.get_script_result(dont_fetch_resources)
        self.logger.debug(
            "Got script result",
            width=width,
            cdt_len=len(script_result["cdt"]),
            blob_urls=[b["url"] for b in script_result["blobs"]],
            resource_urls=script_result["resourceUrls"],
        )
        source = eyes_selenium_utils.get_check_source(self.driver)
        checks = [
            test.check(
                check_settings=check_settings,
                region_selectors=region_xpaths,
                source=source,
            )
            for test in running_tests
        ]
        resource_collection_task = self._resource_collection_task(
            check_settings, region_xpaths, running_tests, script_result, checks
        )
        self.vg_manager.add_resource_collection_task(resource_collection_task)

    def _resource_collection_task(
        self,
        check_settings,  # type: SeleniumCheckSettings
        region_xpaths,  # type: List[List[VisualGridSelector]]
        running_tests,  # type: List[RunningTest]
        script_result,  # type: Dict
        checks,  # type: List[RunningTestCheck]
    ):
        # type: (...) -> ResourceCollectionTask
        tag = check_settings.values.name
        short_description = "{} of {}".format(
            self.configure.test_name, self.configure.app_name
        )
        resource_collection_task = ResourceCollectionTask(
            name="VisualGridEyes.check-resource_collection {} - {}".format(
                short_description, tag
            ),
            logger=self.logger,
            script=script_result,
            resource_cache=self.vg_manager.resource_cache,
            put_cache=self.vg_manager.put_cache,
            rendering_info=self.server_connector.render_info(),
            server_connector=self.server_connector,
            region_selectors=region_xpaths,
            size_mode=check_settings.values.size_mode,
            region_to_check=check_settings.values.target_region,
            script_hooks=check_settings.values.script_hooks,
            agent_id=self.base_agent_id,
            selector=check_settings.values.selector,
            running_tests=running_tests,
            request_options=self._options_dict(
                self.configure.visual_grid_options,
                check_settings.values.visual_grid_options,
            ),
        )

        def on_collected_task_succeeded(render_requests):
            for check in checks:
                check.set_render_request(render_requests[check.running_test])

        def on_collected_task_error(e):
            # TODO: Improve exception handling
            running_tests[0].pending_exceptions.append(e)
            for test in running_tests:
                if test.state != TESTED:
                    # already aborted or closed
                    test.abort()
                    test.becomes_tested()

        resource_collection_task.on_task_succeeded(on_collected_task_succeeded)
        resource_collection_task.on_task_error(on_collected_task_error)
        return resource_collection_task

    def close_async(self):
        for test in self.test_list:
            test.close()

    def close(self, raise_ex=True):  # noqa
        # type: (Optional[bool]) -> Optional[TestResults]
        if not self.test_list:
            return TestResults(status="Failed")
        self.logger.debug("VisualGridEyes.close()", test_list=self.test_list)
        self.close_async()

        wait_till_tests_completed(self.test_list)

        self._is_opened = False

        all_results = collect_test_results(
            {t: t.test_result for t in self.test_list}, raise_ex
        )
        if not all_results:
            return TestResults(status="Failed")
        return all_results[0].test_results

    def abort_async(self):
        """
        If a test is running, aborts it. Otherwise, does nothing.
        """
        for test in self.test_list:
            test.abort_if_not_closed()

    def abort(self):
        """
        If a test is running, aborts it. Otherwise, does nothing.
        """
        self._is_opened = False
        self.abort_async()

    @deprecated.attribute("use `abort()` instead")
    def abort_if_not_closed(self):
        self.abort()

    def _update_check_settings(self, check_settings):
        # type: (SeleniumCheckSettings) -> SeleniumCheckSettings
        match_level = check_settings.values.match_level
        fully = check_settings.values.stitch_content
        send_dom = check_settings.values.send_dom
        ignore_displacements = check_settings.values.ignore_displacements

        if match_level is None:
            check_settings = check_settings.match_level(self.configure.match_level)
        if fully is None:
            fps = self.configure.force_full_page_screenshot
            check_settings = check_settings.fully(
                check_settings.is_check_window if fps is None else fps
            )
        if send_dom is None:
            send = self.configure.send_dom
            check_settings = check_settings.send_dom(True if send is None else send)
        if ignore_displacements is None:
            check_settings = check_settings.ignore_displacements(
                self.configure.ignore_displacements
            )
        return check_settings

    def _create_vgeyes_connector(self, b_info, job_info):
        # type: (RenderBrowserInfo, JobInfo) -> EyesConnector
        agent_run_id = "{}_{}".format(self.configure.test_name, random_alphanum(10))
        return EyesConnector(
            b_info,
            self.configure.clone(),
            deepcopy(self.server_connector),
            agent_run_id,
            job_info,
        )

    def _try_set_target_selector(self, check_settings):
        # type: (SeleniumCheckSettings) -> None
        element = check_settings.values.target_element
        if element is None:
            target_selector = check_settings.values.target_selector
            if target_selector:
                by, value = target_selector
                element = self.driver.find_element(by, value)

        if element is None:
            return None
        element = eyes_selenium_utils.get_underlying_webelement(element)
        xpath = self.driver.execute_script(GET_ELEMENT_XPATH_JS, element)
        vgs = VisualGridSelector(xpath, "target")
        check_settings.values.selector = vgs

    def get_region_xpaths(self, check_settings):
        # type: (SeleniumCheckSettings) -> List[List[VisualGridSelector]]
        element_lists = self.collect_selenium_regions(check_settings)
        frame_chain = self.driver.frame_chain.clone()
        result = []
        for element_list in element_lists:
            xpaths = []
            for elem_region in element_list:
                if elem_region.webelement is None:
                    continue
                xpath = self.driver.execute_script(
                    GET_ELEMENT_XPATH_JS, elem_region.webelement
                )
                xpaths.append(VisualGridSelector(xpath, elem_region.region_provider))
            result.append(xpaths)
        self.driver.switch_to.frames(frame_chain)
        return result

    def collect_selenium_regions(self, check_settings):
        # type: (SeleniumCheckSettings) -> List[List[WebElementRegion]]
        ignore_elements = self.get_elements_from_regions(
            check_settings.values.ignore_regions
        )
        layout_elements = self.get_elements_from_regions(
            check_settings.values.layout_regions
        )
        strict_elements = self.get_elements_from_regions(
            check_settings.values.strict_regions
        )
        content_elements = self.get_elements_from_regions(
            check_settings.values.content_regions
        )
        floating_elements = self.get_elements_from_regions(
            check_settings.values.floating_regions
        )
        accessibility_elements = self.get_elements_from_regions(
            check_settings.values.accessibility_regions
        )
        element = check_settings.values.target_element
        if element is None:
            target_selector = check_settings.values.target_selector
            if target_selector:
                by, value = target_selector
                element = self.driver.find_element(by, value)

        targets = [WebElementRegion("target", element)]
        return [
            ignore_elements,
            layout_elements,
            strict_elements,
            content_elements,
            floating_elements,
            accessibility_elements,
            targets,
        ]

    def get_elements_from_regions(self, regions_provider):
        # type:(List[GetRegion])->List[WebElementRegion]
        elements = []
        for rp in regions_provider:
            if not hasattr(rp, "get_elements"):
                continue
            webelements = rp.get_elements(self.driver)
            for elem in webelements:
                elements.append(WebElementRegion(rp, elem))
        return elements

    def _get_viewport_size(self):
        argument_guard.not_none(self.driver)
        return eyes_selenium_utils.get_viewport_size(self.driver)

    def _set_viewport_size(self):
        viewport_size = self.configure.viewport_size

        if viewport_size is None:
            for render_bi in self.configure.browsers_info:
                if isinstance(render_bi, (DesktopBrowserInfo, RenderBrowserInfo)):
                    viewport_size = render_bi.viewport_size
                    break

        if viewport_size is None:
            self.configure.viewport_size = self._get_viewport_size()
            return

        self.configure.viewport_size = viewport_size
        with self.driver.switch_to.frames_and_back([]):
            try:
                eyes_selenium_utils.set_viewport_size(self.driver, viewport_size)
            except Exception as e:
                self.logger.exception("set_viewport_size failure")
                raise_from(EyesError("Failed to set viewport size"), e)

    @staticmethod
    def _effective_disable_browser_fetching(config, check_settings):
        if check_settings.values.disable_browser_fetching is not None:
            return check_settings.values.disable_browser_fetching
        else:
            return config.disable_browser_fetching

    @staticmethod
    def _effective_layout_breakpoints(config, check_settings):
        if check_settings.values.layout_breakpoints is None:
            return config.layout_breakpoints
        else:
            return check_settings.values.layout_breakpoints


def _group_tests_by_width(running_tests, layout_breakpoints):
    # type: (List[RunningTest], Optional[List[int]]) -> Dict[int, List[RunningTest]]
    if isinstance(layout_breakpoints, list):
        layout_breakpoints = sorted(set(layout_breakpoints))
        layout_breakpoints = [layout_breakpoints[0] - 1] + layout_breakpoints

        def matching_breakpoint(test):
            i = bisect_right(layout_breakpoints, test.browser_info.width)
            return layout_breakpoints[max(i - 1, 0)]

    elif layout_breakpoints is True:

        def matching_breakpoint(test):
            return test.browser_info.width

    else:

        def matching_breakpoint(test):
            return None

    running_tests.sort(key=lambda test: test.browser_info.width)
    grouped = itertools.groupby(running_tests, matching_breakpoint)
    return {width: list(tests) for width, tests in grouped}
