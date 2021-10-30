import time

import pytest
from mock import patch

from applitools.common import EyesError, RenderStatus, RenderStatusResults
from applitools.core import ServerConnector
from applitools.selenium import BrowserType, Eyes, Target


@pytest.mark.test_page_url("https://demo.applitools.com")
def test_abort_when_not_rendered(chrome_driver, vg_runner, batch_info, monkeypatch):
    def failed_status(self, *ids):
        return [
            RenderStatusResults(status=RenderStatus.ERROR, render_id=i) for i in ids
        ]

    monkeypatch.setattr(ServerConnector, "render_status_by_id", failed_status)
    eyes = Eyes(vg_runner)
    eyes.configure.test_name = "TestAbortWhenNotRendering"
    eyes.configure.app_name = "Visual Grid Render Test"
    eyes.configure.batch = batch_info
    eyes.configure.add_browser(1200, 800, BrowserType.CHROME)
    eyes.open(chrome_driver)
    eyes.check(Target.window())
    eyes.close_async()
    all_results = vg_runner.get_all_test_results(False)


@pytest.mark.test_page_url("https://demo.applitools.com")
def test_get_all_tests_results_timeout(
    chrome_driver, vg_runner, batch_info, monkeypatch
):
    original_renderinfo = ServerConnector.render_info

    def delay_renderinfo(self, *ids):
        time.sleep(2)
        return original_renderinfo(self, *ids)

    monkeypatch.setattr(ServerConnector, "render_info", delay_renderinfo)
    eyes = Eyes(vg_runner)
    eyes.configure.test_name = "GetAllTestsResultsTimeout"
    eyes.configure.app_name = "Visual Grid Render Test"
    eyes.configure.batch = batch_info
    eyes.open(chrome_driver)
    eyes.close_async()
    with pytest.raises(EyesError):
        vg_runner.get_all_test_results(False, 1)


@pytest.mark.test_page_url("https://demo.applitools.com")
def test_abort_when_dom_snapshot_error(chrome_driver, vg_runner, batch_info):
    eyes = Eyes(vg_runner)
    eyes.configure.test_name = "TestAbortWhenDonSnapshotError"
    eyes.configure.app_name = "Visual Grid Render Test"
    eyes.configure.batch = batch_info
    eyes.configure.add_browser(1200, 800, BrowserType.CHROME)
    with patch(
        "applitools.selenium.visual_grid.visual_grid_eyes.VisualGridEyes.get_script_result",
        side_effect=Exception,
    ):
        eyes.open(chrome_driver)
        eyes.check(Target.window())
        eyes.close_async()
        all_results = vg_runner.get_all_test_results(False)
        assert len(all_results) == 1


@pytest.mark.test_page_url("data:text/html,<p>Test</p>")
def test_abort_async_on_vg(chrome_driver, vg_runner, batch_info):
    eyes = Eyes(vg_runner)
    eyes.configure.test_name = "Test Abort_VG"
    eyes.configure.app_name = "Test Abort_VG"
    eyes.configure.batch = batch_info
    eyes.configure.add_browser(800, 600, BrowserType.CHROME)
    eyes.open(chrome_driver)
    eyes.check(Target.window())
    time.sleep(15)
    eyes.abort_async()
    all_results = vg_runner.get_all_test_results(False)


@pytest.mark.test_page_url("data:text/html,<p>Test</p>")
def test_abort_after_close_must_not_abort(chrome_driver, vg_runner, batch_info):
    eyes = Eyes(vg_runner)
    eyes.configure.test_name = "Test abort after close VG"
    eyes.configure.app_name = "Test Abort_VG"
    eyes.configure.batch = batch_info
    eyes.configure.add_browser(800, 600, BrowserType.CHROME)
    eyes.open(chrome_driver)
    eyes.check(Target.window())
    eyes.close()
    eyes.abort()
    all_results = vg_runner.get_all_test_results()


@pytest.mark.test_page_url("data:text/html,<p>Test</p>")
def test_abort_after_close_async_must_not_abort(chrome_driver, vg_runner, batch_info):
    eyes = Eyes(vg_runner)
    eyes.configure.test_name = "Test abort after close async VG"
    eyes.configure.app_name = "Test Abort_VG"
    eyes.configure.batch = batch_info
    eyes.configure.add_browser(800, 600, BrowserType.CHROME)
    eyes.open(chrome_driver)
    eyes.check(Target.window())
    eyes.close_async()
    eyes.abort()
    all_results = vg_runner.get_all_test_results()


@pytest.mark.test_page_url("data:text/html,<p>Test</p>")
def test_abort_async_after_close_async_must_not_abort(
    chrome_driver, vg_runner, batch_info
):
    eyes = Eyes(vg_runner)
    eyes.configure.test_name = "Test abort async after close async VG"
    eyes.configure.app_name = "Test Abort_VG"
    eyes.configure.batch = batch_info
    eyes.configure.add_browser(800, 600, BrowserType.CHROME)
    eyes.open(chrome_driver)
    eyes.check(Target.window())
    eyes.close_async()
    eyes.abort_async()
    all_results = vg_runner.get_all_test_results()
