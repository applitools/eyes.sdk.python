from applitools.selenium import RunnerOptions, VisualGridRunner


def test_visual_gird_runner_no_args():
    runner = VisualGridRunner()

    runner.get_all_test_results()

    assert runner._options.get_test_concurrency() == 5


def test_visual_gird_runner_legacy_concurrency_1():
    runner = VisualGridRunner(1)

    runner.get_all_test_results()

    assert runner._options.get_test_concurrency() == 5


def test_visual_gird_runner_legacy_concurrency_2():
    runner = VisualGridRunner(2)

    runner.get_all_test_results()

    assert runner._options.get_test_concurrency() == 10


def test_visual_gird_runner_default_runner_options():
    runner = VisualGridRunner(RunnerOptions())

    runner.get_all_test_results()

    assert runner._options.get_test_concurrency() == 5


def test_visual_gird_runner_runner_options_1():
    runner = VisualGridRunner(RunnerOptions(test_concurrency=1))

    runner.get_all_test_results()

    assert runner._options.get_test_concurrency() == 1


def test_visual_gird_runner_runner_options_2():
    runner = VisualGridRunner(RunnerOptions().test_concurrency(2))

    runner.get_all_test_results()

    assert runner._options.get_test_concurrency() == 2
