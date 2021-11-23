import pytest
from AppiumLibrary import AppiumLibrary
from mock import Mock
from SeleniumLibrary import SeleniumLibrary

from applitools.common.utils.datetime_utils import sleep
from applitools.selenium import Eyes, eyes_selenium_utils
from EyesLibrary.base import RobotMobileNativeRunner, RobotWebRunner, RobotWebUFGRunner


@pytest.mark.parametrize(
    "library,runner,agent_id",
    [
        [Mock(SeleniumLibrary), RobotWebRunner, "eyes.python.robotframework.selenium"],
        [
            Mock(SeleniumLibrary),
            lambda: RobotWebUFGRunner(1),
            "eyes.python.robotframework.visual_grid",
        ],
        [
            Mock(AppiumLibrary),
            RobotMobileNativeRunner,
            "eyes.python.robotframework.appium",
        ],
    ],
)
@pytest.mark.skip(reason="Should be adapted to USDK")
def test_agent_id(
    fake_connector_class, driver_mock, monkeypatch, library, runner, agent_id
):
    monkeypatch.setattr(eyes_selenium_utils, "set_viewport_size", lambda *_: None)
    eyes = Eyes(runner())
    # avoid use custom setter on Eyes object
    eyes._current_eyes.server_connector = fake_connector_class()

    eyes.open(driver_mock, "A", "B", {"width": 100, "height": 100})
    eyes.abort_async()
    while "start_session" not in eyes.server_connector.calls:
        sleep(1)  # wait until runner opens session in background thread
    assert eyes.server_connector.calls["start_session"].agent_id.startswith(agent_id)
