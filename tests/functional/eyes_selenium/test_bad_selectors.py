import pytest
from selenium.common.exceptions import NoSuchElementException

from applitools.common import RectangleSize
from applitools.selenium import Eyes, VisualGridRunner


@pytest.fixture
def eyes_runner_class():
    return VisualGridRunner


@pytest.mark.skip("USDK Difference, Element not exists is ignored")
def test_check_region_with_bad_selector(eyes, local_chrome_driver):
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/VisualGridTestPage/"
    )
    eyes.open(
        local_chrome_driver,
        "Applitools Eyes Python SDK",
        "TestCheckRegionWithBadSelector_VG",
        dict(width=1200, height=800),
    )
    with pytest.raises(NoSuchElementException):
        eyes.check_region("#element_that_does_not_exist")


@pytest.mark.skip("USDK Difference, Element not exists is ignored")
def test_check_region_with_bad_selector_before_valid_check(eyes, local_chrome_driver):
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/VisualGridTestPage/"
    )
    eyes.open(
        local_chrome_driver,
        "Applitools Eyes Python SDK",
        "TestCheckRegionWithBadSelectorBeforeValidCheck_VG",
        viewport_size=RectangleSize(800, 600),
    )
    with pytest.raises(NoSuchElementException):
        eyes.check_region("#element_that_does_not_exist")
