from selenium.webdriver.common.by import By

from applitools.selenium.fluent.target_path import TargetPath
from applitools.selenium.universal_sdk_types import TransformedSelector


def test_transformed_selector_convert_region_by_css():
    converted = TransformedSelector.convert(TargetPath.region(".css"))

    assert converted.type is By.CSS_SELECTOR
    assert converted.selector == ".css"
    assert converted.frame is None
    assert converted.shadow is None


def test_transformed_selector_convert_shadow_by_css_region_by_css():
    converted = TransformedSelector.convert(TargetPath.shadow_dom("#s").region(".css"))

    assert converted.type is By.CSS_SELECTOR
    assert converted.selector == "#s"
    assert converted.frame is None
    assert type(converted.shadow) is TransformedSelector
    assert converted.shadow.type is By.CSS_SELECTOR
    assert converted.shadow.selector == ".css"
    assert converted.shadow.frame is None
    assert converted.shadow.shadow is None


def test_transformed_selector_convert_shadow_by_xpath_shadow_by_css_region_by_css():
    converted = TransformedSelector.convert(
        TargetPath.shadow_dom(By.XPATH, "//x").shadow_dom("#s").region(".css")
    )

    assert converted.type is By.XPATH
    assert converted.selector == "//x"
    assert converted.frame is None
    assert type(converted.shadow) is TransformedSelector
    assert converted.shadow.type is By.CSS_SELECTOR
    assert converted.shadow.selector == "#s"
    assert converted.shadow.frame is None
    assert type(converted.shadow.shadow) is TransformedSelector
    assert converted.shadow.shadow.type is By.CSS_SELECTOR
    assert converted.shadow.shadow.selector == ".css"
    assert converted.shadow.shadow.frame is None
    assert converted.shadow.shadow.shadow is None


def test_transformed_selector_convert_frame_by_css_region_by_css():
    converted = TransformedSelector.convert(
        TargetPath.frame(By.CSS_SELECTOR, "#s").region(".css")
    )

    assert converted.type is By.CSS_SELECTOR
    assert converted.selector == "#s"
    assert converted.shadow is None
    assert type(converted.frame) is TransformedSelector
    assert converted.frame.type is By.CSS_SELECTOR
    assert converted.frame.selector == ".css"
    assert converted.frame.shadow is None
    assert converted.frame.frame is None
