from applitools.selenium import BrowserType, Eyes


def test_get_all_test_results(vg_runner, driver):
    eyes1 = Eyes(vg_runner)
    eyes2 = Eyes(vg_runner)
    eyes1.configuration.add_browser(800, 600, BrowserType.CHROME)
    eyes2.configuration.add_browser(700, 500, BrowserType.FIREFOX)

    driver.get("https://demo.applitools.com")
    eyes1.open(driver, "Python VisualGrid", "TestClose1")
    eyes2.open(driver, "Python VisualGrid", "TestClose2")

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
    eyes.open(driver, "Python VisualGrid", "TestAbortVGEyes")
    eyes.check_window()
    eyes.abort()
