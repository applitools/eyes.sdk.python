from collections import namedtuple

import pytest
from appium.webdriver.common.mobileby import MobileBy
from AppiumLibrary import AppiumLibrary
from mock import Mock
from selenium.webdriver.common.by import By
from SeleniumLibrary import SeleniumLibrary

from EyesLibrary import LocatorConverter
from EyesLibrary.errors import EyesLibraryValueError

TestData = namedtuple("TestData", "selector result")
SELENIUM_SELECTORS_DATA = [
    TestData("id:selector", [By.ID, "selector"]),
    TestData("xpath:selector", [By.XPATH, "selector"]),
    TestData("link:some-link", [By.LINK_TEXT, "some-link"]),
    TestData("partial link:some-link", [By.PARTIAL_LINK_TEXT, "some-link"]),
    TestData("name:some-name", [By.NAME, "some-name"]),
    TestData("tag:some-tag", [By.TAG_NAME, "some-tag"]),
    TestData("class:some-class", [By.CLASS_NAME, "some-class"]),
    TestData("css:css-selector", [By.CSS_SELECTOR, "css-selector"]),
]
APPIUM_SELECTORS_DATA = [
    TestData("id=selector", [By.ID, "selector"]),
    TestData("xpath=selector", [By.XPATH, "selector"]),
    TestData("link=some-link", [By.LINK_TEXT, "some-link"]),
    TestData("partial link=some-link", [By.PARTIAL_LINK_TEXT, "some-link"]),
    TestData("name=some-name", [By.NAME, "some-name"]),
    TestData("tag=some-tag", [By.TAG_NAME, "some-tag"]),
    TestData("class=some-class", [By.CLASS_NAME, "some-class"]),
    TestData("css=css-selector", [By.CSS_SELECTOR, "css-selector"]),
    TestData("accessibility_id=selector", [MobileBy.ACCESSIBILITY_ID, "selector"]),
    TestData("android=selector", [MobileBy.ANDROID_UIAUTOMATOR, "selector"]),
    TestData("ios=selector", [MobileBy.IOS_UIAUTOMATION, "selector"]),
    TestData("nsp=selector", [MobileBy.IOS_PREDICATE, "selector"]),
    TestData("chain=selector", [MobileBy.IOS_CLASS_CHAIN, "selector"]),
]


@pytest.mark.parametrize("data", SELENIUM_SELECTORS_DATA, ids=lambda d: d.selector)
def test_convert_selenium_library_selector(eyes_library_with_selenium, data):
    assert data.result == LocatorConverter(eyes_library_with_selenium).to_by_selector(
        data.selector
    )


@pytest.mark.parametrize("data", APPIUM_SELECTORS_DATA, ids=lambda d: d.selector)
def test_convert_appium_library_selector(eyes_library_with_appium, data):
    assert data.result == LocatorConverter(eyes_library_with_appium).to_by_selector(
        data.selector
    )


def test_default_locator(eyes_library_with_selenium):
    lc = LocatorConverter(eyes_library_with_selenium)
    assert [By.ID, "default"] == lc.to_by_selector("default")
    assert [By.XPATH, "//default"] == lc.to_by_selector("//default")
    assert [By.ID, "incorrect:default"] == lc.to_by_selector("incorrect:default")
