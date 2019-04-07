import os
import typing
from time import sleep

import attr

from applitools.common import EyesError, TestResults, logger
from applitools.common.utils import argument_guard
from applitools.common.visual_grid import RenderBrowserInfo, VisualGridSelector
from applitools.core import CheckSettings, GetRegion
from applitools.selenium import resource
from applitools.selenium.fluent import SeleniumCheckSettings

from .eyes_connector import EyesConnector
from .running_test import RunningTest
from .visual_grid_runner import VisualGridRunner

if typing.TYPE_CHECKING:
    from typing import List, Text, Union, Optional
    from applitools.common.utils.custom_types import AnyWebDriver, AnyWebElement
    from applitools.selenium import Eyes, EyesWebDriver, eyes_selenium_utils


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


PROCESS_RESOURCES = resource.get_resource("processPageAndSerialize.js")


@attr.s
class WebElementRegion(object):
    region_provider = attr.ib()  # type: Union[Text, GetRegion]
    webelement = attr.ib()  # type: AnyWebElement


class VisualGridEyes(object):
    is_disabled = False
    server_url = None
    _api_key = None
    vg_manager = None  # type: VisualGridRunner

    url = None
    branch_name = None
    parent_branch_name = None
    server_connector = None
    driver = None  # type: AnyWebDriver
    _config_provider = None
    rendering_info = None
    vgeyes_connector = None
    test_list = []  # type: List[RunningTest]
    is_vgeyes_issued_open_tasks = False

    @property
    def api_key(self):
        if self._api_key is None:
            self._api_key = os.environ.get("APPLITOOLS_API_KEY")
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value

    def __init__(self, runner, config):
        # type: (VisualGridRunner, Eyes)-> None
        self._elements = []
        self._config_provider = config
        argument_guard.not_none(runner)
        self.is_opened = False
        self.vg_manager = runner

    @property
    def configuration(self):
        return self._config_provider.configuration

    def open(self, driver):
        # type: (AnyWebDriver) -> EyesWebDriver
        if self.is_disabled:
            return driver
        logger.open_()

        argument_guard.not_none(driver)
        self._init_driver(driver)

        logger.info("getting all browsers info...")
        browsers_info = self.configuration.browsers_info
        logger.info("creating test descriptors for each browser info...")
        for b_info in browsers_info:
            self.test_list.append(
                RunningTest(
                    self._create_vgeyes_connector(b_info), self.configuration, b_info
                )
            )
        self.is_opened = True
        self.vg_manager.open(self)
        logger.info("opening {} tests...".format(len(self.test_list)))
        return driver

    def check(self, name, check_settings):
        # type: (Text, SeleniumCheckSettings) -> bool
        if self.is_disabled:
            return False
        argument_guard.is_a(check_settings, CheckSettings)

        self._try_set_target_selector(check_settings)

        self.configuration.send_dom = check_settings.values.send_dom

        size_mode = check_settings.values.size_mode
        if size_mode is None:
            if self.configuration.force_full_page_screenshot:
                check_settings.values.size_mode = "full-page"

        dom_capt_script = (
            "var callback = arguments[arguments.length - 1]; return (%s)().then("
            "JSON.stringify).then(callback, function(err) {callback(err.stack || "
            "err.toString())})" % PROCESS_RESOURCES
        )

        script_result = self.driver.execute_async_script(dom_capt_script)
        logger.info("check('{}', check_settings) - begin".format(name))

        # region_xpaths = self.get_region_xpaths(check_settings)
        # logger.info("region_xpaths: {}".format(region_xpaths))

        # open_tasks = self.add_open_task_to_all_running_test()
        try:
            for test in self.test_list:
                test.check(name, check_settings, script_result, self.vg_manager)
        except Exception as e:
            logger.exception(e)
            for test in self.test_list:
                test.becomes_tested()
        logger.info("added check tasks  {}".format(check_settings))

    def close(self, throw_exception=True):
        # type: (Optional[bool]) -> TestResults
        if self.is_disabled:
            return False
        if not self.test_list:
            return False
        for test in self.test_list:
            test.close()

        while True:
            completed_states = [
                test.state for test in self.test_list if test.state == "completed"
            ]
            if completed_states:
                break
            sleep(0.5)
        self.is_opened = False
        for test in self.test_list:
            if test.pending_exceptions:
                raise test.pending_exceptions

        # if throw_exception:
        #     for test in self.test_list:
        #         if test.test_result.is_new:
        #             raise NewTestError()

        # return self._close_and_return_results()
        results = [test.test_result for test in self.test_list]
        self.vg_manager.stop()
        if results:
            return results[0]

    def _init_driver(self, driver):
        # type: (AnyWebDriver)->None
        self.driver = driver
        self.url = driver.current_url

    def _create_vgeyes_connector(self, b_info):
        # type: (RenderBrowserInfo) -> EyesConnector
        vgeyes_connector = EyesConnector(b_info)
        if b_info.emulation_info:
            vgeyes_connector.device = b_info.emulation_info.device_name

        vgeyes_connector.batch = self.configuration.batch
        vgeyes_connector.branch_name = self.configuration.branch_name
        vgeyes_connector.parent_branch_name = self.configuration.parent_branch_name
        if self.server_connector:
            vgeyes_connector._server_connector = self.server_connector

        if self.server_url:
            vgeyes_connector.server_url = self.server_url
        if self.api_key:
            vgeyes_connector.api_key = self.api_key
        else:
            raise EyesError("Missing API key")

        if self.rendering_info is None:
            logger.debug("initializing rendering info...")
            self.rendering_info = vgeyes_connector.render_info()

        self.vgeyes_connector = vgeyes_connector
        return vgeyes_connector

    def _try_set_target_selector(self, check_settings):
        # type: (SeleniumCheckSettings) -> None
        element = check_settings.values.target_element
        if element is None:
            target_selector = check_settings.values.target_selector
            if target_selector:
                element = self.driver.find_element_by_css_selector(target_selector)

        if element is None:
            return None
        element = eyes_selenium_utils.get_underlying_webelement(element)
        xpath = self.driver.execute_script(GET_ELEMENT_XPATH_JS, element)
        vgs = VisualGridSelector(xpath, "target")
        check_settings.vg.selector = vgs

    def get_region_xpaths(self, check_settings):
        # type: (SeleniumCheckSettings) -> List[VisualGridSelector]
        result = []
        element_lists = self.collect_selenium_regions(check_settings)
        for elem_list in element_lists:
            xpaths = []
            for elem_region in elem_list:
                if elem_region.webelement is None:
                    continue
                # breakpoint()
                xpath = self.driver.execute_script(
                    GET_ELEMENT_XPATH_JS, elem_region.webelement
                )
                xpaths.append(xpath)
            result.extend(xpaths)
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
                element = self.driver.find_element_by_css_selector(target_selector)

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
            webelements = rp.get_elements(self.driver)
            for elem in webelements:
                elements.append(WebElementRegion(elem, rp))
        return elements

    def add_open_task_to_all_running_test(self):
        tasks = []
        if not self.is_vgeyes_issued_open_tasks:
            for r_test in self.test_list:
                task = r_test.open()
                tasks.append(task)
            self.is_vgeyes_issued_open_tasks = True
        return tasks
