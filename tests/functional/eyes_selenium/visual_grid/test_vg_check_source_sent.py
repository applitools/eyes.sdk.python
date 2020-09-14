from mock import patch

from applitools.selenium import BrowserType, Eyes, Target


def test_test_vg_check_source_sent(driver, vg_runner):
    driver.get("https://applitools.com/helloworld")
    eyes = Eyes(vg_runner)
    eyes.configuration.add_browser(800, 600, BrowserType.CHROME)
    eyes.configuration.add_browser(800, 600, BrowserType.FIREFOX)
    eyes.configuration.app_name = "TestCheckSourceSent"
    eyes.configuration.test_name = "TestVgCheckSourceSent"

    try:
        eyes.open(driver)
        with patch(
            "applitools.core.server_connector.ServerConnector.match_window"
        ) as smw:
            eyes.check("", Target.window())
            eyes.close()
            match_window_data = smw.call_args[0][1]
    finally:
        eyes.abort()

    assert match_window_data.options.source == "applitools.com"
