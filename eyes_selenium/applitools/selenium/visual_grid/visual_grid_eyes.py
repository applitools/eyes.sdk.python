import typing
from time import sleep

import attr
from selenium.common.exceptions import WebDriverException

from applitools.common import (
    DiffsFoundError,
    EyesError,
    NewTestError,
    TestFailedError,
    TestResults,
    logger,
)
from applitools.common.utils import argument_guard
from applitools.common.visual_grid import RenderBrowserInfo, VisualGridSelector
from applitools.core import CheckSettings, GetRegion
from applitools.selenium import eyes_selenium_utils, resource
from applitools.selenium.fluent import SeleniumCheckSettings

from .eyes_connector import EyesConnector
from .running_test import RunningTest
from .visual_grid_runner import VisualGridRunner

if typing.TYPE_CHECKING:
    from typing import List, Text, Union, Optional
    from applitools.common.config import SeleniumConfiguration
    from applitools.common.utils.custom_types import AnyWebDriver, AnyWebElement
    from applitools.selenium import Eyes, EyesWebDriver


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
    vg_manager = None  # type: VisualGridRunner
    url = None
    _config_provider = None
    _is_opened = False
    rendering_info = None
    test_list = []  # type: List[RunningTest]

    def __init__(self, runner, config):
        # type: (VisualGridRunner, Eyes)-> None
        self._elements = []
        self._config_provider = config
        argument_guard.not_none(runner)
        self.vg_manager = runner

    @property
    def is_opened(self):
        return self._is_opened

    @property
    def configuration(self):
        # type: () -> SeleniumConfiguration
        return self._config_provider.configuration

    @property
    def _seconds_to_wait_screenshot(self):
        return self.configuration.wait_before_screenshots / 1000.0

    def open(self, driver):
        # type: (AnyWebDriver) -> EyesWebDriver
        if self.is_disabled:
            return driver
        logger.open_()
        argument_guard.not_none(driver)
        logger.debug("VisualGridEyes.open(%s)" % self.configuration)

        self._init_driver(driver)
        browsers_info = self.configuration.browsers_info

        if self.configuration.viewport_size:
            self._set_viewport_size(self.configuration.viewport_size)
        elif browsers_info:
            viewports = [bi.viewportsize for bi in browsers_info]
            if viewports:
                self.configuration.viewport_size = viewports[0]
        else:
            self.configuration.viewport_size = self._get_viewport_size()

        for b_info in browsers_info:
            self.test_list.append(
                RunningTest(
                    self._create_vgeyes_connector(b_info), self.configuration, b_info
                )
            )
        self._is_opened = True
        self.vg_manager.open(self)
        logger.info("VisualGridEyes opening {} tests...".format(len(self.test_list)))
        return driver

    def get_script_result(self):
        dom_capt_script = (
            "var callback = arguments[arguments.length - 1]; return (%s)().then("
            "JSON.stringify).then(callback, function(err) {callback(err.stack || "
            "err.toString())})" % PROCESS_RESOURCES
        )
        for i in range(3):
            sleep(self._seconds_to_wait_screenshot)
            logger.debug("Capturing script_result ({} - try)".format(i))
            try:
                script_result = self.driver.execute_async_script(dom_capt_script)
                break
            except WebDriverException:
                logger.exception("During querying of script result got error")
                script_result = self.get_script_result()
        return script_result

    def check(self, name, check_settings):
        # type: (Text, SeleniumCheckSettings) -> bool
        if self.is_disabled:
            return False
        argument_guard.is_a(check_settings, CheckSettings)
        logger.debug("VisualGridEyes.check(%s, %s)" % (name, check_settings))
        self._try_set_target_selector(check_settings)

        self.configuration.send_dom = check_settings.values.send_dom

        size_mode = check_settings.values.size_mode
        if size_mode is None:
            if self.configuration.force_full_page_screenshot:
                check_settings.values.size_mode = "full-page"

        logger.info("check('{}', check_settings) - begin".format(name))

        # region_xpaths = self.get_region_xpaths(check_settings)
        region_xpaths = []
        self.region_to_check = None
        # logger.info("region_xpaths: {}".format(region_xpaths))
        script_result = self.get_script_result()
        try:
            for test in self.test_list:
                test.check(
                    tag=name,
                    check_settings=check_settings,
                    script_result=script_result,
                    visual_grid_manager=self.vg_manager,
                    region_selectors=region_xpaths,
                    size_mode=size_mode,
                    region_to_check=self.region_to_check,
                )
                if test.state == "new":
                    test.becomes_not_rendered()
        except Exception as e:
            logger.exception(e)
            for test in self.test_list:
                test.becomes_tested()
        logger.info("added check tasks  {}".format(check_settings))

    def close(self, raise_ex=True):  # noqa
        # type: (Optional[bool]) -> List[TestResults]
        if self.is_disabled:
            logger.debug("close(): ignored (disabled)")
            return []
        if not self.test_list:
            return []
        logger.debug("VisualGridEyes.close()\n\t test_list %s" % self.test_list)
        for test in self.test_list:
            test.close()

        while True:
            completed_states = [
                test.state for test in self.test_list if test.state == "completed"
            ]
            if len(completed_states) == len(self.test_list):
                break
            sleep(0.5)
        self._is_opened = False
        self.vg_manager.stop()
        logger.close()

        for test in self.test_list:
            if test.pending_exceptions:
                raise EyesError(
                    "During test execution above exception raised. \n {}".join(
                        test.pending_exceptions
                    )
                )

        if raise_ex:
            for test in self.test_list:
                results = test.test_result
                msg = "Test '{}' of '{}'. \n\tSee details at: {}".format(
                    results.name, results.app_name, results.url
                )
                if results.is_unresolved and not results.is_new:
                    raise DiffsFoundError(msg, results)
                if results.is_new:
                    raise NewTestError(msg, results)
                if results.is_failed:
                    raise TestFailedError(msg, results)

        failed_results = [
            test.test_result
            for test in self.test_list
            if test.test_result.is_unresolved or test.test_result.is_failed
        ]
        return failed_results

    def _init_driver(self, driver):
        # type: (AnyWebDriver)->None
        self.driver = driver
        self.url = driver.current_url

    def _create_vgeyes_connector(self, b_info):
        # type: (RenderBrowserInfo) -> EyesConnector
        vgeyes_connector = EyesConnector(b_info, self.configuration.clone())
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
                element = self.driver.find_element_by_css_selector(target_selector)

        if element is None:
            return None
        element = eyes_selenium_utils.get_underlying_webelement(element)
        xpath = self.driver.execute_script(GET_ELEMENT_XPATH_JS, element)
        vgs = VisualGridSelector(xpath, "target")
        check_settings.values.selector = vgs

    # def get_region_xpaths(self, check_settings):
    #     # type: (SeleniumCheckSettings) -> List[VisualGridSelector]
    #     result = []
    #     element_lists = self.collect_selenium_regions(check_settings)
    #     for elem_list in element_lists:
    #         xpaths = []
    #         for elem_region in elem_list:
    #             if elem_region.webelement is None:
    #                 continue
    #             # breakpoint()
    #             xpath = self.driver.execute_script(
    #                 GET_ELEMENT_XPATH_JS, elem_region.webelement
    #             )
    #             xpaths.append(xpath)
    #         result.extend(xpaths)
    #     return result

    # def collect_selenium_regions(self, check_settings):
    #     # type: (SeleniumCheckSettings) -> List[List[WebElementRegion]]
    #     ignore_elements = self.get_elements_from_regions(
    #         check_settings.values.ignore_regions
    #     )
    #     layout_elements = self.get_elements_from_regions(
    #         check_settings.values.layout_regions
    #     )
    #     strict_elements = self.get_elements_from_regions(
    #         check_settings.values.strict_regions
    #     )
    #     content_elements = self.get_elements_from_regions(
    #         check_settings.values.content_regions
    #     )
    #     floating_elements = self.get_elements_from_regions(
    #         check_settings.values.floating_regions
    #     )
    #     element = check_settings.values.target_element
    #     if element is None:
    #         target_selector = check_settings.values.target_selector
    #         if target_selector:
    #             element = self.driver.find_element_by_css_selector(target_selector)
    #
    #     targets = [WebElementRegion("target", element)]
    #     return [
    #         ignore_elements,
    #         layout_elements,
    #         strict_elements,
    #         content_elements,
    #         floating_elements,
    #         targets,
    #     ]
    #
    # def get_elements_from_regions(self, regions_provider):
    #     # type:(List[GetRegion])->List[WebElementRegion]
    #     elements = []
    #     for rp in regions_provider:
    #         webelements = rp.get_elements(self.driver)
    #         for elem in webelements:
    #             elements.append(WebElementRegion(elem, rp))
    #     return elements

    # def add_open_task_to_all_running_test(self):
    #     tasks = []
    #     if not self.is_vgeyes_issued_open_tasks:
    #         for r_test in self.test_list:
    #             task = r_test.open()
    #             tasks.append(task)
    #         self.is_vgeyes_issued_open_tasks = True
    #     return tasks

    def _get_viewport_size(self):
        argument_guard.not_none(self.driver)
        return eyes_selenium_utils.get_viewport_size(self.driver)

    def _set_viewport_size(self, viewport_size):
        try:
            eyes_selenium_utils.set_viewport_size(self.driver, viewport_size)
        except Exception as e:
            logger.exception(e)
            raise TestFailedError(str(e))
