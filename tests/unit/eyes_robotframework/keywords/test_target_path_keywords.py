import pytest
from mock import Mock

from applitools.selenium import TargetPath
from EyesLibrary import TargetPathKeywords


@pytest.fixture()
def target_path_keyword(eyes_library_with_selenium):
    return TargetPathKeywords(eyes_library_with_selenium)


def test_shadow(target_path_keyword, css_selector, raw_css_selector, web_element):
    res = TargetPath().shadow(raw_css_selector)
    assert res == target_path_keyword.shadow_by_selector(css_selector)

    res = TargetPath().shadow(web_element)
    assert res == target_path_keyword.shadow_by_element(web_element)


def test_shadow_region(
    target_path_keyword, css_selector, raw_css_selector, web_element
):
    res = TargetPath().shadow(raw_css_selector).region(web_element)
    _target_path = target_path_keyword.shadow_by_selector(css_selector)
    assert res == target_path_keyword.region_by_element(web_element, _target_path)


def test_region_before_shadow_raise_exeption(
    target_path_keyword, css_selector, web_element
):
    with pytest.raises(ValueError):
        target_path_keyword.region_by_element(web_element)
    with pytest.raises(ValueError):
        target_path_keyword.region_by_selector(css_selector)
