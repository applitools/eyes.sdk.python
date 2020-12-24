import pytest

from applitools.common import EyesError, Point, RectangleSize
from applitools.selenium import BrowserType, Configuration, Eyes, Target


def test_get_all_test_results(vg_runner, driver):
    eyes1 = Eyes(vg_runner)
    eyes2 = Eyes(vg_runner)
    eyes1.configuration.add_browser(800, 600, BrowserType.CHROME)
    eyes2.configuration.add_browser(700, 500, BrowserType.FIREFOX)

    driver.get("https://demo.applitools.com")
    eyes1.open(driver, "Python | VisualGrid", "TestClose1")
    eyes2.open(driver, "Python | VisualGrid", "TestClose2")

    eyes1.check_window()
    eyes2.check_window()

    eyes1.close_async()
    eyes2.close_async()

    results = vg_runner.get_all_test_results(False)
    print(results)


def test_abort_eyes(vg_runner, driver):
    eyes = Eyes(vg_runner)
    eyes.configuration.add_browser(800, 600, BrowserType.CHROME)
    driver.get("https://demo.applitools.com")
    eyes.open(driver, "Python | VisualGrid", "TestAbortVGEyes")
    eyes.check_window()
    eyes.abort()


def test_vgwith_bad_webhook(vg_runner, driver):
    eyes = Eyes(vg_runner)
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
        vg_runner.get_all_test_results()

    assert e
    assert "failed to run before_capture_screenshot hook script" in str(e)


def test_image_position_in_active_frame_forwarded_to_match_window(
    spy, vg_runner, fake_connector_class, driver
):
    eyes = Eyes(vg_runner)
    match_spy = spy(fake_connector_class, "match_window")
    eyes.server_connector = fake_connector_class()
    eyes.configuration.add_browser(800, 600, BrowserType.CHROME)
    driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage/index.html")

    eyes.open(driver, "a", "b")
    eyes.check(Target.window())
    eyes.close(False)
    vg_runner.get_all_test_results()

    assert match_spy.call_args.args[2].app_output.location == Point(1, 2)
