from mock import patch

from applitools.selenium import Eyes, Target, BrowserType


def test_default_rendering_of_multiple_targets(driver, vg_runner):
    driver.get("https://applitools.com/helloworld")
    eyes = Eyes(vg_runner)
    eyes.configuration.add_browser(800, 600, BrowserType.CHROME)
    eyes.configuration.add_browser(800, 600, BrowserType.FIREFOX)
    eyes.configuration.app_name = "TestTrackingTestHostname"
    eyes.configuration.test_name = "TestTrackingTestHostnameOfMultipleTargets"

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
