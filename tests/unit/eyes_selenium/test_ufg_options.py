from mock import MagicMock

from applitools.common import VisualGridOption
from applitools.common.selenium import BrowserType
from applitools.core import ServerConnector
from applitools.selenium import VisualGridRunner, Eyes, Target


def test_ufg_options(started_connector, driver_mock):
    runner = MagicMock(VisualGridRunner)
    eyes = Eyes(runner)

    eyes.server_connector = MagicMock(ServerConnector)

    (
        eyes.configure.add_browser(
            800, 600, BrowserType.CHROME
        ).set_visual_grid_options(
            VisualGridOption("option1", "value1"), VisualGridOption("option2", False)
        )
    )

    eyes.open(driver_mock, "Mock app", "Mock Test")
    eyes.check(
        "",
        Target.window().visual_grid_options(
            VisualGridOption("option3", "value3"), VisualGridOption("option4", 5)
        ),
    )
    render_request_json = eyes.server_connector.last_render_request

    assert render_request_json
