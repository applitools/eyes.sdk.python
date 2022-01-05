from selenium.webdriver.common.by import By

from applitools.selenium.fluent.target_path import (
    FrameLocator,
    RegionLocator,
    ShadowDomLocator,
    TargetPath,
)


def test_target_path_region_by_css():
    path = TargetPath.region(".css")

    assert type(path) is RegionLocator
    assert path.by is By.CSS_SELECTOR
    assert path.selector == ".css"
    assert path.parent is None


def test_target_path_region_by_xpath():
    path = TargetPath.region(By.XPATH, "//x")

    assert type(path) is RegionLocator
    assert path.by is By.XPATH
    assert path.selector == "//x"
    assert path.parent is None


def test_target_path_frame_by_name_or_id():
    path = TargetPath.frame("name_or_id")

    assert type(path) is FrameLocator
    assert path.by is None
    assert path.selector is None
    assert path.number_or_id_or_name == "name_or_id"
    assert path.parent is None


def test_target_path_frame_by_number():
    path = TargetPath.frame(1)

    assert type(path) is FrameLocator
    assert path.by is None
    assert path.selector is None
    assert path.number_or_id_or_name == 1
    assert path.parent is None


def test_target_path_frame_by_css_selector():
    path = TargetPath.frame(By.CSS_SELECTOR, ".css")

    assert type(path) is FrameLocator
    assert path.by is By.CSS_SELECTOR
    assert path.selector == ".css"
    assert path.number_or_id_or_name is None
    assert path.parent is None


def test_target_path_shadow_dom_by_css():
    path = TargetPath.shadow_dom(".css")

    assert type(path) is ShadowDomLocator
    assert path.by is By.CSS_SELECTOR
    assert path.selector == ".css"
    assert path.parent is None


def test_target_path_shadow_dom_by_xpath():
    path = TargetPath.shadow_dom(By.XPATH, "//x")

    assert type(path) is ShadowDomLocator
    assert path.by is By.XPATH
    assert path.selector == "//x"
    assert path.parent is None


def test_target_region_within_frame():
    path = TargetPath.frame(1).region(".css")

    assert type(path) is RegionLocator
    assert path.by is By.CSS_SELECTOR
    assert path.selector == ".css"
    assert type(path.parent) is FrameLocator
    assert path.parent.number_or_id_or_name == 1


def test_target_path_region_css_repr():
    path = TargetPath.region(".css")

    assert repr(path) == "TargetPath.region('.css')"


def test_target_path_region_xpath_repr():
    path = TargetPath.region(By.XPATH, "//x")

    assert repr(path) == "TargetPath.region(By.XPATH, '//x')"


def test_target_path_shadow_dom_css_repr():
    path = TargetPath.shadow_dom(".css")

    assert repr(path) == "TargetPath.shadow_dom('.css')"


def test_target_path_shadow_dom_xpath_repr():
    path = TargetPath.shadow_dom(By.XPATH, "//x")

    assert repr(path) == "TargetPath.shadow_dom(By.XPATH, '//x')"


def test_target_path_frame_number_repr():
    path = TargetPath.frame(1)

    assert repr(path) == "TargetPath.frame(1)"


def test_target_path_frame_name_repr():
    path = TargetPath.frame("frame")

    assert repr(path) == "TargetPath.frame('frame')"


def test_target_path_frame_css_repr():
    path = TargetPath.frame(By.CSS_SELECTOR, ".css")

    assert repr(path) == "TargetPath.frame(By.CSS_SELECTOR, '.css')"


def test_target_path_shadow_dom_css_region_css_repr():
    path = TargetPath.shadow_dom("#shadow").region(".region")

    assert repr(path) == "TargetPath.shadow_dom('#shadow').region('.region')"


def test_target_path_frame_shadow_dom_region_repr():
    path = TargetPath.frame(1).shadow_dom("#shadow").region(".region")

    assert repr(path) == "TargetPath.frame(1).shadow_dom('#shadow').region('.region')"


def test_target_path_region_eq():
    assert TargetPath.region(".css") == TargetPath.region(".css")
    assert TargetPath.region(".css") != TargetPath.region("#id")


def test_target_path_frame_region_eq():
    assert TargetPath.frame(1).region(".css") == TargetPath.frame(1).region(".css")
    assert TargetPath.frame(1).region(".css") != TargetPath.frame(1).region("#id")
    assert TargetPath.frame(1).region(".css") != TargetPath.frame(2).region(".css")
