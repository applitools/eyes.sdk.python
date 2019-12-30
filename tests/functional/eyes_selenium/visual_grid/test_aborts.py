import pytest
from mock import patch

from applitools.common import RenderStatus, RenderStatusResults
from applitools.selenium import BrowserType, Eyes, Target, Configuration


@pytest.fixture
def conf(batch_info):
    return Configuration(
        app_name="Visual Grid Render Test", batch=batch_info
    ).add_browser(1200, 800, BrowserType.CHROME)


def test_abort_when_not_rendered(driver, vg_runner, conf):
    eyes = Eyes(vg_runner)
    eyes.set_configuration(conf.set_test_name("TestAbortWhenNotRendering"))
    driver.get("https://demo.applitools.com")
    with patch(
        "applitools.core.server_connector.ServerConnector.render_status_by_id"
    ) as rsbi:
        rsbi.return_value = [RenderStatusResults(status=RenderStatus.ERROR)]
        eyes.open(driver)
        eyes.check("", Target.window())
        eyes.close_async()
        all_results = vg_runner.get_all_test_results(False)


def test_abort_async_on_vg(driver, vg_runner, conf):
    eyes = Eyes(vg_runner)
    eyes.set_configuration(conf.set_test_name("TestAbortAsync"))
    driver.get("https://demo.applitools.com")
    eyes.open(driver)
    eyes.check("", Target.window())
    eyes.close_async()
    eyes.abort_async()
    all_results = vg_runner.get_all_test_results(False)
