import pytest

from applitools.selenium import (
    BrowserType,
    Configuration,
    Eyes,
    Target,
    VisualGridRunner,
)

@pytest.mark.platform("Linux")
@pytest.mark.test_page_url("https://applitools.com/helloworld")
class TestCounts:
    def test_vg_tests_count_1(self, batch_info, driver):
        runner = VisualGridRunner(10)
        eyes = Eyes(runner)
        eyes.send_dom = False
        eyes.batch = batch_info
        eyes.open(driver, "Test Count", "Test_VGTestsCount_1", {"width": 640, "height": 480})
        eyes.check("Test", Target.window())
        eyes.close()
        results_summary = runner.get_all_test_results()
        assert results_summary.size() == 1

    def test_vg_tests_count_2(self, batch_info, driver):
        runner = VisualGridRunner(10)
        eyes = Eyes(runner)
        eyes.send_dom = False
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
        results_summary = runner.get_all_test_results()
        assert results_summary.size() == 2

    def test_vg_tests_count_3(self, batch_info, driver):
        runner = VisualGridRunner(10)
        eyes = Eyes(runner)
        eyes.send_dom = False
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
        results_summary = runner.get_all_test_results()
        assert results_summary.size() == 2

    def test_vg_tests_count_4(self, batch_info, driver):
        runner = VisualGridRunner(10)
        eyes = Eyes(runner)
        eyes.send_dom = False
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
        results_summary = runner.get_all_test_results()
        assert results_summary.size() == 1

    def test_vg_tests_count_5(self, batch_info, driver):
        runner = VisualGridRunner(10)
        eyes = Eyes(runner)
        eyes.send_dom = False
        config = (
            Configuration()
            .set_batch(batch_info)
            .add_browser(900, 600, BrowserType.CHROME)
            .add_browser(1024, 768, BrowserType.CHROME)
        )
        eyes.set_configuration(config)
        eyes.open(driver, "Test Count", "Test_VGTestsCount_5", {"width": 640, "height": 480})
        eyes.check("Test", Target.window())
        eyes.close()
        results_summary = runner.get_all_test_results()
        assert results_summary.size() == 2
