import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from applitools.selenium import Target

pytestmark = [
    pytest.mark.platform("Linux"),
    pytest.mark.viewport_size({"width": 700, "height": 460}),
]


@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/VisualGridTestPage/duplicates.html"
)
@pytest.mark.test_suite_name("Eyes Selenium SDK - Duplicates")
def test_duplicatedIFrames(eyes_opened):
    eyes_opened.driver.switch_to.frame(2)
    wait = WebDriverWait(eyes_opened.driver, 30)
    wait.until(EC.visibility_of_element_located((By.ID, "p2")))
    eyes_opened.driver.switch_to.default_content()
    eyes_opened.check_window("Duplicated Iframes")


@pytest.mark.skip
@pytest.mark.viewport_size({"width": 1024, "height": 768})
@pytest.mark.test_suite_name("Eyes Selenium SDK - ACME")
@pytest.mark.test_page_url("https://afternoon-savannah-68940.herokuapp.com/#")
def test_acme_login(eyes_opened):
    username = eyes_opened.driver.find_element_by_id("username")
    username.click()
    username.send_keys("adamC")
    password = eyes_opened.driver.find_element_by_id("password")
    password.click()
    password.send_keys("MySecret123?")
    eyes_opened.check(Target.region(username), Target.region(password))
