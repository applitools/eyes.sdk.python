import pytest

from applitools.selenium import BrowserType, Configuration, Eyes, Target
from tests.utils import get_session_results


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
        "Step 3", Target.window().ignore("body > div > div > form > div:nth-child(1)")
    )
    eyes.close_async()
    trc = vg_runner.get_all_test_results().all_results[0]
    session_results = get_session_results(eyes.api_key, trc.test_results)
    actual_output = session_results["actualAppOutput"]
    assert len(actual_output[1]["imageMatchSettings"]["layout"]) == 1
    assert actual_output[1]["imageMatchSettings"]["layout"][0] == {
        "left": 80,
        "top": 322,
        "width": 290,
        "height": 65,
    }
    assert len(actual_output[2]["imageMatchSettings"]["ignore"]) == 1
    assert actual_output[2]["imageMatchSettings"]["ignore"][0] == {
        "left": 367,
        "top": 322,
        "width": 290,
        "height": 65,
    }
