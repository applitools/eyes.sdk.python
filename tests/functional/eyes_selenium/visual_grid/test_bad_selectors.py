import pytest
from selenium.common.exceptions import NoSuchElementException

from applitools.common import RectangleSize
from applitools.selenium import Eyes, Target


@pytest.mark.skip("USDK Difference, Element not exists is ignored")
def test_check_region_with_bad_selector(driver, vg_runner):
    eyes = Eyes(vg_runner)
    driver.get("https://applitools.github.io/demo/TestPages/VisualGridTestPage/")
    eyes.open(
        driver,
        "Applitools Eyes Python SDK",
        "TestCheckRegionWithBadSelector_VG",
        dict(width=1200, height=800),
    )
    with pytest.raises(NoSuchElementException):
        eyes.check_region("#element_that_does_not_exist")


@pytest.mark.skip("USDK Difference, Element not exists is ignored")
def test_check_region_with_bad_selector_before_valid_check(driver, vg_runner):
    eyes = Eyes(vg_runner)
    driver.get("https://applitools.github.io/demo/TestPages/VisualGridTestPage/")
    eyes.open(
        driver,
        "Applitools Eyes Python SDK",
        "TestCheckRegionWithBadSelectorBeforeValidCheck_VG",
        viewport_size=RectangleSize(800, 600),
    )
    with pytest.raises(NoSuchElementException):
        eyes.check_region("#element_that_does_not_exist")
