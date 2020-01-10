import pytest

from applitools.common import RectangleSize, EyesError
from applitools.selenium import BrowserType, Eyes, Configuration, Target


def test_get_all_test_results(eyes_runner, driver):
    eyes1 = Eyes(eyes_runner)
    eyes2 = Eyes(eyes_runner)
    eyes1.configuration.add_browser(800, 600, BrowserType.CHROME)
    eyes2.configuration.add_browser(700, 500, BrowserType.FIREFOX)

    driver.get("https://demo.applitools.com")
    eyes1.open(driver, "Python | VisualGrid", "TestClose1")
    eyes2.open(driver, "Python | VisualGrid", "TestClose2")

    eyes1.check_window()
    eyes2.check_window()

    eyes1.close_async()
    eyes2.close_async()

    results = eyes_runner.get_all_test_results(False)
    print(results)


def test_abort_eyes(eyes_runner, driver):
    eyes = Eyes(eyes_runner)
    eyes.configuration.add_browser(800, 600, BrowserType.CHROME)
    driver.get("https://demo.applitools.com")
    eyes.open(driver, "Python | VisualGrid", "TestAbortVGEyes")
    eyes.check_window()
    eyes.abort()


def test_vgwith_bad_webhook(eyes_runner, driver):
    eyes = Eyes(eyes_runner)
    eyes.configuration = Configuration(
        app_name="Visual Grid Python Tests",
        test_name="Bad Webhook",
        viewport_size=RectangleSize(800, 600),
    )

    eyes.open(driver)
    eyes.check(
        "",
        Target.window()
        .fully()
        .before_render_screenshot_hook("gibberish uncompilable java script"),
    )
    with pytest.raises(EyesError) as e:
        eyes.close()
        eyes_runner.get_all_test_results()

    assert e
    assert "failed to run before_capture_screenshot hook script" in str(e)
