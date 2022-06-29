from __future__ import absolute_import, unicode_literals

from typing import TYPE_CHECKING, Text

try:
    from appium.webdriver.common.appiumby import AppiumBy
except ImportError:
    # for appium<2
    from appium.webdriver.common.mobileby import MobileBy as AppiumBy

from AppiumLibrary import AppiumLibrary
from AppiumLibrary.locators import ElementFinder as AppiumElementFinder
from selenium.webdriver.remote.webelement import By
from SeleniumLibrary import SeleniumLibrary
from SeleniumLibrary.locators import ElementFinder as SeleniumElementFinder

from applitools.common.validators import is_webelement

from .base import LibraryComponent
from .errors import EyesLibraryValueError

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import BySelector


class AppiumElementFinderAdapter(AppiumElementFinder):
    def __init__(self, driver):
        super(AppiumElementFinderAdapter, self).__init__()
        self.__driver = driver


SELENIUM_LOCATOR_TO_BY_SELECTOR = {
    "id": By.ID,
    "xpath": By.XPATH,
    "link": By.LINK_TEXT,
    "partial link": By.PARTIAL_LINK_TEXT,
    "name": By.NAME,
    "tag": By.TAG_NAME,
    "class": By.CLASS_NAME,
    "css": By.CSS_SELECTOR,
}

APPIUM_LOCATOR_TO_BY_SELECTOR = {
    "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
    "android": AppiumBy.ANDROID_UIAUTOMATOR,
    "ios": AppiumBy.IOS_UIAUTOMATION,
    "nsp": AppiumBy.IOS_PREDICATE,
    "chain": AppiumBy.IOS_CLASS_CHAIN,
}
APPIUM_LOCATOR_TO_BY_SELECTOR.update(SELENIUM_LOCATOR_TO_BY_SELECTOR)


class LocatorConverter(LibraryComponent):
    def __init__(self, *args, **kwargs):
        super(LocatorConverter, self).__init__(*args, **kwargs)
        if isinstance(self.ctx.current_library, SeleniumLibrary):
            self._element_finder = SeleniumElementFinder(self.library)
            self._locator_to_by_selector = SELENIUM_LOCATOR_TO_BY_SELECTOR
        elif isinstance(self.ctx.current_library, AppiumLibrary):
            self._element_finder = AppiumElementFinderAdapter(self.driver)
            self._locator_to_by_selector = APPIUM_LOCATOR_TO_BY_SELECTOR
        else:
            raise EyesLibraryValueError(
                "Not supported library. Should be `SeleniumLibrary` or `AppiumLibrary`"
            )

    def to_by_selector(self, locator):
        # type: (Text) -> BySelector
        if is_webelement(locator):
            raise EyesLibraryValueError("Cannot convert WebElement to selector")
        prefix, criteria = self._element_finder._parse_locator(locator)
        if prefix is None:
            # appium returns None instead of `default`
            prefix = "default"
        if not criteria:
            raise ValueError("Incorrect selector: `{}`".format(locator))
        return self.__locator_to_by_selector(prefix, criteria)

    def __locator_to_by_selector(self, prefix, criteria):
        # type: (Text, Text) -> BySelector
        if prefix == "default":
            if criteria.startswith("//"):
                return [By.XPATH, criteria]
            return [By.ID, criteria]
        return [self._locator_to_by_selector[prefix], criteria]
