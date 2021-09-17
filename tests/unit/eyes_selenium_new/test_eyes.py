from applitools.selenium.command_executor import ManagerType
from applitools.selenium.eyes import RunnerOptions, VisualGridRunner


def test_visual_grid_runner_creation_no_args():
    runner = VisualGridRunner()

    assert runner._manager_args == (ManagerType.VG, 5, False)


def test_visual_grid_runner_creation_int():
    runner = VisualGridRunner(2)

    assert runner._manager_args == (ManagerType.VG, 10, True)


def test_visual_grid_runner_creation_runner_options():
    runner = VisualGridRunner(RunnerOptions().test_concurrency(7))

    assert runner._manager_args == (ManagerType.VG, 7, False)
