import pytest
from selenium.webdriver.support.wait import WebDriverWait

from applitools.selenium import Eyes, Target

pytestmark = [
    pytest.mark.test_page_url(
        "https://applitools.github.io/demo/TestPages/VisualGridTestPage"
    ),
]


def test_VG_RCA_config(chrome_driver, vg_runner):
    eyes = Eyes(vg_runner)
    eyes.open(chrome_driver, "Test Visual Grid", "Test RCA Config")
    eyes.send_dom = True
    eyes.check("", Target.window())
    eyes.close()
    vg_runner.get_all_test_results()


def test_VG_RCA_fluent(chrome_driver, vg_runner):
    eyes = Eyes(vg_runner)
    chrome_driver.switch_to.frame("iframe")
    WebDriverWait(chrome_driver, 30)
    chrome_driver.switch_to.default_content()

    eyes.open(chrome_driver, "Test Visual Grid", "Test RCA Fluent")
    eyes.send_dom = True
    eyes.check("", Target.window().send_dom(True))
    eyes.close()
    vg_runner.get_all_test_results()
