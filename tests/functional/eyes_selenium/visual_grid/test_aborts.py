import pytest

from applitools.common import EyesError, RectangleSize
from applitools.selenium import Eyes


def test_get_all_tests_results_timeout(driver, vg_runner, batch_info):
    eyes = Eyes(vg_runner)
    eyes.configure.test_name = "GetAllTestsResultsTimeout"
    eyes.configure.app_name = "Visual Grid Render Test"
    eyes.configure.batch = batch_info
    eyes.configure.viewport_size = RectangleSize(1024, 768)
    driver.get("https://demo.applitools.com")
    eyes.open(driver)
    eyes.check_window()
    eyes.close_async()
    with pytest.raises(EyesError):
        vg_runner.get_all_test_results(False, 0.001)
