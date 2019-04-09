import pytest

from applitools.common import BrowserType, SeleniumConfiguration, BatchInfo
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
    environment = "My env name"
    conf.add_browser(800, 600, BrowserType.CHROME, environment)
    # conf.add_browser(700, 500, BrowserType.FIREFOX, environment)
    # conf.add_browser(700, 500, BrowserType.IE_10, environment)
    # conf.add_browser(700, 500, BrowserType.IE_11, environment)
    # conf.add_browser(1600, 1200, BrowserType.CHROME, environment)
    # conf.add_browser(1200, 800, BrowserType.EDGE, environment)

    return conf


@pytest.mark.test_page_url("http://opzharp.ru/")
# @pytest.mark.test_page_url("http://www.sage.co.uk/")
@pytest.mark.app_name("Michael's App")
@pytest.mark.test_name("First Test")
@pytest.mark.viewport_size(dict(width=600, height=600))
def test_top_sites(eyes_vg, request):
    test_page_url = request.node.get_closest_marker("test_page_url").args[0]
    eyes_vg.check("Step1 - " + test_page_url, Target.window().send_dom(True))
    # eyes_vg.check(
    #     "Step2 - " + test_page_url, Target.window().fully(False).send_dom(True)
    # )
