import time

import pytest

from applitools.selenium import ClassicRunner, Eyes, Target, VisualGridRunner


def pytest_generate_tests(metafunc):
    metafunc.parametrize("eyes_runner", [ClassicRunner(), VisualGridRunner(5)])


@pytest.fixture()
def name_suffix(eyes_runner):
    if isinstance(eyes_runner, ClassicRunner):
        return ""
    else:
        return "_VG"


def test_double_open_check_close(local_chrome_driver, eyes_runner, name_suffix):
    eyes = Eyes(eyes_runner)
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/VisualGridTestPage/"
    )
    eyes.open(
        local_chrome_driver,
        "Applitools Eyes SDK",
        "TestDoubleOpenCheckClose" + name_suffix,
        dict(width=1200, height=800),
    )
    eyes.check("Step 1", Target.window().fully().ignore_displacements(False))
    eyes.close(False)

    eyes.open(
        local_chrome_driver,
        "Applitools Eyes SDK",
        "TestDoubleOpenCheckClose" + name_suffix,
        dict(width=1200, height=800),
    )
    eyes.check("Step 2", Target.window().fully().ignore_displacements(False))
    eyes.close(False)

    all_test_results = eyes_runner.get_all_test_results(False)
    assert len(all_test_results.all_results) == 2


def test_double_open_check_close_async(local_chrome_driver, eyes_runner, name_suffix):
    eyes = Eyes(eyes_runner)
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/VisualGridTestPage/"
    )
    eyes.open(
        local_chrome_driver,
        "Applitools Eyes SDK",
        "TestDoubleOpenCheckCloseAsync" + name_suffix,
        dict(width=1200, height=800),
    )
    eyes.check("Step 1", Target.window().fully().ignore_displacements(False))
    eyes.close_async()

    eyes.open(
        local_chrome_driver,
        "Applitools Eyes SDK",
        "TestDoubleOpenCheckCloseAsync" + name_suffix,
        dict(width=1200, height=800),
    )
    eyes.check("Step 2", Target.window().fully().ignore_displacements(False))
    eyes.close_async()

    all_test_results = eyes_runner.get_all_test_results(False)
    assert len(all_test_results.all_results) == 2


def test_double_open_check_close_with_different_instances(
    local_chrome_driver, eyes_runner, name_suffix
):
    eyes1 = Eyes(eyes_runner)
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/VisualGridTestPage/"
    )
    eyes1.open(
        local_chrome_driver,
        "Applitools Eyes SDK",
        "TestDoubleOpenCheckCloseWithDifferentInstances" + name_suffix,
        dict(width=1200, height=800),
    )
    eyes1.check("Step 1", Target.window().fully().ignore_displacements(False))
    eyes1.close(False)

    eyes2 = Eyes(eyes_runner)
    eyes2.open(
        local_chrome_driver,
        "Applitools Eyes SDK",
        "TestDoubleOpenCheckCloseWithDifferentInstances" + name_suffix,
        dict(width=1200, height=800),
    )
    eyes2.check("Step 2", Target.window().fully().ignore_displacements(False))
    eyes2.close(False)

    all_test_results = eyes_runner.get_all_test_results(False)
    assert len(all_test_results.all_results) == 2


def test_double_open_check_close_async_with_different_instances(
    local_chrome_driver, eyes_runner, name_suffix
):
    eyes1 = Eyes(eyes_runner)
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/VisualGridTestPage/"
    )
    eyes1.open(
        local_chrome_driver,
        "Applitools Eyes SDK",
        "TestDoubleOpenCheckCloseAsyncWithDifferentInstances" + name_suffix,
        dict(width=1200, height=800),
    )
    eyes1.check("Step 1", Target.window().fully().ignore_displacements(False))
    eyes1.close_async()

    eyes2 = Eyes(eyes_runner)
    eyes2.open(
        local_chrome_driver,
        "Applitools Eyes SDK",
        "TestDoubleOpenCheckCloseAsyncWithDifferentInstances" + name_suffix,
        dict(width=1200, height=800),
    )
    eyes2.check("Step 2", Target.window().fully().ignore_displacements(False))
    eyes2.close_async()

    all_test_results = eyes_runner.get_all_test_results(False)
    assert len(all_test_results.all_results) == 2


def test_double_check_dont_get_all_results(
    local_chrome_driver, eyes_runner, name_suffix
):
    eyes = Eyes(eyes_runner)
    local_chrome_driver.get("https://applitools.com/helloworld")
    eyes.open(
        local_chrome_driver,
        "Applitools Eyes SDK",
        "TestDoubleCheckDontGetAllResults" + name_suffix,
        dict(width=1200, height=800),
    )
    eyes.check("Step 1", Target.window().with_name("Step 1"))
    eyes.check("Step 2", Target.window().with_name("Step 2"))
    eyes.close(False)
