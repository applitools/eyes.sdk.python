from applitools.common import Region
from applitools.core import VisualLocator
from applitools.selenium import Eyes, ClassicRunner


def test_visual_locator(driver, eyes_class, eyes_runner):
    driver.get("https://applitools.github.io/demo/TestPages/FramesTestPage/")
    eyes = Eyes(ClassicRunner())
    eyes.open(driver, "Applitools Eyes SDK", "testVisualLocators")

    result = eyes.locate(VisualLocator.name("applitools_title"))
    eyes.close_async()

    assert len(result) == 1
    assert result["applitools_title"][0] == Region(2, 11, 173, 58)
