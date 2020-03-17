from applitools.selenium import (
    Eyes,
    Configuration,
    BrowserType,
    Target,
)


def test_check_element_and_window_in_sequence(driver, eyes, batch_info, vg_runner):
    driver.get("https://demo.applitools.com")
    eyes = Eyes(vg_runner)
    eyes.set_configuration(
        Configuration(
            test_name="TestCheckElementAndWindow",
            app_name="Visual Grid Additional Test",
            batch=batch_info,
        ).add_browser(1024, 768, BrowserType.CHROME)
    )
    eyes.open(driver)
    eyes.check_window("Step 1")
    eyes.check(
        "Step 2",
        Target.region("body > div > div").layout(
            "body > div > div > form > div:nth-child(1)"
        ),
    )
    eyes.check(
        "Step 3", Target.window().layout("body > div > div > form > div:nth-child(1)"),
    )
    eyes.close_async()
    res = vg_runner.get_all_test_results()
