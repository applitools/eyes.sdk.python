from mock import MagicMock

from applitools.common import VisualGridOption
from applitools.common.selenium import BrowserType
from applitools.core import ServerConnector
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
    eyes.open(driver, "Mock app", "Mock Test")
    eyes.check(
        "",
        Target.window().visual_grid_options(
            VisualGridOption("option3", "value3"), VisualGridOption("option4", 5)
        ),
    )
    eyes.close_async()
    res = runner.get_all_test_results()
