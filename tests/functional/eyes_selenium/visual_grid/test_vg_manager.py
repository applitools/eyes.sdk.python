from applitools.selenium import BrowserType, Eyes


def test_get_all_test_results(vg_runner, driver):
    eyes1 = Eyes(vg_runner)
    eyes2 = Eyes(vg_runner)
    eyes1.configuration.add_browser(800, 600, BrowserType.CHROME)
    eyes2.configuration.add_browser(700, 500, BrowserType.FIREFOX)

    driver.get("https://demo.applitools.com")
    eyes1.open(driver, "Testing1", "TestClose1")
    eyes2.open(driver, "Testing2", "TestClose2")

    eyes1.check_window()
    eyes2.check_window()

    eyes1.close_async()
    eyes2.close_async()

    results = vg_runner.get_all_test_results(False)
    print(results)
