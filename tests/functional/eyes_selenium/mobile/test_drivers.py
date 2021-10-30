import pytest
from appium import webdriver as appium_webdriver
from selenium import webdriver as selenium_webdriver


@pytest.fixture
def webdriver_module():
    return appium_webdriver


@pytest.mark.platform("Android")
@pytest.mark.test_page_url("https://applitools.com/helloworld")
@pytest.mark.parametrize(
    "eyes",
    [{"webdriver_module": appium_webdriver}, {"webdriver_module": selenium_webdriver}],
    indirect=True,
    ids=lambda o: "with Appium"
    if o["webdriver_module"].__name__.startswith("appium.")
    else "with Selenium",
)
def test_selenium_and_appium_work(eyes, sauce_galaxy_s9_android9_driver):
    eyes.open("TestSeleniumAndAppiumWork")
    eyes.check_window("Home")
    eyes.close()
