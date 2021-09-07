from __future__ import absolute_import, unicode_literals

from AppiumLibrary.locators import ElementFinder as AppiumElementFinder
from selenium.webdriver.remote.webelement import By
from SeleniumLibrary import ElementFinder as SeleniumElementFinder

from applitools.selenium.validators import is_webelement

from .base import LibraryComponent
from .config_parser import SelectedRunner


class AppiumElementFinderAdapter(AppiumElementFinder):
    def __init__(self, driver):
        super(AppiumElementFinderAdapter, self).__init__()
        self.__driver = driver


class ElementFinder(LibraryComponent):
    def __init__(self, *args, **kwargs):
        super(ElementFinder, self).__init__(*args, **kwargs)
        if self.ctx.selected_runner in [
            SelectedRunner.web,
            SelectedRunner.web_ufg,
        ]:
            self._element_finder = SeleniumElementFinder(self.library)
        elif self.ctx.selected_runner == SelectedRunner.mobile_native:
            self._element_finder = AppiumElementFinderAdapter(self.driver)

        self._selectors = {
            "id": By.ID,
            "xpath": By.XPATH,
            "link": By.LINK_TEXT,
            "partial link": By.PARTIAL_LINK_TEXT,
            "name": By.NAME,
            "tag": By.TAG_NAME,
            "class": By.CLASS_NAME,
            "css": By.CSS_SELECTOR,
        }

    def convert_to_by_selector(self, locator):
        if is_webelement(locator):
            raise TypeError("Cannot convert WebElement to selector")
        prefix, criteria = self._element_finder._parse_locator(locator)
        if not criteria:
            raise ValueError("Incorrect selector: `{}`".format(locator))
        return [self._selectors[prefix], criteria]
