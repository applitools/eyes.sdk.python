import pytest
from mock import patch

from applitools.selenium import BrowserType, Eyes, Target


@pytest.mark.test_page_url("https://applitools.com/helloworld")
def test_test_vg_check_source_sent(chrome_driver, vg_runner):
    eyes = Eyes(vg_runner)
    eyes.configure.add_browser(800, 600, BrowserType.CHROME)
    eyes.configure.add_browser(800, 600, BrowserType.FIREFOX)
    eyes.configure.app_name = "TestCheckSourceSent"
    eyes.configure.test_name = "TestVgCheckSourceSent"

    try:
        eyes.open(chrome_driver)
        with patch(
            "applitools.core.server_connector.ServerConnector.match_window"
        ) as smw:
            eyes.check("", Target.window())
            eyes.close()
            match_window_data = smw.call_args[0][1]
    finally:
        eyes.abort()

    assert match_window_data.options.source == "applitools.com"
