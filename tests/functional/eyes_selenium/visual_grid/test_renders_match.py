from applitools.selenium import (
    Configuration,
    Eyes,
    Target,
    VisualGridRunner,
)


def init_eyes(runner, driver, batch_info, test_name, viewport):
    eyes = Eyes(runner)
    sconf = Configuration()
    sconf.set_batch(batch_info)
    sconf.set_viewport_size(viewport)
    sconf.set_app_name("TestRendersMatch")
    sconf.set_test_name(test_name)
    eyes.set_configuration(sconf)
    eyes.open(driver)
    return eyes


def test_success(driver, batch_info):
    visual_grid_runner = VisualGridRunner(10)
    viewport_list = [
        {"width": 800, "height": 600},
        {"width": 700, "height": 500},
        {"width": 1200, "height": 800},
        {"width": 1600, "height": 1200},
    ]
    driver.get("https://www.applitools.com/helloworld")
    try:
        for viewport in viewport_list:
            eyes = init_eyes(None, driver, batch_info, "TestSuccess", viewport)
            eyes.check("", Target.window().fully())
            eyes.close_async()

            eyes = init_eyes(
                visual_grid_runner, driver, batch_info, "TestSuccess", viewport
            )
            eyes.check("", Target.window().fully())
            eyes.close_async()
        results = visual_grid_runner.get_all_test_results()
        assert len(results) == len(viewport_list)
    finally:
        eyes.abort()


def test_failure(driver, batch_info):
    visual_grid_runner = VisualGridRunner(10)
    viewport_list = [
        {"width": 800, "height": 600},
        {"width": 700, "height": 500},
        {"width": 1200, "height": 800},
        {"width": 1600, "height": 1200},
    ]
    driver.get("https://www.applitools.com/helloworld")
    try:
        results_total = 0
        for viewport in viewport_list:
            eyes = init_eyes(None, driver, batch_info, "TestFailure", viewport)
            eyes.check("", Target.window().fully())
            eyes.close()

            eyes = init_eyes(
                visual_grid_runner, driver, batch_info, "TestFailure", viewport
            )
            eyes.check("", Target.window().fully())
            eyes.close()
            results = visual_grid_runner.get_all_test_results()
            results_total += len(results)
        assert results_total == 4
    finally:
        eyes.abort()
