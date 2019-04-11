import pytest

from applitools.common import BrowserType, DeviceName, SeleniumConfiguration, logger
from applitools.common.visual_grid import (
    ChromeEmulationInfo,
    EmulationDevice,
    ScreenOrientation,
)
from applitools.selenium import Target

logger.set_logger(logger.StdoutLogger())


@pytest.fixture
def sel_config(request, batch_info):
    test_page_url = request.node.get_closest_marker("test_page_url").args[0]

    conf = SeleniumConfiguration()
    conf.test_name = "VG hello world - {}".format(test_page_url)
    conf.app_name = "VG hello world"
    conf.batch = batch_info
    conf.baseline_env_name = "michael"
    conf.add_browser(800, 600, BrowserType.CHROME)
    conf.add_browser(700, 500, BrowserType.CHROME)
    conf.add_browser(1600, 1200, BrowserType.CHROME)
    conf.add_browser(1280, 1024, BrowserType.CHROME)
    conf.add_browser(1280, 1024, BrowserType.EDGE)
    conf.add_device_emulation(DeviceName.iPhone_4)
    conf.add_device_emulation(DeviceName.iPhone_X)
    conf.add_device_emulation(DeviceName.Nexus_10, ScreenOrientation.LANDSCAPE)
    return conf


@pytest.mark.test_page_url("https://google.com")
@pytest.mark.app_name("Michael's App name")
@pytest.mark.test_name(" michael test name")
def test_emulation(eyes_vg, request):
    test_page_url = request.node.get_closest_marker("test_page_url").args[0]
    eyes_vg.check("Step1 - " + test_page_url, Target.window().send_dom())
    # eyes_vg.check("Step2 - " + test_page_url, Target.window().fully(False).send_dom())
