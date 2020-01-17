from selenium.webdriver.support.wait import WebDriverWait

from applitools.selenium import Eyes, BatchInfo, Target

batch_info = BatchInfo("Test Visual Grid RCA")


def test_VG_RCA_config(driver, vg_runner):
    eyes = Eyes(vg_runner)
    eyes.batch = batch_info
    driver.get("https://applitools.github.io/demo/TestPages/VisualGridTestPage")
    eyes.open(driver, "Test Visual Grid", "Test RCA Config")
    eyes.send_dom = True
    eyes.check("", Target.window())
    eyes.close()
    vg_runner.get_all_test_results()


def test_VG_RCA_fluent(driver, vg_runner):
    eyes = Eyes(vg_runner)
    eyes.batch = batch_info
    driver.get("https://applitools.github.io/demo/TestPages/VisualGridTestPage")
    driver.switch_to.frame("iframe")
    WebDriverWait(driver, 30)
    driver.switch_to.default_content()

    eyes.open(driver, "Test Visual Grid", "Test RCA Fluent")
    eyes.send_dom = True
    eyes.check("", Target.window().send_dom(True))
    eyes.close()
    vg_runner.get_all_test_results()
