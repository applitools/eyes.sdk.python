import pytest

from applitools.common import RGridDom
from applitools.selenium import Eyes, VisualGridRunner


def test_visual_grid_runner_runner_started_logging(fake_connector_class):
    connector = fake_connector_class()
    runner = VisualGridRunner()

    runner._send_runner_started_log_message(connector)

    event = connector.input_calls["send_logs"][0][0]
    assert event.level.value == 2
    assert event.event == '{"defaultConcurrency": 5, "type": "runnerStarted"}'


@pytest.mark.skip("Fix reverted due to regression https://trello.com/c/YewzI8IN")
def test_render_failure_aborts_session(driver, batch_info, vg_runner, spy):
    driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage")
    eyes = Eyes(vg_runner)
    close_session_spy = spy(eyes.server_connector, "stop_session")

    def broken(*args):
        raise Exception

    eyes.server_connector.render = broken
    eyes.open(driver, "Eyes SDK", "UFG Render Error")
    eyes.check_window()
    eyes.close(False)

    assert close_session_spy.call_args_list == [spy.call(spy.ANY, True, False)]


@pytest.mark.skip("Fix reverted due to regression https://trello.com/c/YewzI8IN")
def test_snapshot_too_big_aborts_session(driver, vg_runner, spy, monkeypatch):
    monkeypatch.setattr(RGridDom, "MAX_CDT_SIZE", 1)
    driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage")
    eyes = Eyes(vg_runner)
    close_session_spy = spy(eyes.server_connector, "stop_session")

    eyes.open(driver, "Eyes SDK", "UFG Render Error")
    eyes.check_window()
    eyes.close(False)

    assert close_session_spy.call_args_list == [spy.call(spy.ANY, True, False)]
