import pytest
from selenium.webdriver.common.by import By

from applitools.common import Region
from applitools.core import TextRegionSettings, VisualLocator
from applitools.selenium import ClassicRunner, Eyes, VisualGridRunner
from applitools.selenium.text_regions import OCRRegion


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
    regions = eyes.extract_text_regions(
        TextRegionSettings(patterns[0], patterns[1])
        .ignore_case()
        .patterns([patterns[2]])
    )

    eyes.close_async()

    assert len(regions) == 3
    assert regions[patterns[0]][0].text == "Header1: Hello world!"
    assert regions[patterns[0]][1].text == "Header3: HEllQ w@rld!!"

    assert regions[patterns[1]][1].text == "1. One"
    assert regions[patterns[1]][2].text == "2. Two"
    assert regions[patterns[1]][3].text == "3. Three"
    assert regions[patterns[1]][4].text == "4. Four"

    assert (
        regions[patterns[2]][0].text
        == "Incididum minim ad occaecat mollit sint elit ipsum. Consectetur eiusmod sint officia labore elit nostrud mollit eiusmod"
    )


@pytest.mark.parametrize("eyes_runner", [ClassicRunner()])
def test_extract_text(driver, eyes_runner):
    driver.get("https://applitools.github.io/demo/TestPages/FramesTestPage/")
    eyes = Eyes(eyes_runner)
    test_name = "testExtractText"
    if isinstance(eyes_runner, VisualGridRunner):
        test_name += "_VG"
    expected = [
        """ttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt
BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG
HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK
LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLI
MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN
OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO"""
    ]
    eyes.open(driver, "Applitools Eyes SDK", test_name)
    element = driver.find_element_by_css_selector("#overflowing-div")
    text_results = eyes.extract_text(OCRRegion(element))
    assert len(text_results) == 1
    assert text_results == expected

    text_results = eyes.extract_text(OCRRegion([By.CSS_SELECTOR, "#overflowing-div"]))
    assert len(text_results) == 1
    assert text_results == expected

    text_results = eyes.extract_text(OCRRegion(Region(0, 0, 400, 800)))
    assert len(text_results) == 1

    eyes.close_async()
