import pytest

from applitools.common import RGridDom
from applitools.selenium import Eyes, VisualGridRunner

pytestmark = [
    pytest.mark.test_page_url(
        "https://applitools.github.io/demo/TestPages/SimpleTestPage"
    ),
]


def test_visual_grid_runner_runner_started_logging(fake_connector_class):
    connector = fake_connector_class()
    runner = VisualGridRunner()

    runner._send_runner_started_log_message(connector)

    event = connector.input_calls["send_logs"][0][0]
    assert event.level.value == 2
    assert event.event == '{"defaultConcurrency": 5, "type": "runnerStarted"}'


def test_render_failure_aborts_session(chrome_driver, batch_info, vg_runner, spy):
    eyes = Eyes(vg_runner)
    close_session_spy = spy(eyes.server_connector, "stop_session")

    def broken(*args):
        raise Exception

    eyes.server_connector.render = broken
    eyes.open(chrome_driver, "Eyes SDK", "UFG Render Error")
    eyes.check_window()
    eyes.close(False)

    assert close_session_spy.call_args_list == [spy.call(spy.ANY, True, False)]


def test_snapshot_too_big_aborts_session(chrome_driver, vg_runner, spy, monkeypatch):
    monkeypatch.setattr(RGridDom, "MAX_CDT_SIZE", 1)
    eyes = Eyes(vg_runner)
    close_session_spy = spy(eyes.server_connector, "stop_session")

    eyes.open(chrome_driver, "Eyes SDK", "UFG Render Error")
    eyes.check_window()
    eyes.close(False)

    assert close_session_spy.call_args_list == [spy.call(spy.ANY, True, False)]


def test_non_closed_tests_aborted(chrome_driver, vg_runner, spy, capsys):
    eyes = Eyes(vg_runner)
    close_session_spy = spy(eyes.server_connector, "stop_session")

    eyes.open(chrome_driver, "Eyes SDK", "UFG Render Error")
    eyes.check_window()

    vg_runner.get_all_test_results(False)
    stdout = capsys.readouterr().out

    assert close_session_spy.call_args_list == [spy.call(spy.ANY, True, False)]
    assert "Warning: Unclosed tests found and aborted: {'UFG Render Error'}" in stdout


def test_non_closed_finished_tests_do_not_issue_warning(
    chrome_driver, vg_runner, capsys
):
    eyes = Eyes(vg_runner)

    eyes.open(chrome_driver, "Eyes SDK", "UFG Render Error")
    eyes.check_window()
    eyes.close_async()
    vg_runner.get_all_test_results(False)
    stdout = capsys.readouterr().out

    assert "Warning: Unclosed tests found and aborted" not in stdout


def test_null_render_status_aborts_test(chrome_driver, vg_runner, spy, capsys):
    eyes = Eyes(vg_runner)
    close_session_spy = spy(eyes.server_connector, "stop_session")

    def render_status_none(*args):
        return [None]

    eyes.server_connector.render_status_by_id = render_status_none
    eyes.open(chrome_driver, "Eyes SDK", "UFG Render Error")
    eyes.check_window()
    eyes.close_async()
    vg_runner.get_all_test_results(False)

    assert close_session_spy.call_args_list == [spy.call(spy.ANY, True, False)]
