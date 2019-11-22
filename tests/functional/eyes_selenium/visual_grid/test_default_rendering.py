from applitools.selenium import Eyes, Target, BrowserType


def test_default_rendering_of_multiple_targets(driver, vg_runner):
    driver.get("https://applitools.com/helloworld")
    eyes = Eyes(vg_runner)
    eyes.configuration.add_browser(800, 600, BrowserType.CHROME)
    eyes.configuration.add_browser(800, 600, BrowserType.FIREFOX)
    eyes.configuration.add_browser(1200, 800, BrowserType.CHROME)
    eyes.configuration.add_browser(1200, 800, BrowserType.FIREFOX)
    eyes.configuration.app_name = "TestDefaultRendering"
    eyes.configuration.test_name = "TestDefaultRenderingOfMultipleTargets"

    try:
        eyes.open(driver)
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
