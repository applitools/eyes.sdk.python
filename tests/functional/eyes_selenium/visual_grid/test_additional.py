from applitools.selenium import (
    Eyes,
    Configuration,
    BrowserType,
    Target,
)


def test_check_element_and_window_in_sequence(driver, eyes, batch_info, vg_runner):
    driver.get(
        "https://applitools.github.io/demo/TestPages/VisualGridTestPage/index.html"
    )
    eyes = Eyes(vg_runner)
    eyes.set_configuration(
        Configuration(
            test_name="TestCheckElementAndWindow",
            app_name="Visual Grid Additional Test",
            batch=batch_info,
        ).add_browser(1200, 800, BrowserType.CHROME)
    )
    eyes.open(driver)
    eyes.check("check element", Target.region("#scroll1"))
    eyes.check("check window", Target.window())
    eyes.close_async()
    vg_runner.get_all_test_results()
