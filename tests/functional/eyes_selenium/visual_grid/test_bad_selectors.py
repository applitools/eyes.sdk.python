import pytest
from selenium.common.exceptions import NoSuchElementException

from applitools.selenium import Eyes, Target


def test_check_region_with_bad_selector(driver, eyes_runner):
    eyes = Eyes(eyes_runner)
    driver.get("https://applitools.github.io/demo/TestPages/VisualGridTestPage/")
    eyes.open(
        driver,
        "Applitools Eyes Python SDK",
        "TestCheckRegionWithBadSelector_VG",
        dict(width=1200, height=800),
    )
    with pytest.raises(NoSuchElementException):
        eyes.check_region("#element_that_does_not_exist")
        eyes.close_async()
        eyes_runner.get_all_test_results()


def test_check_region_with_bad_ignore_selector(driver, eyes):
    driver.get("https://applitools.github.io/demo/TestPages/VisualGridTestPage/")
    eyes.open(
        driver, "Applitools Eyes Python SDK", "TestCheckRegionWithBadIgnoreSelector_VG"
    )
    eyes.check(
        "",
        Target.window()
        .ignore("body>p:nth-of-type(" "14)")
        .before_render_screenshot_hook(
            "var p = document.querySelector('body>p:nth-of-type(14)'); p.parentNode.removeChild(p);"
        ),
    )


def test_check_region_with_bad_selector_before_valid_check(driver, eyes):
    driver.get("https://applitools.github.io/demo/TestPages/VisualGridTestPage/")
    eyes.open(
        driver,
        "Applitools Eyes Python SDK",
        "TestCheckRegionWithBadSelectorBeforeValidCheck_VG",
    )
    with pytest.raises(NoSuchElementException):
        eyes.check_region("#element_that_does_not_exist")
        driver.find_element_by_id("centred").click()
        eyes.check_region("#modal-content")

        eyes.close_async()
