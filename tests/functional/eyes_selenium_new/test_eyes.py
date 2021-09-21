from applitools.selenium import ClassicRunner, Eyes, VisualGridRunner


def test_create_open_eyes(local_chrome_driver):
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/SimpleTestPage"
    )
    eyes = Eyes()
    eyes.open(local_chrome_driver, "USDK Test", "Test create open eyes")
    check_result = eyes.check_window()
    close_result = eyes.close()

    assert check_result.as_expected
    assert len(close_result) == 1
    assert close_result[0].is_passed


def test_create_open_vg_eyes(local_chrome_driver):
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/SimpleTestPage"
    )
    runner = VisualGridRunner()
    eyes = Eyes(runner)
    eyes.open(local_chrome_driver, "USDK Test", "Test create open VG eyes")
    check_result = eyes.check_window()
    close_result = eyes.close()

    assert check_result.as_expected is None
    assert len(close_result) == 1
    assert close_result[0].is_passed


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

    eyes.close()
    abort_result = eyes.abort()

    assert abort_result is None
