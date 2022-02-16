from mock import call, patch

from applitools.selenium import RunnerOptions, VisualGridRunner
from applitools.selenium.__version__ import __version__
from applitools.selenium.command_executor import ManagerType


def test_visual_grid_runner_creation_default():
    get_instance = "applitools.selenium.command_executor.CommandExecutor.get_instance"
    with patch(get_instance) as get_instance:
        VisualGridRunner()

        assert get_instance.mock_calls == [
            call("eyes.selenium.visualgrid.python", __version__),
            call().core_make_manager(ManagerType.VG, 5, False),
        ]


def test_visual_grid_runner_creation_legacy_concurrency():
    get_instance = "applitools.selenium.command_executor.CommandExecutor.get_instance"
    with patch(get_instance) as get_instance:
        VisualGridRunner(2)

        assert get_instance.mock_calls == [
            call("eyes.selenium.visualgrid.python", __version__),
            call().core_make_manager(ManagerType.VG, 10, True),
        ]


def test_visual_grid_runner_creation_test_concurrency():
    get_instance = "applitools.selenium.command_executor.CommandExecutor.get_instance"
    with patch(get_instance) as get_instance:
        VisualGridRunner(RunnerOptions().test_concurrency(3))

        assert get_instance.mock_calls == [
            call("eyes.selenium.visualgrid.python", __version__),
            call().core_make_manager(ManagerType.VG, 3, False),
        ]
