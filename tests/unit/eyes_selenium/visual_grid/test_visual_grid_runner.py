from applitools.selenium import RunnerOptions, VisualGridRunner


def test_visual_gird_runner_no_args():
    runner = VisualGridRunner()

    runner.get_all_test_results()

    assert runner._concurrency.kind.value == "defaultConcurrency"
    assert runner._concurrency.value == 5


def test_visual_gird_runner_legacy_concurrency_1():
    runner = VisualGridRunner(1)

    runner.get_all_test_results()

    assert runner._concurrency.kind.value == "concurrency"
    assert runner._concurrency.value == 5


def test_visual_gird_runner_legacy_concurrency_2():
    runner = VisualGridRunner(2)

    runner.get_all_test_results()

    assert runner._concurrency.kind.value == "concurrency"
    assert runner._concurrency.value == 10


def test_visual_gird_runner_default_runner_options():
    runner = VisualGridRunner(RunnerOptions())

    runner.get_all_test_results()

    assert runner._concurrency.kind.value == "defaultConcurrency"
    assert runner._concurrency.value == 5


def test_visual_gird_runner_runner_options_2():
    runner = VisualGridRunner(RunnerOptions().test_concurrency(2))

    runner.get_all_test_results()

    assert runner._concurrency.kind.value == "testConcurrency"
    assert runner._concurrency.value == 2
