from applitools.selenium import ClassicRunner, Eyes, VisualGridRunner


def test_create_open_check_close_eyes(local_chrome_driver):
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/SimpleTestPage"
    )
    eyes = Eyes()
    eyes.configure.set_hide_scrollbars(False)
    eyes.open(
        local_chrome_driver,
        "USDK Test",
        "Test create open eyes",
        {"width": 800, "height": 600},
    )
    check_result = eyes.check_window()
    eyes.close(False)

    assert check_result.as_expected


def test_create_open_check_close_vg_eyes(local_chrome_driver):
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/SimpleTestPage"
    )
    runner = VisualGridRunner()
    eyes = Eyes(runner)
    eyes.open(
        local_chrome_driver,
        "USDK Test",
        "Test create open VG eyes",
        {"width": 800, "height": 600},
    )
    check_result = eyes.check_window()
    eyes.close_async()
    all_results = runner.get_all_test_results().all_results

    assert check_result is None
    assert len(all_results) == 1
    assert all_results[0].test_results.is_passed


def test_open_abort_eyes(local_chrome_driver):
    eyes = Eyes()
    eyes.open(local_chrome_driver, "USDK Test", "Test create abort eyes")

    abort_result = eyes.abort()

    assert len(abort_result) == 1
    assert abort_result[0].is_failed
    assert abort_result[0].is_aborted


def test_open_close_abort_eyes(local_chrome_driver):
    eyes = Eyes()
    eyes.open(local_chrome_driver, "USDK Test", "Test create close abort eyes")

    eyes.close(False)
    abort_result = eyes.abort()

    assert abort_result is None


def test_run_test_delete_result(local_chrome_driver):
    eyes = Eyes()
    eyes.open(local_chrome_driver, "USDK Test", "Test run_test_delete_result")
    eyes.check_window()
    result = eyes.close(False)
    result.delete()


def test_get_all_test_results(local_chrome_driver):
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/SimpleTestPage"
    )
    runner = ClassicRunner()
    eyes1 = Eyes(runner)
    eyes1.configure.set_hide_scrollbars(False)
    eyes1.open(local_chrome_driver, "USDK Test", "Test get all test results 1")
    eyes1.check_window()
    results = [eyes1.close()]
    eyes2 = Eyes(runner)
    eyes2.configure.set_hide_scrollbars(False)
    eyes2.open(local_chrome_driver, "USDK Test", "Test get all test results 2")
    eyes2.check_window()
    results.append(eyes2.close())

    all_results = runner.get_all_test_results()

    assert len(all_results) == 2
    assert results[0] == all_results[0].test_results
    assert results[1] == all_results[1].test_results


def test_get_all_vg_test_results(local_chrome_driver):
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/SimpleTestPage"
    )
    runner = VisualGridRunner()
    eyes1 = Eyes(runner)
    eyes1.open(
        local_chrome_driver,
        "USDK Test",
        "Test get all vg test results 1",
        {"width": 800, "height": 600},
    )
    eyes1.check_window()
    results = [eyes1.close()]
    eyes2 = Eyes(runner)
    eyes2.open(
        local_chrome_driver,
        "USDK Test",
        "Test get all vg test results 2",
        {"width": 800, "height": 600},
    )
    eyes2.check_window()
    results.append(eyes2.close())

    all_results = runner.get_all_test_results()

    assert len(all_results) == 2
    assert results[0] == all_results[0].test_results
    assert results[1] == all_results[1].test_results
