import pytest

from applitools.common import BatchInfo, StitchMode
from applitools.selenium import ClassicRunner, Eyes, Target, VisualGridRunner, logger


def test_classic_runner_works_normally(driver):
    classic_runner = ClassicRunner()
    eyes = Eyes(classic_runner)
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
    [VisualGridRunner(10), ClassicRunner()],
    ids=lambda o: "VG" if isinstance(o, VisualGridRunner) else "CR",
)
def test_eyes_runner(driver, runner):
    eyes = Eyes(runner)
    eyes2 = Eyes(runner)

    eyes.send_dom = True
    eyes2.send_dom = False
    eyes.stitch_mode = StitchMode.CSS
    eyes2.stitch_mode = StitchMode.CSS

    batch_info = BatchInfo("Runner Testing")
    batch_info.id = "RCA_Batch_ID"
    eyes.batch_info = batch_info
    eyes2.batch_info = batch_info

    driver.get(
        "http://applitools.github.io/demo/TestPages/VisualGridTestPage/index.html"
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
