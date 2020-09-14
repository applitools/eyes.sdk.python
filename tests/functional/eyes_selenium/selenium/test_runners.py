import pytest

from applitools.selenium import (
    BatchInfo,
    ClassicRunner,
    Configuration,
    Eyes,
    StitchMode,
    Target,
    VisualGridRunner,
    logger,
)


def test_classic_runner_works_normally(driver):
    classic_runner = ClassicRunner()
    eyes = Eyes(classic_runner)
    driver.get("https://applitools.github.io/demo/TestPages/FramesTestPage/")
    eyes.open(
        driver,
        "Applitools Eyes Java SDK",
        "Classic Runner Test",
        dict(width=1200, height=800),
    )
    eyes.check("Step 1", Target.window())
    eyes.close(False)
    print(classic_runner.get_all_test_results())


def test_classic_runner_raise_exception(driver):
    classic_runner = ClassicRunner()
    eyes = Eyes(classic_runner)
    eyes.open(
        driver,
        "Applitools Eyes Java SDK",
        "Classic Runner Test",
        dict(width=1200, height=800),
    )
    eyes.check("Step 1", Target.window())
    logger.info(str(eyes.close(False)))
    with pytest.raises(Exception):
        classic_runner.get_all_test_results()


def test_eyes_none_runner(driver):
    eyes = Eyes(None)
    eyes.configure.hide_scrollbars = True
    driver.get("https://applitools.github.io/demo/TestPages/FramesTestPage/")
    eyes.open(
        driver, "Eyes Selenium SDK - Null Runner", "TestSeleniumEyesWithNullRunner"
    )
    eyes.check_window()
    eyes.close()


@pytest.mark.parametrize(
    "runner",
    [ClassicRunner()],
    ids=lambda o: "VG" if isinstance(o, VisualGridRunner) else "CR",
)
def test_eyes_runner(driver, runner):
    eyes = Eyes(runner)
    eyes2 = Eyes(runner)
    batch_info = BatchInfo("Runner Testing")
    config = (
        Configuration()
        .set_send_dom(True)
        .set_hide_scrollbars(True)
        .set_stitch_mode(StitchMode.CSS)
        .set_batch(batch_info)
    )
    eyes.set_configuration(config)
    eyes2.set_configuration(config)
    driver.get(
        "http://applitools.github.io/demo/TestPages/VisualGridTestPage/index.html"
    )
    eyes.add_property(
        "Runner", "VisualGrid" if isinstance(runner, VisualGridRunner) else "Selenium"
    )
    eyes.open(
        driver,
        "Applitools Eyes Java SDK",
        "Classic Runner Test",
        dict(width=1200, height=800),
    )
    eyes2.open(
        driver,
        "Applitools Eyes Java SDK",
        "Classic Runner 2 Test",
        dict(width=1200, height=800),
    )

    eyes.check("Step 1", Target.window().fully().ignore_displacements(False))
    eyes2.check("Step 1", Target.window().fully().ignore_displacements(False))

    eyes.close_async()

    eyes.open(
        driver,
        "Applitools Eyes Java SDK",
        "Classic Runner Test",
        dict(width=1200, height=800),
    )
    eyes.check("Step 2", Target.window().fully().ignore_displacements(False))
    eyes.close_async()
    eyes2.close(True)

    driver.quit()
    all_tests_results = runner.get_all_test_results()
    if len(all_tests_results.all_results) != 3:
        raise Exception
