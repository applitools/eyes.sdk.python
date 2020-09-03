from mock import patch

from applitools.common import VisualGridOption
from applitools.common.selenium import BrowserType
from applitools.selenium import VisualGridRunner, Eyes, Target


def test_ufg_options(driver):
    runner = VisualGridRunner(1)
    eyes = Eyes(runner)

    (
        eyes.configure.add_browser(
            800, 600, BrowserType.CHROME
        ).set_visual_grid_options(
            VisualGridOption("option1", "value1"), VisualGridOption("option2", False)
        )
    )

    driver.get("https://google.com")
    with patch("applitools.core.server_connector.ServerConnector.render",) as patched:
        eyes.open(driver, "Mock app", "Mock Test")
        eyes.check(
            "",
            Target.window().visual_grid_options(
                VisualGridOption("option3", "value3"),
                VisualGridOption("option4", 5),
                VisualGridOption("option1", 5),
            ),
        )
        eyes.close_async()
        res = runner.get_all_test_results()

        request_options = patched.call_args.args[0].options
        assert request_options == {
            "option1": 5,
            "option2": False,
            "option3": "value3",
            "option4": 5,
        }
