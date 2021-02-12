import pytest
from selenium.webdriver.common.by import By

from applitools.common import Region
from applitools.core import TextRegionSettings, VisualLocator
from applitools.selenium import ClassicRunner, Eyes, OCRRegion, VisualGridRunner


@pytest.mark.parametrize("eyes_runner", [ClassicRunner(), VisualGridRunner(1)])
def test_visual_locator(driver, eyes_runner):
    driver.get("https://applitools.github.io/demo/TestPages/FramesTestPage/")
    eyes = Eyes(eyes_runner)
    test_name = "testVisualLocators"
    if isinstance(eyes_runner, VisualGridRunner):
        test_name += "_VG"
    eyes.open(driver, "Applitools Eyes SDK", test_name)

    result = eyes.locate(VisualLocator.name("applitools_title"))
    eyes.close_async()

    assert len(result) == 1
    assert result["applitools_title"][0] == Region(3, 19, 158, 38)


# TODO: Remove after merge of generated tests
@pytest.mark.parametrize("eyes_runner", [ClassicRunner()])
def test_extract_text_regions(driver, eyes_runner):
    driver.get("https://applitools.github.io/demo/TestPages/OCRPage")
    eyes = Eyes(eyes_runner)
    test_name = "testExtractTextRegions"
    if isinstance(eyes_runner, VisualGridRunner):
        test_name += "_VG"

    eyes.open(driver, "Applitools Eyes SDK", test_name)
    patterns = ["header\\d:.+", "\\d\\..+", "nostrud"]
    regions = eyes.extract_text_regions(TextRegionSettings(patterns).ignore_case())

    eyes.close_async()

    assert len(regions) == 3


@pytest.mark.parametrize("eyes_runner", [ClassicRunner()])
def test_extract_text(driver, eyes_runner):
    driver.get("https://applitools.github.io/demo/TestPages/FramesTestPage/")
    eyes = Eyes(eyes_runner)
    test_name = "testExtractText"
    if isinstance(eyes_runner, VisualGridRunner):
        test_name += "_VG"

    eyes.open(driver, "Applitools Eyes SDK", test_name)
    element = driver.find_element_by_css_selector("#overflowing-div")
    text_results = eyes.extract_text(OCRRegion(element))
    assert len(text_results) == 1

    text_results = eyes.extract_text(OCRRegion("#overflowing-div"))
    assert len(text_results) == 1

    text_results = eyes.extract_text(OCRRegion(Region(0, 0, 400, 800)))
    assert len(text_results) == 1

    eyes.close_async()
