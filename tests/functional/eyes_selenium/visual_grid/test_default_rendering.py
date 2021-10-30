import pytest

from applitools.selenium import BrowserType, Eyes, Target


@pytest.mark.test_page_url("https://applitools.com/helloworld")
def test_default_rendering_of_multiple_targets(chrome_driver, vg_runner):
    eyes = Eyes(vg_runner)
    eyes.configure.add_browser(800, 600, BrowserType.CHROME)
    eyes.configure.add_browser(800, 600, BrowserType.FIREFOX)
    eyes.configure.add_browser(1200, 800, BrowserType.CHROME)
    eyes.configure.add_browser(1200, 800, BrowserType.FIREFOX)
    eyes.configure.app_name = "TestDefaultRendering"
    eyes.configure.test_name = "TestDefaultRenderingOfMultipleTargets"

    try:
        eyes.open(chrome_driver)
        eyes.check("", Target.window())
        eyes.close()
    finally:
        eyes.abort()

    all_test_results = vg_runner.get_all_test_results()
    batch_id = None
    batch_name = None
    for trc in all_test_results:
        if batch_id is None:
            batch_id = trc.test_results.batch_id
        if batch_name is None:
            batch_name = trc.test_results.batch_name

        assert batch_id == trc.test_results.batch_id
        assert batch_name == trc.test_results.batch_name
