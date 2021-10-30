import pytest

from applitools.common import VisualGridOption
from applitools.common.selenium import BrowserType
from applitools.selenium import Eyes, Target, VisualGridRunner


@pytest.mark.test_page_url("https://google.com")
def test_ufg_options(chrome_driver, fake_connector_class):
    runner = VisualGridRunner(1)
    eyes = Eyes(runner)
    eyes.server_connector = fake_connector_class()

    (
        eyes.configure.add_browser(
            800, 600, BrowserType.CHROME
        ).set_visual_grid_options(
            VisualGridOption("option1", "value1"), VisualGridOption("option2", False)
        )
    )

    eyes.open(chrome_driver, "Mock app", "Mock Test")
    eyes.check(
        "",
        Target.window().visual_grid_options(
            VisualGridOption("option3", "value3"),
            VisualGridOption("option4", 5),
            VisualGridOption("option1", 5),
        ),
    )
    eyes.close_async()
    runner.get_all_test_results()

    request_options = eyes.server_connector.input_calls["render"][0][0].options
    assert request_options == {
        "option1": 5,
        "option2": False,
        "option3": "value3",
        "option4": 5,
    }
