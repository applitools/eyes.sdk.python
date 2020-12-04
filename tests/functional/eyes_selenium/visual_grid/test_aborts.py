import time

from mock import patch

from applitools.common import RenderStatus, RenderStatusResults
from applitools.selenium import BrowserType, Eyes, Target


def test_abort_when_not_rendered(driver, vg_runner, batch_info):
    eyes = Eyes(vg_runner)
    eyes.configure.test_name = "TestAbortWhenNotRendering"
    eyes.configure.app_name = "Visual Grid Render Test"
    eyes.configure.batch = batch_info
    eyes.configure.add_browser(1200, 800, BrowserType.CHROME)
    driver.get("https://demo.applitools.com")
    with patch(
        "applitools.core.server_connector.ServerConnector.render_status_by_id"
    ) as rsbi:
        rsbi.return_value = [RenderStatusResults(status=RenderStatus.ERROR)]
        eyes.open(driver)
        eyes.check(Target.window())
        eyes.close_async()
        all_results = vg_runner.get_all_test_results(False)


def test_abort_when_dom_snapshot_error(driver, vg_runner, batch_info):
    eyes = Eyes(vg_runner)
    eyes.configure.test_name = "TestAbortWhenDonSnapshotError"
    eyes.configure.app_name = "Visual Grid Render Test"
    eyes.configure.batch = batch_info
    eyes.configure.add_browser(1200, 800, BrowserType.CHROME)
    driver.get("https://demo.applitools.com")
    with patch(
        "applitools.selenium.visual_grid.visual_grid_eyes.VisualGridEyes.get_script_result",
        side_effect=Exception,
    ):
        eyes.open(driver)
        eyes.check(Target.window())
        eyes.close_async()
        all_results = vg_runner.get_all_test_results(False)
        assert len(all_results) == 1


def test_abort_async_on_vg(driver, vg_runner, batch_info):
    eyes = Eyes(vg_runner)
    eyes.configure.test_name = "Test Abort_VG"
    eyes.configure.app_name = "Test Abort_VG"
    eyes.configure.batch = batch_info
    eyes.configure.add_browser(800, 600, BrowserType.CHROME)
    driver.get("data:text/html,<p>Test</p>")
    eyes.open(driver)
    eyes.check(Target.window())
    time.sleep(15)
    eyes.abort_async()
    all_results = vg_runner.get_all_test_results(False)
