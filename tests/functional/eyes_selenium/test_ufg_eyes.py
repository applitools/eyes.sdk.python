import pytest

from applitools.common import EyesError
from applitools.common.geometry import RectangleSize
from applitools.selenium import Eyes, Target, VisualGridRunner


@pytest.mark.parametrize(
    "target",
    [Target.window(), Target.window().disable_browser_fetching()],
)
def test_fetch_deep_css_chain(local_chrome_driver, target):
    vg_runner = VisualGridRunner(10)
    eyes = Eyes(vg_runner)
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/CorsCssTestPage/"
    )
    eyes.open(
        local_chrome_driver,
        "Test Visual Grid",
        "Test Deep CSS chain",
        RectangleSize(800, 600),
    )

    eyes.check(target)

    eyes.close()
    vg_runner.get_all_test_results()


def test_get_all_tests_results_timeout(local_chrome_driver, batch_info):
    vg_runner = VisualGridRunner(10)
    eyes = Eyes(vg_runner)
    eyes.configure.test_name = "GetAllTestsResultsTimeout"
    eyes.configure.app_name = "Visual Grid Render Test"
    eyes.configure.batch = batch_info
    eyes.configure.viewport_size = RectangleSize(1024, 768)
    local_chrome_driver.get("https://demo.applitools.com")
    eyes.open(local_chrome_driver)
    eyes.check_window()
    eyes.close_async()
    with pytest.raises(EyesError):
        vg_runner.get_all_test_results(False, 0.001)
