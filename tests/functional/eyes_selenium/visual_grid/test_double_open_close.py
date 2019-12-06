from applitools.selenium import Eyes, Target


def test_double_open_check_close(driver, vg_runner):
    eyes = Eyes(vg_runner)
    driver.get("https://applitools.github.io/demo/TestPages/VisualGridTestPage/")
    eyes.open(
        driver,
        "Applitools Eyes Python SDK",
        "TestDoubleOpenCheckClose_VG",
        dict(width=1200, height=800),
    )
    eyes.check("Step 1", Target.window().fully().ignore_displacements(False))
    eyes.close(False)

    eyes.open(
        driver,
        "Applitools Eyes Python SDK",
        "TestDoubleOpenCheckClose_VG",
        dict(width=1200, height=800),
    )
    eyes.check("Step 2", Target.window().fully().ignore_displacements(False))
    eyes.close(False)

    all_test_results = vg_runner.get_all_test_results(False)
    assert len(all_test_results.all_results) == 2


def test_double_open_check_close_async(driver, vg_runner):
    eyes = Eyes(vg_runner)
    driver.get("https://applitools.github.io/demo/TestPages/VisualGridTestPage/")
    eyes.open(
        driver,
        "Applitools Eyes Python SDK",
        "TestDoubleOpenCheckCloseAsync_VG",
        dict(width=1200, height=800),
    )
    eyes.check("Step 1", Target.window().fully().ignore_displacements(False))
    eyes.close_async()

    eyes.open(
        driver,
        "Applitools Eyes Python SDK",
        "TestDoubleOpenCheckCloseAsync_VG",
        dict(width=1200, height=800),
    )
    eyes.check("Step 2", Target.window().fully().ignore_displacements(False))
    eyes.close_async()

    all_test_results = vg_runner.get_all_test_results(False)
    assert len(all_test_results.all_results) == 2


def test_double_open_check_close_with_different_instances(driver, vg_runner):
    eyes1 = Eyes(vg_runner)
    driver.get("https://applitools.github.io/demo/TestPages/VisualGridTestPage/")
    eyes1.open(
        driver,
        "Applitools Eyes Python SDK",
        "TestDoubleOpenCheckCloseWithDifferentInstances_VG",
        dict(width=1200, height=800),
    )
    eyes1.check("Step 1", Target.window().fully().ignore_displacements(False))
    eyes1.close(False)

    eyes2 = Eyes(vg_runner)
    eyes2.open(
        driver,
        "Applitools Eyes Python SDK",
        "TestDoubleOpenCheckCloseWithDifferentInstances_VG",
        dict(width=1200, height=800),
    )
    eyes2.check("Step 2", Target.window().fully().ignore_displacements(False))
    eyes2.close(False)

    all_test_results = vg_runner.get_all_test_results(False)
    assert len(all_test_results.all_results) == 2


def test_double_open_check_close_async_with_different_instances(driver, vg_runner):
    eyes1 = Eyes(vg_runner)
    driver.get("https://applitools.github.io/demo/TestPages/VisualGridTestPage/")
    eyes1.open(
        driver,
        "Applitools Eyes Python SDK",
        "TestDoubleOpenCheckCloseAsyncWithDifferentInstances_VG",
        dict(width=1200, height=800),
    )
    eyes1.check("Step 1", Target.window().fully().ignore_displacements(False))
    eyes1.close_async()

    eyes2 = Eyes(vg_runner)
    eyes2.open(
        driver,
        "Applitools Eyes Python SDK",
        "TestDoubleOpenCheckCloseAsyncWithDifferentInstances_VG",
        dict(width=1200, height=800),
    )
    eyes2.check("Step 2", Target.window().fully().ignore_displacements(False))
    eyes2.close_async()

    all_test_results = vg_runner.get_all_test_results(False)
    assert len(all_test_results.all_results) == 2
