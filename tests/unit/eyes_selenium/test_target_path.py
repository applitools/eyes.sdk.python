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


class DummyElement(object):
    def __init__(self, id_):
        self._id = id_

    def __repr__(self):
        return "DummyElement({!r})".format(self._id)


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
    assert path.value.element._id == 1
    assert path.parent is None


def test_target_path_shadow_element():
    path = TargetPath.shadow(DummyElement(1))

    assert type(path) is ShadowDomLocator
    assert type(path.value) is ElementReference
    assert path.value.element._id == 1
    assert path.parent is None


def test_target_path_region_element():
    path = TargetPath.region(DummyElement(1))

    assert type(path) is RegionLocator
    assert type(path.value) is ElementReference
    assert path.value.element._id == 1
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

    assert repr(path) == "TargetPath.region(DummyElement(1))"


def test_target_path_shadow_css_repr():
    path = TargetPath.shadow(".css")

    assert repr(path) == "TargetPath.shadow('.css')"


def test_target_path_shadow_xpath_repr():
    path = TargetPath.shadow(By.XPATH, "//x")

    assert repr(path) == "TargetPath.shadow(By.XPATH, '//x')"


def test_target_path_shadow_element_repr():
    path = TargetPath.shadow(DummyElement(1))

    assert repr(path) == "TargetPath.shadow(DummyElement(1))"


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

    assert repr(path) == "TargetPath.frame(DummyElement(1))"


def test_target_path_shadow_css_region_css_repr():
    path = TargetPath.shadow("#shadow").region(".region")

    assert repr(path) == "TargetPath.shadow('#shadow').region('.region')"


def test_target_path_frame_shadow_region_repr():
    path = TargetPath.frame(1).shadow("#shadow").region(".region")

    assert repr(path) == "TargetPath.frame(1).shadow('#shadow').region('.region')"


def test_target_path_frame_element_shadow_region_repr():
    path = TargetPath.frame(DummyElement(1)).shadow("#").region(".")

    assert repr(path) == "TargetPath.frame(DummyElement(1)).shadow('#').region('.')"


def test_target_path_region_eq():
    assert TargetPath.region(".css") == TargetPath.region(".css")
    assert TargetPath.region(".css") != TargetPath.region("#id")


def test_target_path_frame_region_eq():
    assert TargetPath.frame(1).region(".css") == TargetPath.frame(1).region(".css")
    assert TargetPath.frame(1).region(".css") != TargetPath.frame(1).region("#id")
    assert TargetPath.frame(1).region(".css") != TargetPath.frame(2).region(".css")


def test_target_path_to_dict_region_by_css():
    converted = TargetPath.region(".css").to_dict(True)

    assert converted == {"type": "css selector", "selector": ".css"}


def test_target_path_to_dict_region_element():
    converted = TargetPath.region(DummyElement("1")).to_dict(True)

    assert converted == {"elementId": "1"}


def test_target_path_to_dict_shadow_by_css():
    converted = TargetPath.shadow(".css").to_dict(True)

    assert converted == {"type": "css selector", "selector": ".css"}


def test_target_path_to_dict_shadow_by_css_region_by_css():
    converted = TargetPath.shadow("#s").region(".css").to_dict(True)

    assert converted == {
        "type": "css selector",
        "selector": "#s",
        "shadow": {"type": "css selector", "selector": ".css"},
    }


def test_target_path_to_dict_shadow_by_xpath_shadow_by_css_region_by_css():
    converted = (
        TargetPath.shadow(By.XPATH, "//x").shadow("#s").region(".css").to_dict(True)
    )

    assert converted == {
        "type": "xpath",
        "selector": "//x",
        "shadow": {
            "type": "css selector",
            "selector": "#s",
            "shadow": {
                "type": "css selector",
                "selector": ".css",
            },
        },
    }


def test_target_path_to_dict_frame_by_css_region_by_css():
    converted = TargetPath.frame(By.CSS_SELECTOR, "#s").region(".css").to_dict(True)

    assert converted == {
        "type": "css selector",
        "selector": "#s",
        "frame": {"type": "css selector", "selector": ".css"},
    }


def test_target_path_to_dict_selenium_region_by_id():
    converted = TargetPath.region(By.ID, "id").to_dict(True)

    assert converted == {"type": "css selector", "selector": '[id="id"]'}


def test_target_path_to_dict_selenium_region_by_tag_name():
    converted = TargetPath.region(By.TAG_NAME, "tag").to_dict(True)

    assert converted == {"type": "css selector", "selector": "tag"}


def test_target_path_to_dict_selenium_region_by_class_name():
    converted = TargetPath.region(By.CLASS_NAME, "class").to_dict(True)

    assert converted == {"type": "css selector", "selector": ".class"}


def test_target_path_to_dict_selenium_region_by_name():
    converted = TargetPath.region(By.NAME, "name").to_dict(True)

    assert converted == {"type": "css selector", "selector": '[name="name"]'}


def test_target_path_to_dict_appium_region_by_id():
    converted = TargetPath.region(By.ID, "id").to_dict(False)

    assert converted == {"type": "id", "selector": "id"}


def test_target_path_to_dict_appium_region_by_tag_name():
    converted = TargetPath.region(By.TAG_NAME, "tag").to_dict(False)

    assert converted == {"type": "tag name", "selector": "tag"}


def test_target_path_to_dict_appium_region_by_class_name():
    converted = TargetPath.region(By.CLASS_NAME, "class").to_dict(False)

    assert converted == {"type": "class name", "selector": "class"}


def test_target_path_to_dict_appium_region_by_name():
    converted = TargetPath.region(By.NAME, "name").to_dict(False)

    assert converted == {"type": "name", "selector": "name"}
