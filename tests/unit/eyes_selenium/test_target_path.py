from collections import namedtuple

from selenium.webdriver.common.by import By

from applitools.selenium.fluent.target_path import (
    ElementReference,
    ElementSelector,
    FrameLocator,
    FrameSelector,
    RegionLocator,
    ShadowDomLocator,
    TargetPath,
)

DummyElement = namedtuple("DummyElement", "id")


def test_target_path_region_by_css():
    path = TargetPath.region(".css")

    assert type(path) is RegionLocator
    assert type(path.value) is ElementSelector
    assert path.value.by is By.CSS_SELECTOR
    assert path.value.selector == ".css"
    assert path.parent is None


def test_target_path_region_by_xpath():
    path = TargetPath.region(By.XPATH, "//x")

    assert type(path) is RegionLocator
    assert type(path.value) is ElementSelector
    assert path.value.by is By.XPATH
    assert path.value.selector == "//x"
    assert path.parent is None


def test_target_path_frame_by_name_or_id():
    path = TargetPath.frame("name_or_id")

    assert type(path) is FrameLocator
    assert type(path.value) is FrameSelector
    assert path.value.number_or_id_or_name == "name_or_id"
    assert path.parent is None


def test_target_path_frame_by_number():
    path = TargetPath.frame(1)

    assert type(path) is FrameLocator
    assert type(path.value) is FrameSelector
    assert path.value.number_or_id_or_name == 1
    assert path.parent is None


def test_target_path_frame_by_css_selector():
    path = TargetPath.frame(By.CSS_SELECTOR, ".css")

    assert type(path) is FrameLocator
    assert type(path.value) is ElementSelector
    assert path.value.by is By.CSS_SELECTOR
    assert path.value.selector == ".css"
    assert path.parent is None


def test_target_path_shadow_by_css():
    path = TargetPath.shadow(".css")

    assert type(path) is ShadowDomLocator
    assert type(path.value) is ElementSelector
    assert path.value.by is By.CSS_SELECTOR
    assert path.value.selector == ".css"
    assert path.parent is None


def test_target_path_shadow_by_xpath():
    path = TargetPath.shadow(By.XPATH, "//x")

    assert type(path) is ShadowDomLocator
    assert type(path.value) is ElementSelector
    assert path.value.by is By.XPATH
    assert path.value.selector == "//x"
    assert path.parent is None


def test_target_path_frame_element():
    path = TargetPath.frame(DummyElement(1))

    assert type(path) is FrameLocator
    assert type(path.value) is ElementReference
    assert path.value.element.id == 1
    assert path.parent is None


def test_target_path_shadow_element():
    path = TargetPath.shadow(DummyElement(1))

    assert type(path) is ShadowDomLocator
    assert type(path.value) is ElementReference
    assert path.value.element.id == 1
    assert path.parent is None


def test_target_path_region_element():
    path = TargetPath.region(DummyElement(1))

    assert type(path) is RegionLocator
    assert type(path.value) is ElementReference
    assert path.value.element.id == 1
    assert path.parent is None


def test_target_region_within_frame():
    path = TargetPath.frame(1).region(".css")

    assert type(path) is RegionLocator
    assert type(path.value) is ElementSelector
    assert path.value.by is By.CSS_SELECTOR
    assert path.value.selector == ".css"
    assert type(path.parent) is FrameLocator
    assert type(path.parent.value) is FrameSelector
    assert path.parent.value.number_or_id_or_name == 1
    assert path.parent.parent is None


def test_target_path_region_css_repr():
    path = TargetPath.region(".css")

    assert repr(path) == "TargetPath.region('.css')"


def test_target_path_region_xpath_repr():
    path = TargetPath.region(By.XPATH, "//x")

    assert repr(path) == "TargetPath.region(By.XPATH, '//x')"


def test_target_path_region_element_repr():
    path = TargetPath.region(DummyElement(1))

    assert repr(path) == "TargetPath.region(DummyElement(id=1))"


def test_target_path_shadow_css_repr():
    path = TargetPath.shadow(".css")

    assert repr(path) == "TargetPath.shadow('.css')"


def test_target_path_shadow_xpath_repr():
    path = TargetPath.shadow(By.XPATH, "//x")

    assert repr(path) == "TargetPath.shadow(By.XPATH, '//x')"


def test_target_path_shadow_element_repr():
    path = TargetPath.shadow(DummyElement(1))

    assert repr(path) == "TargetPath.shadow(DummyElement(id=1))"


def test_target_path_frame_number_repr():
    path = TargetPath.frame(1)

    assert repr(path) == "TargetPath.frame(1)"


def test_target_path_frame_name_repr():
    path = TargetPath.frame("frame")

    assert repr(path) == "TargetPath.frame('frame')"


def test_target_path_frame_css_repr():
    path = TargetPath.frame(By.CSS_SELECTOR, ".css")

    assert repr(path) == "TargetPath.frame(By.CSS_SELECTOR, '.css')"


def test_target_path_frame_element_repr():
    path = TargetPath.frame(DummyElement(1))

    assert repr(path) == "TargetPath.frame(DummyElement(id=1))"


def test_target_path_shadow_css_region_css_repr():
    path = TargetPath.shadow("#shadow").region(".region")

    assert repr(path) == "TargetPath.shadow('#shadow').region('.region')"


def test_target_path_frame_shadow_region_repr():
    path = TargetPath.frame(1).shadow("#shadow").region(".region")

    assert repr(path) == "TargetPath.frame(1).shadow('#shadow').region('.region')"


def test_target_path_frame_element_shadow_region_repr():
    path = TargetPath.frame(DummyElement(2)).shadow("#").region(".")

    assert repr(path) == "TargetPath.frame(DummyElement(id=2)).shadow('#').region('.')"


def test_target_path_region_eq():
    assert TargetPath.region(".css") == TargetPath.region(".css")
    assert TargetPath.region(".css") != TargetPath.region("#id")


def test_target_path_frame_region_eq():
    assert TargetPath.frame(1).region(".css") == TargetPath.frame(1).region(".css")
    assert TargetPath.frame(1).region(".css") != TargetPath.frame(1).region("#id")
    assert TargetPath.frame(1).region(".css") != TargetPath.frame(2).region(".css")
