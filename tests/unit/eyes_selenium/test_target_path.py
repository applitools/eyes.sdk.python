from selenium.webdriver.common.by import By

from applitools.selenium.fluent.target_path import TargetPath


def test_element_path():
    path = TargetPath(By.ID, "i")

    assert path.by is By.ID
    assert path.selector == "i"
    assert path.shadow_path is None


def test_element_path_implicit():
    path = TargetPath("c")

    assert path.by is By.CSS_SELECTOR
    assert path.selector == "c"
    assert path.shadow_path is None


def test_element_path_with_fluent_shadow():
    path = TargetPath(By.ID, "i").shadow(By.CSS_SELECTOR, "c")

    assert path.by is By.ID
    assert path.selector == "i"
    assert path.shadow_path.by is By.CSS_SELECTOR
    assert path.shadow_path.selector == "c"
    assert path.shadow_path.shadow_path is None


def test_element_comparison():
    assert TargetPath(By.ID, "i") == TargetPath(By.ID, "i")
    assert TargetPath(By.ID, "i") != TargetPath(By.ID, "o")
    assert TargetPath(By.ID, "i") != TargetPath(By.ID, "i").shadow(By.ID, "i")


def test_target_path_id_with_implicit_css_shadow():
    path = TargetPath(By.ID, "i").shadow("c")

    assert path == TargetPath(By.ID, "i", TargetPath(By.CSS_SELECTOR, "c"))  # noqa


def test_target_path_3_level_implicit_css_shadows():
    path = TargetPath("c").shadow("cc").shadow("ccc")

    assert path == TargetPath(  # noqa
        By.CSS_SELECTOR,
        "c",
        TargetPath(  # noqa
            By.CSS_SELECTOR,
            "cc",
            TargetPath(
                By.CSS_SELECTOR,
                "ccc",
            ),
        ),
    )


def test_target_path_id_with_two_level_shadows():
    path = TargetPath(By.ID, "i").shadow(By.XPATH, "x").shadow(By.LINK_TEXT, "l")

    assert path == TargetPath(  # noqa
        By.ID,
        "i",
        TargetPath(  # noqa
            By.XPATH,
            "x",
            TargetPath(
                By.LINK_TEXT,
                "l",
            ),
        ),
    )


def test_target_path_css_with_explicit_link_in_shadow():
    path = TargetPath("c").shadow(By.LINK_TEXT, "l")

    assert path == TargetPath(  # noqa
        By.CSS_SELECTOR, "c", TargetPath(By.LINK_TEXT, "l")
    )


def test_target_path_name_repr():
    path = TargetPath(By.NAME, "n")

    assert repr(path) == "TargetPath(By.NAME, 'n')"


def test_target_path_css_repr():
    path = TargetPath("c")

    assert repr(path) == "TargetPath('c')"


def test_target_path_with_one_level_shadow_repr():
    path = TargetPath("c").shadow("cc")

    assert repr(path) == "TargetPath('c').shadow('cc')"


def test_target_path_name_with_one_level_shadow_link_text_repr():
    path = TargetPath(By.NAME, "n").shadow(By.LINK_TEXT, "l")

    assert repr(path) == "TargetPath(By.NAME, 'n').shadow(By.LINK_TEXT, 'l')"


def test_target_path_immutable():
    root = TargetPath("root")
    path1 = root.shadow("s1")
    path2 = root.shadow("s2")

    assert root == TargetPath("root")
    assert path1 == TargetPath("root").shadow("s1")
    assert path2 == TargetPath("root").shadow("s2")
