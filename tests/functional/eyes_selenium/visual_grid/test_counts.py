import pytest

from applitools.selenium import (
    BrowserType,
    Configuration,
    Eyes,
    Target,
)

pytestmark = [
    pytest.mark.platform("Linux"),
    pytest.mark.test_suite_name("Eyes Selenium SDK - Fluent API"),
    pytest.mark.viewport_size({"width": 700, "height": 460}),
    pytest.mark.test_page_url("https://applitools.com/helloworld"),
]


@pytest.fixture
def eyes(vg_runner, batch_info):
    eyes = Eyes(vg_runner)
    eyes.send_dom = False
    return eyes


def test_vg_tests_count_1(eyes, batch_info, driver):
    eyes.batch = batch_info
    eyes.open(
        driver, "Test Count", "Test_VGTestsCount_1", {"width": 640, "height": 480}
    )
    eyes.check("Test", Target.window())
    eyes.close()
    results_summary = eyes._runner.get_all_test_results()
    assert results_summary.size() == 1


def test_vg_tests_count_2(eyes, batch_info, driver):
    config = (
        Configuration()
        .set_batch(batch_info)
        .add_browser(900, 600, BrowserType.CHROME)
        .add_browser(1024, 768, BrowserType.CHROME)
    )
    eyes.set_configuration(config)
    eyes.open(driver, "Test Count", "Test_VGTestsCount_2")
    eyes.check("Test", Target.window())
    eyes.close()
    results_summary = eyes._runner.get_all_test_results()
    assert results_summary.size() == 2


def test_vg_tests_count_3(eyes, batch_info, driver):
    config = (
        Configuration()
        .set_batch(batch_info)
        .add_browser(900, 600, BrowserType.CHROME)
        .add_browser(1024, 768, BrowserType.CHROME)
        .set_app_name("Test Count")
        .set_test_name("Test_VGTestsCount_3")
    )
    eyes.set_configuration(config)
    eyes.open(driver)
    eyes.check("Test", Target.window())
    eyes.close()
    results_summary = eyes._runner.get_all_test_results()
    assert results_summary.size() == 2


def test_vg_tests_count_4(eyes, batch_info, driver):
    config = (
        Configuration()
        .set_batch(batch_info)
        .set_app_name("Test Count")
        .set_test_name("Test_VGTestsCount_4")
    )
    eyes.set_configuration(config)
    eyes.open(driver)
    eyes.check("Test", Target.window())
    eyes.close()
    results_summary = eyes._runner.get_all_test_results()
    assert results_summary.size() == 1


def test_vg_tests_count_5(eyes, batch_info, driver):
    config = (
        Configuration()
        .set_batch(batch_info)
        .add_browser(900, 600, BrowserType.CHROME)
        .add_browser(1024, 768, BrowserType.CHROME)
    )
    eyes.set_configuration(config)
    eyes.open(
        driver, "Test Count", "Test_VGTestsCount_5", {"width": 640, "height": 480}
    )
    eyes.check("Test", Target.window())
    eyes.close()
    results_summary = eyes._runner.get_all_test_results()
    assert results_summary.size() == 2
