import pytest as pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

from applitools.common import DesktopBrowserInfo
from applitools.common.selenium import BrowserType
from applitools.core import VisualLocator
from applitools.selenium import (
    ClassicRunner,
    Eyes,
    Target,
    TargetPath,
    VisualGridRunner,
)


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


def test_get_all_vg_test_results_all_desktop_browsers(local_chrome_driver):
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/SimpleTestPage"
    )
    runner = VisualGridRunner(5)
    eyes = Eyes(runner)
    for browser_type in BrowserType:
        eyes.configure.add_browser(DesktopBrowserInfo(800, 600, browser_type))

    eyes.open(
        local_chrome_driver,
        "USDK Test",
        "Test get all vg test results all browsers",
    )
    eyes.check_window()
    eyes.close_async()
    all_results = runner.get_all_test_results()

    assert len(all_results) == 16


def test_check_element_in_shadow(local_chrome_driver):
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/ShadowDOM/index.html"
    )
    with Eyes() as eyes:
        eyes.open(
            local_chrome_driver,
            "USDK Test",
            "Test check element in shadow dom",
            {"width": 800, "height": 600},
        )
        eyes.check(Target.shadow("#has-shadow-root").region("h1"))


def test_check_element_by_id(local_chrome_driver):
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/FramesTestPage/"
    )
    with Eyes() as eyes:
        eyes.open(
            local_chrome_driver,
            "USDK Test",
            "Test check element by id",
            {"width": 800, "height": 600},
        )
        eyes.check(Target.region([By.ID, "overflowing-div"]))


def test_locate_with_missing_locator_returns_empty_result(local_chrome_driver):
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/SimpleTestPage"
    )
    eyes = Eyes()
    eyes.open(
        local_chrome_driver,
        "USDK Test",
        "Test missing locator",
        {"width": 800, "height": 600},
    )
    try:
        located = eyes.locate(VisualLocator.name("non-existing-locator"))
        assert located == {"non-existing-locator": []}
        eyes.close(False)
    finally:
        eyes.abort()


@pytest.mark.parametrize("runner_type", [ClassicRunner, VisualGridRunner])
@pytest.mark.skip("Currently get_all_test_results does not abort eyes")
def test_get_all_test_results_aborts_eyes(runner_type):
    runner = runner_type()
    options = webdriver.ChromeOptions()
    options.headless = True
    with webdriver.Chrome(options=options) as driver:
        driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage/")
        eyes = Eyes(runner)
        eyes.configure.set_hide_scrollbars(False)
        eyes.open(
            driver,
            "USDK Tests",
            "Auto aborted eyes get all test results {}".format(type(runner).__name__),
            {"width": 1024, "height": 768},
        )
        eyes.check_window()

    results = runner.get_all_test_results()
    assert len(results) == 1
