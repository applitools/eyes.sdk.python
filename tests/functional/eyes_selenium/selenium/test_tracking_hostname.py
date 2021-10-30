import pytest
from mock import patch


@pytest.mark.test_page_url("https://demo.applitools.com")
def test_match_window_data_contains_webapp_domain(eyes, chrome_driver):
    eyes.open(
        chrome_driver,
        "TestCheckSourceSent",
        "Test tracking hostname",
        {"width": 1000, "height": 600},
    )
    with patch("applitools.core.server_connector.ServerConnector.match_window") as smw:
        eyes.check_window("Step 1", fully=True)
        match_window_data = smw.call_args[0][1]
    eyes.close()
    assert match_window_data.options.source == "demo.applitools.com"
