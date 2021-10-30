import pytest
from selenium.common.exceptions import NoSuchElementException

from applitools.selenium import Eyes, Target


@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/VisualGridTestPage/"
)
def test_check_region_with_bad_selector(chrome_driver, vg_runner):
    eyes = Eyes(vg_runner)
    eyes.open(
        chrome_driver,
        "Applitools Eyes Python SDK",
        "TestCheckRegionWithBadSelector_VG",
        dict(width=1200, height=800),
    )
    with pytest.raises(NoSuchElementException):
        eyes.check_region("#element_that_does_not_exist")
        eyes.close_async()
        vg_runner.get_all_test_results()


@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/VisualGridTestPage/"
)
def test_check_region_with_bad_ignore_selector(chrome_driver, vg_runner):
    eyes = Eyes(vg_runner)
    eyes.open(
        chrome_driver,
        "Applitools Eyes Python SDK",
        "TestCheckRegionWithBadIgnoreSelector_VG",
    )
    eyes.check(
        "",
        Target.window()
        .ignore("body>p:nth-of-type(" "14)")
        .before_render_screenshot_hook(
            "var p = document.querySelector('body>p:nth-of-type(14)'); p.parentNode.removeChild(p);"
        ),
    )
    eyes.close()
    vg_runner.get_all_test_results()


@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/VisualGridTestPage/"
)
def test_check_region_with_bad_selector_before_valid_check(chrome_driver, vg_runner):
    eyes = Eyes(vg_runner)
    eyes.open(
        chrome_driver,
        "Applitools Eyes Python SDK",
        "TestCheckRegionWithBadSelectorBeforeValidCheck_VG",
    )
    with pytest.raises(NoSuchElementException):
        eyes.check_region("#element_that_does_not_exist")
        chrome_driver.find_element_by_id("centred").click()
        eyes.check_region("#modal-content")

        eyes.close_async()
        vg_runner.get_all_test_results()
