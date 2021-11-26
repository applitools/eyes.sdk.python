import pytest

from applitools.common.geometry import RectangleSize
from applitools.selenium import Eyes, Target


@pytest.mark.parametrize(
    "target",
    [Target.window(), Target.window().disable_browser_fetching()],
)
def test_fetch_deep_css_chain(driver, vg_runner, target):
    eyes = Eyes(vg_runner)
    driver.get("https://applitools.github.io/demo/TestPages/CorsCssTestPage/")
    eyes.open(
        driver, "Test Visual Grid", "Test Deep CSS chain", RectangleSize(800, 600)
    )

    eyes.check(target)

    eyes.close()
    vg_runner.get_all_test_results()
