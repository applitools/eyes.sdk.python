from appium.webdriver import WebElement as AppiumWebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement

import pytest
from applitools.selenium import EyesWebElement, Region
from applitools.selenium.fluent import SeleniumCheckSettings
from mock import MagicMock


def get_cs_from_method(method_name, *args):
    """
    Return initialized CheckSettings instance and invoked `method_name` with `args`

    Example ::

        cs = SeleniumCheckSettings().region(*args)
    """
    return getattr(SeleniumCheckSettings(), method_name)(*args)


def get_regions_from_(method_name, *args):
    """
        Return regions for invoked method from CheckSettings

    :param method_name: layout, ignore, strict or content
    """
    cs = get_cs_from_method(method_name, *args)
    regions = getattr(cs.values, "{}_regions".format(method_name))
    return regions


def test_check_region_and_frame_with_unsupported_input():
    with pytest.raises(TypeError):
        cs = get_cs_from_method("region", 12355)
    with pytest.raises(TypeError):
        cs = get_cs_from_method("frame", set())


@pytest.mark.parametrize("method_name", ["ignore", "layout", "strict", "content"])
def test_match_region_with_unsupported_input(method_name):
    with pytest.raises(TypeError):
        cs = get_cs_from_method(method_name, 1245)


def test_check_frame(method_name="frame"):
    frame_reference = "frame-name-or-id"
    cs = get_cs_from_method(method_name, frame_reference)
    assert cs.values.frame_chain[0].frame_name_or_id == frame_reference

    frame_selector = [By.ID, "some-selector"]
    cs = get_cs_from_method(method_name, frame_selector)
    assert cs.values.frame_chain[0].frame_selector == [By.ID, "some-selector"]

    frame_index = 3
    cs = get_cs_from_method(method_name, frame_index)
    assert cs.values.frame_chain[0].frame_index == frame_index

    frame_element = MagicMock(EyesWebElement)
    cs = get_cs_from_method(method_name, frame_element)
    assert cs.values.frame_chain[0].frame_element == frame_element


def test_check_region_with_region(method_name="region"):
    region = Region(0, 1, 2, 3)
    cs = get_cs_from_method(method_name, region)
    assert cs.values.target_region == region


def test_check_region_with_elements(method_name="region"):
    eyes_element = MagicMock(EyesWebElement)
    cs = get_cs_from_method(method_name, eyes_element)
    assert cs.values.target_element == eyes_element

    selenium_element = MagicMock(SeleniumWebElement)
    cs = get_cs_from_method(method_name, selenium_element)
    assert cs.values.target_element == selenium_element

    appium_element = MagicMock(AppiumWebElement)
    cs = get_cs_from_method(method_name, appium_element)
    assert cs.values.target_element == appium_element


@pytest.mark.parametrize(
    "by", [By.NAME, By.ID, By.CLASS_NAME, By.TAG_NAME, By.CSS_SELECTOR, By.XPATH]
)
def test_check_region_with_by_params(by, method_name="region"):
    value = "Selector"
    cs = get_cs_from_method(method_name, [by, value])
    assert cs.values.target_selector == [by, value]


@pytest.mark.parametrize("method_name", ["ignore", "layout", "strict", "content"])
def test_match_regions_with_selectors_input(method_name):
    css_selector = ".cssSelector"
    regions = get_regions_from_(method_name, css_selector)
    assert regions[0].by == By.CSS_SELECTOR
    assert regions[0].value == css_selector

    locator = [By.XPATH, "locator"]
    regions = get_regions_from_(method_name, locator, css_selector)
    assert regions[0].by == By.XPATH
    assert regions[0].value == "locator"
    assert regions[1].by == By.CSS_SELECTOR
    assert regions[1].value == css_selector


@pytest.mark.parametrize("method_name", ["ignore", "layout", "strict", "content"])
def test_match_regions_with_regions_input(method_name):
    region, region1 = Region(0, 1, 2, 3), Region(0, 2, 4, 5)
    regions = get_regions_from_(method_name, region)
    assert regions[0]._region == region

    regions = get_regions_from_(method_name, region, region1)
    assert regions[0]._region == region
    assert regions[1]._region == region1


@pytest.mark.parametrize("method_name", ["ignore", "layout", "strict", "content"])
def test_match_regions_with_elements(method_name):
    eyes_element = MagicMock(EyesWebElement)
    selenium_element = MagicMock(SeleniumWebElement)
    appium_element = MagicMock(AppiumWebElement)

    regions = get_regions_from_(
        method_name, eyes_element, selenium_element, appium_element
    )
    assert regions[0].element == eyes_element
    assert regions[1].element == selenium_element
    assert regions[2].element == appium_element


@pytest.mark.parametrize("method_name", ["ignore", "layout", "strict", "content"])
def test_match_regions_with_by_values(method_name):
    by_name = [By.NAME, "some-name"]
    by_id = [By.ID, "ident"]
    by_class = [By.CLASS_NAME, "class_name"]
    by_tag_name = [By.TAG_NAME, "tag_name"]
    by_css_selector = [By.CSS_SELECTOR, "css_selector"]
    by_xpath = [By.XPATH, "xpath"]

    regions = get_regions_from_(
        method_name, by_name, by_id, by_class, by_tag_name, by_css_selector, by_xpath
    )
    assert regions[0].by == By.NAME
    assert regions[0].value == "some-name"
    assert regions[1].by == By.ID
    assert regions[1].value == "ident"
    assert regions[2].by == By.CLASS_NAME
    assert regions[2].value == "class_name"
    assert regions[3].by == By.TAG_NAME
    assert regions[3].value == "tag_name"
    assert regions[4].by == By.CSS_SELECTOR
    assert regions[4].value == "css_selector"
    assert regions[5].by == By.XPATH
    assert regions[5].value == "xpath"


def test_before_render_screenshot_hook():
    cs = SeleniumCheckSettings()
    cs.before_render_screenshot_hook("some hook")
    assert cs.values.script_hooks["beforeCaptureScreenshot"] == "some hook"
