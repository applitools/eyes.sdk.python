from selenium.webdriver.common.by import By

from applitools.selenium.fluent.target_path import ElementPath, TargetPath


def test_element_path():
    path = ElementPath(By.ID, "i")

    assert path.by is By.ID
    assert path.selector == "i"
    assert path.shadow_path is None


def test_element_path_with_init_shadow():
    path = ElementPath(By.ID, "i", ElementPath(By.CSS_SELECTOR, "c"))

    assert path.by is By.ID
    assert path.selector == "i"
    assert path.shadow_path.by is By.CSS_SELECTOR
    assert path.shadow_path.selector == "c"
    assert path.shadow_path.shadow_path is None


def test_element_path_with_fluent_shadow():
    path = ElementPath(By.ID, "i").shadow([By.CSS_SELECTOR, "c"])

    assert path.by is By.ID
    assert path.selector == "i"
    assert path.shadow_path.by is By.CSS_SELECTOR
    assert path.shadow_path.selector == "c"
    assert path.shadow_path.shadow_path is None


def test_element_comparison():
    assert ElementPath(By.ID, "i") == ElementPath(By.ID, "i")
    assert ElementPath(By.ID, "i") != ElementPath(By.ID, "o")
    assert ElementPath(By.ID, "i") != ElementPath(By.ID, "i", ElementPath(By.ID, "i"))


def test_target_path_id():
    path = TargetPath.id("a")

    assert path.by is By.ID
    assert path.selector == "a"
    assert path.shadow_path is None


def test_target_path_xpath():
    path = TargetPath.xpath("x")

    assert path.by is By.XPATH
    assert path.selector == "x"
    assert path.shadow_path is None


def test_target_path_link_text():
    path = TargetPath.link_text("l")

    assert path.by is By.LINK_TEXT
    assert path.selector == "l"
    assert path.shadow_path is None


def test_target_path_partial_link_text():
    path = TargetPath.partial_link_text("p")

    assert path.by is By.PARTIAL_LINK_TEXT
    assert path.selector == "p"
    assert path.shadow_path is None


def test_target_path_name():
    path = TargetPath.name("n")

    assert path.by is By.NAME
    assert path.selector == "n"
    assert path.shadow_path is None


def test_target_path_tag_name():
    path = TargetPath.tag_name("t")

    assert path.by is By.TAG_NAME
    assert path.selector == "t"
    assert path.shadow_path is None


def test_target_path_class_name():
    path = TargetPath.class_name("c")

    assert path.by is By.CLASS_NAME
    assert path.selector == "c"
    assert path.shadow_path is None


def test_target_path_css_selector():
    path = TargetPath.css_selector("c")

    assert path.by is By.CSS_SELECTOR
    assert path.selector == "c"
    assert path.shadow_path is None


def test_target_path_id_with_implicit_css_shadow():
    path = TargetPath.id("i").shadow("c")

    assert path == ElementPath(By.ID, "i", ElementPath(By.CSS_SELECTOR, "c"))


def test_target_path_id_with_two_level_implicit_css_shadow():
    path = TargetPath.id("i").shadow("c").shadow("cc")

    assert path == ElementPath(
        By.ID,
        "i",
        ElementPath(
            By.CSS_SELECTOR,
            "c",
            ElementPath(
                By.CSS_SELECTOR,
                "cc",
            ),
        ),
    )


def test_target_path_name_with_explicit_link_in_shadow():
    path = TargetPath.name("n").shadow([By.LINK_TEXT, "l"])

    assert path == ElementPath(By.NAME, "n", ElementPath(By.LINK_TEXT, "l"))


def test_target_path_repr():
    path = TargetPath.name("n")

    assert repr(path) == "ElementPath(By.NAME, 'n')"


def test_target_path_with_one_level_shadow_repr():
    path = TargetPath.name("n").shadow("c")

    assert repr(path) == "ElementPath(By.NAME, 'n', ElementPath(By.CSS_SELECTOR, 'c'))"
