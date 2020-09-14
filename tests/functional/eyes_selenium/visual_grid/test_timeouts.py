import pytest

from applitools.common import EyesError, RectangleSize
from applitools.selenium import BrowserType, Configuration, DeviceName, Eyes, Target
from applitools.selenium.visual_grid import visual_grid_eyes

original_timeout = -1


@pytest.fixture(autouse=True)
def setup_and_teardown():
    global original_timeout
    original_timeout = visual_grid_eyes.DOM_EXTRACTION_TIMEOUT
    yield
    visual_grid_eyes.DOM_EXTRACTION_TIMEOUT = original_timeout


def test_timeout(driver, vg_runner, batch_info):
    eyes = Eyes(vg_runner)
    driver.get("https://applitools.com/helloworld")
    eyes.batch = batch_info
    eyes.open(
        driver, "Timeout Test", "Visual Grid Timeout Test", RectangleSize(1200, 800)
    )
    eyes.check("", Target.window().with_name("Test"))
    eyes.close()
    vg_runner.get_all_test_results()


def test_timeout2(driver, vg_runner, batch_info):
    visual_grid_eyes.DOM_EXTRACTION_TIMEOUT = 1
    eyes = Eyes(vg_runner)
    driver.get("https://applitools.com/helloworld")
    conf = Configuration(
        batch=batch_info, app_name="Test Timeouts", test_name="Test Timeouts"
    )
    conf.add_browser(800, 600, BrowserType.CHROME)
    conf.add_browser(700, 500, BrowserType.FIREFOX)
    conf.add_browser(600, 400, BrowserType.EDGE)
    conf.add_browser(900, 700, BrowserType.IE_10)
    conf.add_browser(1000, 800, BrowserType.IE_11)
    conf.add_device_emulation(DeviceName.Galaxy_S5)
    conf.add_device_emulation(DeviceName.iPhone6_7_8_Plus)
    conf.add_device_emulation(DeviceName.Laptop_with_HiDPI_screen)
    eyes.configuration = conf
    eyes.open(driver)

    with pytest.raises(EyesError) as e:
        eyes.check("", Target.window().with_name("Test"))
        eyes.close()
        vg_runner.get_all_test_results()
        assert "Domsnapshot Timed out" in str(e)
