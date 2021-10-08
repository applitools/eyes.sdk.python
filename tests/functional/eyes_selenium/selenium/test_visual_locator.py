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
    eyes.close(False)

    assert len(result) == 1
    assert result["applitools_title"][0] == Region(3, 19, 158, 38)
