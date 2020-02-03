import json
import threading
import typing
import uuid
from collections import OrderedDict

import attr

from applitools.common import (
    DiffsFoundError,
    EyesError,
    NewTestError,
    TestFailedError,
    TestResults,
    logger,
    RectangleSize,
)
from applitools.common.utils import argument_guard, datetime_utils
from applitools.common.visual_grid import RenderBrowserInfo, VisualGridSelector
from applitools.core import CheckSettings, GetRegion
from applitools.selenium import __version__, eyes_selenium_utils, resource
from applitools.selenium.fluent import SeleniumCheckSettings

from .eyes_connector import EyesConnector
from .running_test import RunningTest
from .visual_grid_runner import VisualGridRunner

if typing.TYPE_CHECKING:
    from typing import List, Text, Union, Optional, Dict
    from applitools.common.utils.custom_types import AnyWebElement
    from applitools.selenium import Eyes, EyesWebDriver, Configuration


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


PROCESS_RESOURCES = resource.get_resource("processPageAndPoll.js")
DOM_EXTRACTION_TIMEOUT = 5 * 60 * 1000


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
        self.vg_manager = runner
        self.test_list = []  # type: List[RunningTest]
        self._test_uuid = None

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

    def add_property(self, name, value):
        # type: (Text, Text) -> None
        """
        Associates a key/value pair with the test. This can be used later for filtering.
        :param name: (string) The property name.
        :param value: (string) The property value
        """
        self.configure.properties.append({"name": name, "value": value})

    def open(self, driver):
        # type: (EyesWebDriver) -> EyesWebDriver
        self._test_uuid = uuid.uuid4()
        logger.open_()
        argument_guard.not_none(driver)
        logger.debug("VisualGridEyes.open(%s)" % self.configure)

        self._driver = driver
        self._set_viewport_size()

        for b_info in self.configure.browsers_info:
            test = RunningTest(
                self._create_vgeyes_connector(b_info), self.configure, b_info
            )
            test.on_results_received(
                lambda r: self.vg_manager.aggregate_result(test, r)
            )
            test.test_uuid = self._test_uuid
            self.test_list.append(test)
        self._is_opened = True
        self.vg_manager.open(self)
        logger.info("VisualGridEyes opening {} tests...".format(len(self.test_list)))
        return driver

    def _start_timer(self):
        def set_timer():
            self.is_check_timer_timeout = True

        timer = threading.Timer(DOM_EXTRACTION_TIMEOUT, set_timer)
        timer.daemon = True
        timer.setName("VG_StopWatch")
        timer.start()
        return timer

    def get_script_result(self):
        # type: () -> Dict
        script_response = {}
        status = None
        timer = self._start_timer()
        while True:
            if status == "SUCCESS" or self.is_check_timer_timeout:
                self.is_check_timer_timeout = False
                break
            script_result_string = self.driver.execute_script(
                PROCESS_RESOURCES + "return __processPageAndPoll();"
            )
            try:
                script_response = json.loads(
                    script_result_string, object_pairs_hook=OrderedDict
                )
                status = script_response.get("status")
            except Exception as e:
                logger.exception(e)
        timer.cancel()
        script_result = script_response.get("value")
        if script_result is None or status == "ERROR":
            raise EyesError("Failed to capture script_result")
        return script_result

    def check(self, name, check_settings):
        # type: (Text, SeleniumCheckSettings) -> None
        argument_guard.is_a(check_settings, CheckSettings)
        logger.debug("VisualGridEyes.check(%s, %s)" % (name, check_settings))
        self._try_set_target_selector(check_settings)

        self.configure.send_dom = check_settings.values.send_dom

        check_settings = self._update_check_settings(check_settings)
        logger.info("check('{}', check_settings) - begin".format(name))

        region_xpaths = self.get_region_xpaths(check_settings)
        logger.info("region_xpaths: {}".format(region_xpaths))
        script_result = self.get_script_result()
        try:
            for test in self.test_list:
                if self._test_uuid != test.test_uuid:
                    continue
                test.check(
                    tag=name,
                    check_settings=check_settings,
                    script_result=script_result,
                    visual_grid_manager=self.vg_manager,
                    region_selectors=region_xpaths,
                    region_to_check=check_settings.values.target_region,
                    script_hooks=check_settings.values.script_hooks,
                )
                if test.state == "new":
                    test.becomes_not_rendered()
        except Exception as e:
            logger.exception(e)
            self.abort()
            for test in self.test_list:
                test.becomes_tested()
        logger.info("added check tasks  {}".format(check_settings))

    def close_async(self):
        for test in self.test_list:
            test.close()

    def close(self, raise_ex=True):  # noqa
        # type: (Optional[bool]) -> Optional[TestResults]
        if not self.test_list:
            return TestResults()
        logger.debug("VisualGridEyes.close()\n\t test_list %s" % self.test_list)
        self.close_async()

        while True:
            states = list(set([t.state for t in self.test_list]))
            if len(states) == 1 and states[0] == "completed":
                break
            datetime_utils.sleep(500)

        self._is_opened = False

        for test in self.test_list:
            if test.pending_exceptions:
                raise EyesError(
                    "During test execution above exception raised. \n {:s}".join(
                        str(e) for e in test.pending_exceptions
                    )
                )
        if raise_ex:
            for test in self.test_list:
                if test.test_result is None:
                    raise TestFailedError("Test haven't finished correctly")
                results = test.test_result
                scenario_id_or_name = results.name
                app_id_or_name = results.app_name
                if results.is_unresolved and not results.is_new:
                    raise DiffsFoundError(results, scenario_id_or_name, app_id_or_name)
                if results.is_new:
                    raise NewTestError(results, scenario_id_or_name, app_id_or_name)
                if results.is_failed:
                    raise TestFailedError(results, scenario_id_or_name, app_id_or_name)

        all_results = [t.test_result for t in self.test_list if t.test_result]
        if not all_results:
            return TestResults()
        return all_results[0]

    def abort_async(self):
        """
        If a test is running, aborts it. Otherwise, does nothing.
        """
        for test in self.test_list:
            test.abort()

    def abort(self):
        """
        If a test is running, aborts it. Otherwise, does nothing.
        """
        self._is_opened = False
        self.abort_async()

    def abort_if_not_closed(self):
        logger.deprecation("Use `abort()` instead")
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
            check_settings = check_settings.fully(True if fps is None else fps)
        if send_dom is None:
            send = self.configure.send_dom
            check_settings = check_settings.send_dom(True if send is None else send)
        if ignore_displacements is None:
            check_settings = check_settings.ignore_displacements(
                self.configure.ignore_displacements
            )
        return check_settings

    def _create_vgeyes_connector(self, b_info):
        # type: (RenderBrowserInfo) -> EyesConnector
        vgeyes_connector = EyesConnector(b_info, self.configure.clone())
        if b_info.emulation_info:
            vgeyes_connector.device = b_info.emulation_info.device_name

        if self.rendering_info is None:
            self.rendering_info = vgeyes_connector.render_info()
        if self.rendering_info:
            vgeyes_connector._server_connector._render_info = self.rendering_info
        return vgeyes_connector

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
                if not render_bi.emulation_info:
                    viewport_size = RectangleSize(render_bi.width, render_bi.height)
                    break

        if viewport_size is None:
            viewport_size = self._get_viewport_size()

        self.configure.viewport_size = viewport_size
        try:
            eyes_selenium_utils.set_viewport_size(self.driver, viewport_size)
        except Exception as e:
            logger.exception(e)
            raise EyesError(str(e))
