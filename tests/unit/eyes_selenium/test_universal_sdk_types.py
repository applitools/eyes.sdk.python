from selenium.webdriver.common.by import By

from applitools.selenium.fluent.target_path import TargetPath
from applitools.selenium.universal_sdk_types import TransformedSelector


def test_transformed_selector_convert_region_by_css():
    converted = TransformedSelector.convert(True, TargetPath.region(".css"))

    assert converted.type is By.CSS_SELECTOR
    assert converted.selector == ".css"
    assert converted.frame is None
    assert converted.shadow is None


def test_transformed_selector_convert_shadow_by_css_region_by_css():
    converted = TransformedSelector.convert(
        True, TargetPath.shadow("#s").region(".css")
    )

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
        True, TargetPath.shadow(By.XPATH, "//x").shadow("#s").region(".css")
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
        True, TargetPath.frame(By.CSS_SELECTOR, "#s").region(".css")
    )

    assert converted.type is By.CSS_SELECTOR
    assert converted.selector == "#s"
    assert converted.shadow is None
    assert type(converted.frame) is TransformedSelector
    assert converted.frame.type is By.CSS_SELECTOR
    assert converted.frame.selector == ".css"
    assert converted.frame.shadow is None
    assert converted.frame.frame is None


def test_transformed_selector_convert_target_by_id():
    converted = TransformedSelector.convert(True, TargetPath.region(By.ID, "id"))

    assert converted.type is By.CSS_SELECTOR
    assert converted.selector == '[id="id"]'
    assert converted.shadow is None
    assert converted.frame is None


def test_transformed_selector_convert_target_by_tag_name():
    converted = TransformedSelector.convert(True, TargetPath.region(By.TAG_NAME, "tag"))

    assert converted.type is By.CSS_SELECTOR
    assert converted.selector == "tag"
    assert converted.shadow is None
    assert converted.frame is None


def test_transformed_selector_convert_target_by_class_name():
    converted = TransformedSelector.convert(
        True, TargetPath.region(By.CLASS_NAME, "class")
    )

    assert converted.type is By.CSS_SELECTOR
    assert converted.selector == ".class"
    assert converted.shadow is None
    assert converted.frame is None


def test_transformed_selector_convert_target_by_name():
    converted = TransformedSelector.convert(True, TargetPath.region(By.NAME, "name"))

    assert converted.type is By.CSS_SELECTOR
    assert converted.selector == '[name="name"]'
    assert converted.shadow is None
    assert converted.frame is None


def test_appium_transformed_selector_convert_target_by_id():
    converted = TransformedSelector.convert(False, TargetPath.region(By.ID, "id"))

    assert converted.type is By.ID
    assert converted.selector == "id"
    assert converted.shadow is None
    assert converted.frame is None


def test_appium_transformed_selector_convert_target_by_tag_name():
    converted = TransformedSelector.convert(
        False, TargetPath.region(By.TAG_NAME, "tag")
    )

    assert converted.type is By.TAG_NAME
    assert converted.selector == "tag"
    assert converted.shadow is None
    assert converted.frame is None


def test_appium_transformed_selector_convert_target_by_class_name():
    converted = TransformedSelector.convert(
        False, TargetPath.region(By.CLASS_NAME, "class")
    )

    assert converted.type is By.CLASS_NAME
    assert converted.selector == "class"
    assert converted.shadow is None
    assert converted.frame is None


def test_appium_transformed_selector_convert_target_by_name():
    converted = TransformedSelector.convert(False, TargetPath.region(By.NAME, "name"))

    assert converted.type is By.NAME
    assert converted.selector == "name"
    assert converted.shadow is None
    assert converted.frame is None
