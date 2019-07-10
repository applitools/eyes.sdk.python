from mock import MagicMock
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement
from appium.webdriver import WebElement as AppiumWebElement

from applitools.selenium import Region, EyesWebElement
from applitools.selenium.fluent import SeleniumCheckSettings


def test_check_region(driver_mock):
    region = Region(0, 1, 2, 3)
    cs = SeleniumCheckSettings().region(region)
    assert cs.values.target_region == region

    selector_or_xpath = ".cssSelector_or_XPATH"
    cs = SeleniumCheckSettings().region(selector_or_xpath)
    assert cs.values.target_selector == selector_or_xpath

    eyes_element = MagicMock(EyesWebElement)
    cs = SeleniumCheckSettings().region(eyes_element)
    assert cs.values.target_element == eyes_element

    selenium_element = MagicMock(SeleniumWebElement)
    cs = SeleniumCheckSettings().region(selenium_element)
    assert cs.values.target_element == selenium_element

    appium_element = MagicMock(AppiumWebElement)
    cs = SeleniumCheckSettings().region(appium_element)
    assert cs.values.target_element == appium_element

    cs = SeleniumCheckSettings().region([By.NAME, "some-name"])
    assert cs.values.target_selector == '[name="some-name"]'
    cs = SeleniumCheckSettings().region([By.ID, "ident"])
    assert cs.values.target_selector == "#ident"
    cs = SeleniumCheckSettings().region([By.CLASS_NAME, "class_name"])
    assert cs.values.target_selector == ".class_name"
    cs = SeleniumCheckSettings().region([By.TAG_NAME, "tag_name"])
    assert cs.values.target_selector == "tag_name"
    cs = SeleniumCheckSettings().region([By.CSS_SELECTOR, selector_or_xpath])
    assert cs.values.target_selector == selector_or_xpath
    cs = SeleniumCheckSettings().region([By.XPATH, selector_or_xpath])
    assert cs.values.target_selector == selector_or_xpath
