import pytest

from applitools.common import (
    BatchInfo,
    BrowserType,
    DeviceName,
    ScreenOrientation,
    SeleniumConfiguration,
)
from applitools.selenium import Target


@pytest.fixture
def sel_config(request):
    test_page_url = request.node.get_closest_marker("test_page_url").args[0]

    conf = SeleniumConfiguration()
    conf.test_name = "Top 10 websites - {}".format(test_page_url)
    conf.app_name = "Top Ten Sites"
    conf.batch = BatchInfo("TTS - config batch")
    conf.branch_name = "TTS - config branch"
    conf.baseline_env_name = "My Other Env Name"
    conf.add_browser(800, 600, BrowserType.CHROME)
    # conf.add_browser(700, 500, BrowserType.FIREFOX)
    # conf.add_browser(700, 500, BrowserType.IE10)
    # conf.add_browser(700, 500, BrowserType.IE11)
    # conf.add_browser(1600, 1200, BrowserType.CHROME)
    # conf.add_browser(1200, 800, BrowserType.EDGE)
    # conf.add_browser(800, 600, BrowserType.CHROME)
    # conf.add_browser(700, 500, BrowserType.CHROME)
    # conf.add_device_emulation(DeviceName.iPhone_4)
    # conf.add_device_emulation(DeviceName.iPhone_X)
    # conf.add_device_emulation(DeviceName.Nexus_10, ScreenOrientation.LANDSCAPE)
    return conf


@pytest.mark.test_page_url("http://opzharp.ru/")
# @pytest.mark.test_page_url("http://www.sage.co.uk/")
# @pytest.mark.test_page_url("http://allatra.tv/")
@pytest.mark.viewport_size(dict(width=600, height=600))
def test_top_sites(eyes_vg, request):
    test_page_url = request.node.get_closest_marker("test_page_url").args[0]
    eyes_vg.check("Step1 - " + test_page_url, Target.window().send_dom(True))
    eyes_vg.check(
        "Step2 - " + test_page_url, Target.window().fully(False).send_dom(True)
    )
