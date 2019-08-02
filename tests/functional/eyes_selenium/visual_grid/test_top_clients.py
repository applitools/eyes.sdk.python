import pytest
from applitools.selenium import (
    BatchInfo,
    BrowserType,
    Configuration,
    DeviceName,
    ScreenOrientation,
    Target,
)


@pytest.fixture
def sel_config(test_page_url):
    conf = Configuration()
    conf.test_name = "Top 10 websites - {}".format(test_page_url)
    conf.app_name = "Top Ten Sites"
    conf.batch = BatchInfo("Python | VisualGrid")
    conf.branch_name = "TTS - config branch"
    conf.add_browser(800, 600, BrowserType.CHROME)
    conf.add_browser(700, 500, BrowserType.FIREFOX)
    # conf.add_browser(700, 500, BrowserType.IE_10)
    # conf.add_browser(700, 500, BrowserType.IE_11)
    conf.add_browser(1600, 1200, BrowserType.CHROME)
    conf.add_browser(1200, 800, BrowserType.EDGE)
    conf.add_browser(800, 600, BrowserType.CHROME)
    conf.add_browser(700, 500, BrowserType.CHROME)
    conf.add_device_emulation(DeviceName.iPhone_4)
    conf.add_device_emulation(DeviceName.iPhone_X)
    conf.add_device_emulation(DeviceName.Nexus_10, ScreenOrientation.LANDSCAPE)
    return conf


@pytest.mark.parametrize(
    "test_page_url",
    [
        # "https://www.google.com/",
        # "http://allatra.tv/",
        # "http://opzharp.ru/",
        # "http://www.sage.co.uk/",
        # "https://www.wikipedia.org/",
        # "https://www.instagram.com/",
        # "https://youtube.com/",
        # "http://applitools-vg-test.surge.sh/test.html"
        "https://demo.applitools.com"
    ],
)
@pytest.mark.viewport_size(dict(width=600, height=600))
def test_top_sites(eyes_vg, test_page_url):
    eyes_vg.check("Step1 - " + test_page_url, Target.window().send_dom(True))
    eyes_vg.check(
        "Step2 - " + test_page_url, Target.window().fully(True).send_dom(True)
    )
