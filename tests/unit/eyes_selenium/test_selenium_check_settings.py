import mock
import pytest
from appium.webdriver import WebElement as AppiumWebElement
from mock import MagicMock
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement

from applitools.common import FloatingBounds
from applitools.selenium import AccessibilityRegionType, EyesWebElement, Region
from applitools.selenium.fluent import SeleniumCheckSettings


def get_cs_from_method(method_name, *args, **kwargs):
    """
    Return initialized CheckSettings instance and invoked `method_name` with `args`

    Example ::

        cs = SeleniumCheckSettings().region(*args)
    """
    return getattr(SeleniumCheckSettings(), method_name)(*args, **kwargs)


def get_regions_from_(method_name, *args, **kwargs):
    """
        Return regions for invoked method from CheckSettings

    :param method_name: layout, ignore, strict or content
    """
    cs = get_cs_from_method(method_name, *args, **kwargs)
    regions = getattr(cs.values, "{}_regions".format(method_name))
    return regions


def test_default_check_settings():
    check_settings = SeleniumCheckSettings()

    assert check_settings.values.disable_browser_fetching is None


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
    assert regions[0]._by == By.CSS_SELECTOR
    assert regions[0]._value == css_selector

    locator = [By.XPATH, "locator"]
    regions = get_regions_from_(method_name, locator, css_selector)
    assert regions[0]._by == By.XPATH
    assert regions[0]._value == "locator"
    assert regions[1]._by == By.CSS_SELECTOR
    assert regions[1]._value == css_selector


@pytest.mark.parametrize("method_name", ["ignore", "layout", "strict", "content"])
def test_match_regions_with_regions_input(method_name):
    region, region1 = Region(0, 1, 2, 3), Region(0, 2, 4, 5)
    regions = get_regions_from_(method_name, region)
    assert regions[0]._region == region
    assert regions[0].get_regions(None, None) == [region]

    regions = get_regions_from_(method_name, region, region1)
    assert regions[0]._region == region
    assert regions[1]._region == region1
    assert regions[0].get_regions(None, None) == [region]
    assert regions[1].get_regions(None, None) == [region1]


@pytest.mark.parametrize("method_name", ["ignore", "layout", "strict", "content"])
def test_match_regions_with_elements(method_name):
    eyes_element = MagicMock(EyesWebElement)
    selenium_element = MagicMock(SeleniumWebElement)
    appium_element = MagicMock(AppiumWebElement)

    regions = get_regions_from_(
        method_name, eyes_element, selenium_element, appium_element
    )
    assert regions[0]._element == eyes_element
    assert regions[1]._element == selenium_element
    assert regions[2]._element == appium_element


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
    assert regions[0]._by == By.NAME
    assert regions[0]._value == "some-name"
    assert regions[1]._by == By.ID
    assert regions[1]._value == "ident"
    assert regions[2]._by == By.CLASS_NAME
    assert regions[2]._value == "class_name"
    assert regions[3]._by == By.TAG_NAME
    assert regions[3]._value == "tag_name"
    assert regions[4]._by == By.CSS_SELECTOR
    assert regions[4]._value == "css_selector"
    assert regions[5]._by == By.XPATH
    assert regions[5]._value == "xpath"


def test_match_floating_region():
    regions = get_regions_from_("floating", 5, [By.NAME, "name"])
    assert regions[0].floating_bounds == FloatingBounds(5, 5, 5, 5)
    assert regions[0]._by == By.NAME
    assert regions[0]._value == "name"

    regions = get_regions_from_("floating", 5, "name")
    assert regions[0].floating_bounds == FloatingBounds(5, 5, 5, 5)
    assert regions[0]._by == By.CSS_SELECTOR
    assert regions[0]._value == "name"

    element = MagicMock(SeleniumWebElement)
    regions = get_regions_from_("floating", 5, element)
    assert regions[0].floating_bounds == FloatingBounds(5, 5, 5, 5)
    assert regions[0]._element == element


def test_match_accessibility_region():
    regions = get_regions_from_(
        "accessibility", [By.NAME, "name"], AccessibilityRegionType.BoldText
    )
    assert regions[0].accessibility_type == AccessibilityRegionType.BoldText
    assert regions[0]._by == By.NAME
    assert regions[0]._value == "name"

    regions = get_regions_from_(
        "accessibility", "name", AccessibilityRegionType.BoldText
    )
    assert regions[0].accessibility_type == AccessibilityRegionType.BoldText
    assert regions[0]._by == By.CSS_SELECTOR
    assert regions[0]._value == "name"

    element = MagicMock(SeleniumWebElement)
    regions = get_regions_from_(
        "accessibility", element, AccessibilityRegionType.BoldText
    )
    assert regions[0].accessibility_type == AccessibilityRegionType.BoldText
    assert regions[0]._element == element


def test_before_render_screenshot_hook():
    cs = SeleniumCheckSettings()
    cs.before_render_screenshot_hook("some hook")
    assert cs.values.script_hooks["beforeCaptureScreenshot"] == "some hook"


def test_disable_browser_fetching_combinations():
    from applitools.selenium import Configuration, Target
    from applitools.selenium.visual_grid import VisualGridEyes

    effective_option = VisualGridEyes._effective_disable_browser_fetching
    cfg = Configuration()
    assert effective_option(cfg, Target.window()) is False
    assert effective_option(cfg, Target.window().disable_browser_fetching()) is True
    assert effective_option(cfg, Target.window().disable_browser_fetching(True)) is True
    assert (
        effective_option(cfg, Target.window().disable_browser_fetching(False)) is False
    )

    cfg.set_disable_browser_fetching(False)

    assert effective_option(cfg, Target.window()) is False
    assert effective_option(cfg, Target.window().disable_browser_fetching()) is True
    assert effective_option(cfg, Target.window().disable_browser_fetching(True)) is True
    assert (
        effective_option(cfg, Target.window().disable_browser_fetching(False)) is False
    )

    cfg.set_disable_browser_fetching(True)

    assert effective_option(cfg, Target.window()) is True
    assert effective_option(cfg, Target.window().disable_browser_fetching()) is True
    assert effective_option(cfg, Target.window().disable_browser_fetching(True)) is True
    assert (
        effective_option(cfg, Target.window().disable_browser_fetching(False)) is False
    )


@pytest.mark.parametrize("method_name", ["ignore", "layout", "strict", "content"])
def test_region_padding_are_added(method_name):
    regions_selector = get_regions_from_(
        method_name, [By.NAME, "name"], padding={"top": 1, "left": 2}
    )
    regions_element = get_regions_from_(
        method_name, MagicMock(EyesWebElement), padding={"width": 200, "left": 5}
    )

    assert regions_selector[0]._padding == {"top": 1, "left": 2}
    assert regions_element[0]._padding == {"width": 200, "left": 5}
