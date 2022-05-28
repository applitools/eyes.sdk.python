import pytest
from mock import Mock
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from applitools.common import (
    AccessibilityRegionType,
    MatchLevel,
    Region,
    VisualGridOption,
)
from applitools.selenium.fluent import SeleniumCheckSettings
from EyesLibrary import CheckSettingsKeywords

WEB_ELEMENT = Mock(WebElement)

REGION_LIST = ["ignore", "layout", "content", "strict"]


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


@pytest.fixture
def get_regions_from_cs_keyword(eyes_library_with_selenium):
    def internal_func(method_name, by_method_postfix, keyword_value):
        cs_keyword = CheckSettingsKeywords(eyes_library_with_selenium)
        cs = getattr(
            cs_keyword, "{}_region_by_{}".format(method_name, by_method_postfix)
        )(keyword_value)
        regions = getattr(cs.values, "{}_regions".format(method_name))
        return regions

    return internal_func


@pytest.fixture()
def check_settings_keyword(eyes_library_with_selenium):
    return CheckSettingsKeywords(eyes_library_with_selenium)


@pytest.mark.parametrize(
    "region_to_parse,result_region", [("[23 44 55 66]", Region(23, 44, 55, 66))]
)
@pytest.mark.parametrize("region_method_name", REGION_LIST)
def test_check_regions_by_coordinates(
    region_to_parse, result_region, region_method_name, get_regions_from_cs_keyword
):
    assert get_regions_from_(
        region_method_name, result_region
    ) == get_regions_from_cs_keyword(
        region_method_name,
        by_method_postfix="coordinates",
        keyword_value=region_to_parse,
    )


@pytest.mark.parametrize("region_to_parse,result_region", [(WEB_ELEMENT, WEB_ELEMENT)])
@pytest.mark.parametrize("region_method_name", REGION_LIST)
def test_check_regions_by_element(
    region_to_parse, result_region, region_method_name, get_regions_from_cs_keyword
):
    assert get_regions_from_(
        region_method_name, result_region
    ) == get_regions_from_cs_keyword(
        region_method_name,
        by_method_postfix="element",
        keyword_value=region_to_parse,
    )


@pytest.mark.parametrize(
    "region_to_parse,result_region", [("id:some-id", [By.ID, "some-id"])]
)
@pytest.mark.parametrize("region_method_name", REGION_LIST)
def test_check_regions_by_selector(
    region_to_parse, result_region, region_method_name, get_regions_from_cs_keyword
):
    assert get_regions_from_(
        region_method_name, result_region
    ) == get_regions_from_cs_keyword(
        region_method_name,
        by_method_postfix="selector",
        keyword_value=region_to_parse,
    )


def test_floating_region_by_coordinates(check_settings_keyword):
    res = SeleniumCheckSettings().floating(34, Region(23, 44, 55, 66))
    assert res == check_settings_keyword.floating_region_with_max_offset_by_coordinates(
        34, "[23 44 55 66]"
    )
    res = SeleniumCheckSettings().floating(Region(23, 44, 55, 66), 20, 30, 40, 50)
    assert res == check_settings_keyword.floating_region_by_coordinates(
        "[23 44 55 66]", 20, 30, 40, 50
    )


def test_floating_region_by_element(check_settings_keyword, web_element):
    res = SeleniumCheckSettings().floating(34, web_element)
    assert res == check_settings_keyword.floating_region_with_max_offset_by_element(
        34, web_element
    )
    res = SeleniumCheckSettings().floating(web_element, 20, 30, 40, 50)
    assert res == check_settings_keyword.floating_region_by_element(
        web_element, 20, 30, 40, 50
    )


def test_floating_region_by_selector(check_settings_keyword, css_selector, by_selector):
    res = SeleniumCheckSettings().floating(34, by_selector)
    assert res == check_settings_keyword.floating_region_with_max_offset_by_selector(
        34, css_selector
    )
    res = SeleniumCheckSettings().floating(by_selector, 20, 30, 40, 50)
    assert res == check_settings_keyword.floating_region_by_selector(
        css_selector, 20, 30, 40, 50
    )


def test_accessibility_region_by_element(check_settings_keyword, web_element):
    res = SeleniumCheckSettings().accessibility(
        web_element, AccessibilityRegionType.RegularText
    )
    assert res == check_settings_keyword.accessibility_region_by_element(
        web_element, AccessibilityRegionType.RegularText
    )


def test_accessibility_region_by_coordinates(check_settings_keyword):
    res = SeleniumCheckSettings().accessibility(
        Region(23, 44, 55, 66), AccessibilityRegionType.RegularText
    )
    assert res == check_settings_keyword.accessibility_region_by_coordinates(
        "[23 44 55 66]", AccessibilityRegionType.RegularText
    )


def test_accessibility_region_by_selector(
    check_settings_keyword, by_selector, css_selector
):
    res = SeleniumCheckSettings().accessibility(
        by_selector, AccessibilityRegionType.RegularText
    )
    assert res == check_settings_keyword.accessibility_region_by_selector(
        css_selector, AccessibilityRegionType.RegularText
    )


def test_visual_grid_option(check_settings_keyword):
    res = SeleniumCheckSettings().visual_grid_options(VisualGridOption("KEY", "VALUE"))
    assert res == check_settings_keyword.visual_grid_option("KEY", "VALUE")


def test_disable_browser_fetching(check_settings_keyword):
    res = SeleniumCheckSettings().disable_browser_fetching()
    assert res == check_settings_keyword.disable_browser_fetching()


def test_layout_breakpoints(check_settings_keyword):
    res = SeleniumCheckSettings().layout_breakpoints(True)
    assert res == check_settings_keyword.enable_layout_breakpoints()
    res = SeleniumCheckSettings().layout_breakpoints(40, 50, 40, 60)
    assert res == check_settings_keyword.layout_breakpoints("40 50 40 60")


def test_before_render_screenshot_hook(check_settings_keyword):
    res = SeleniumCheckSettings().before_render_screenshot_hook('{"script":34}')
    assert res == check_settings_keyword.before_render_screenshot_hook('{"script":34}')


def test_send_dom(check_settings_keyword):
    res = SeleniumCheckSettings().send_dom()
    assert res == check_settings_keyword.send_dom()


def test_scroll_root_element_by_element(check_settings_keyword, web_element):
    res = SeleniumCheckSettings().scroll_root_element(web_element)
    assert res == check_settings_keyword.scroll_root_element_by_element(web_element)


def test_scroll_root_element_by_selector(
    check_settings_keyword, css_selector, by_selector
):
    res = SeleniumCheckSettings().scroll_root_element(by_selector)
    assert res == check_settings_keyword.scroll_root_element_by_selector(css_selector)


def test_variation_group_id(check_settings_keyword):
    res = SeleniumCheckSettings().variation_group_id("group id")
    assert res == check_settings_keyword.variation_group_id("group id")


def test_match_level(check_settings_keyword):
    res = SeleniumCheckSettings().match_level(MatchLevel.LAYOUT)
    assert res == check_settings_keyword.match_level("LAYOUT")


def test_enable_patterns(check_settings_keyword):
    res = SeleniumCheckSettings().enable_patterns()
    assert res == check_settings_keyword.enable_patterns()


def test_ignore_displacements(check_settings_keyword):
    res = SeleniumCheckSettings().ignore_displacements()
    assert res == check_settings_keyword.ignore_displacements()


def test_ignore_caret(check_settings_keyword):
    res = SeleniumCheckSettings().ignore_caret()
    assert res == check_settings_keyword.ignore_caret()


def test_fully(check_settings_keyword):
    res = SeleniumCheckSettings().fully()
    assert res == check_settings_keyword.fully()


def test_with_name(check_settings_keyword):
    res = SeleniumCheckSettings().with_name("NAME")
    assert res == check_settings_keyword.with_name("NAME")


def test_timeout(check_settings_keyword):
    res = SeleniumCheckSettings().timeout(53)
    assert res == check_settings_keyword.timeout(53)
