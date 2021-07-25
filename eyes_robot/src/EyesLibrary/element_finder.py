from AppiumLibrary.locators import ElementFinder as AppiumElementFinder
from EyesLibrary import SelectedRunner
from EyesLibrary.base import LibraryComponent
from selenium.webdriver.remote.webelement import By
from SeleniumLibrary import ElementFinder as SeleniumElementFinder

from applitools.selenium.validators import is_webelement


class AppiumElementFinderAdapter(AppiumElementFinder):
    def __init__(self, driver):
        super(AppiumElementFinderAdapter, self).__init__()
        self.__driver = driver

    def find(self, locator, tag=None):
        return super(AppiumElementFinderAdapter, self).find(self.__driver, locator, tag)


class ElementFinder(LibraryComponent):
    def __init__(self, *args, **kwargs):
        super(ElementFinder, self).__init__(*args, **kwargs)
        self._element_finders = {
            SelectedRunner.selenium: lambda: SeleniumElementFinder(
                self._libraries.get(SelectedRunner.selenium)
            ),
            SelectedRunner.selenium_ufg: lambda: SeleniumElementFinder(
                self._libraries.get(SelectedRunner.selenium)
            ),
            SelectedRunner.appium: lambda: AppiumElementFinderAdapter(self.driver),
        }
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

    def find(self, locator):
        if is_webelement(locator):
            return locator
        finder = self._element_finders[self.ctx.selected_runner]()
        return finder.find(locator)

    def convert_to_by_selector(self, locator):
        if is_webelement(locator):
            raise TypeError("Cannot convert WebElement to selector")
        finder = self._element_finders[self.ctx.selected_runner]()
        prefix, criteria = finder._parse_locator(locator)
        return [self._selectors[prefix], criteria]
