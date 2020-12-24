from applitools.selenium import VisualGridRunner


def test_visual_grid_runner_runner_started_logging(fake_connector_class):
    connector = fake_connector_class()
    runner = VisualGridRunner()

    runner._send_runner_started_log_message(connector)

    event = connector.input_calls["send_logs"][0][0]
    assert event.level.value == 2
    assert event.event == '{"defaultConcurrency": 5, "type": "runnerStarted"}'
