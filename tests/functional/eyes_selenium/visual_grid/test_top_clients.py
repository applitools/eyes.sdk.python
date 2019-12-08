import pytest

from applitools.selenium import (
    BrowserType,
    Configuration,
    DeviceName,
    Eyes,
    ScreenOrientation,
    Target,
    logger,
)


@pytest.fixture
def sel_config(test_page_url):
    conf = Configuration()
    conf.test_name = "Top 10 websites - {}".format(test_page_url)
    conf.app_name = "Top Ten Sites"
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


@pytest.fixture
def eyes_vg(vg_runner, sel_config, batch_info, driver, request, test_page_url):
    app_name = request.node.get_closest_marker("app_name")
    if app_name:
        app_name = app_name.args[0]
    test_name = request.node.get_closest_marker("test_name")
    if test_name:
        test_name = test_name.args[0]
    viewport_size = request.node.get_closest_marker("viewport_size")
    if viewport_size:
        viewport_size = viewport_size.args[0]
    else:
        viewport_size = None

    eyes = Eyes(vg_runner)
    eyes.server_url = "https://eyes.applitools.com/"
    eyes.configuration = sel_config
    eyes.configuration.batch = batch_info
    app_name = app_name or eyes.configuration.app_name
    test_name = test_name or eyes.configuration.test_name
    viewport_size = viewport_size or eyes.configuration.viewport_size

    driver.get(test_page_url)
    eyes.open(driver, app_name, test_name, viewport_size)
    yield eyes
    logger.debug("closing WebDriver for url {}".format(test_page_url))
    eyes.close()
    # TODO: print VG test results


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
