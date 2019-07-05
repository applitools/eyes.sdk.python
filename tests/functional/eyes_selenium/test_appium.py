import pytest
from appium import webdriver as appium_webdriver
from selenium import webdriver as selenium_webdriver

from applitools.selenium import StitchMode


@pytest.fixture
def webdriver_module():
    return appium_webdriver


@pytest.mark.platform("Android")
@pytest.mark.capabilities(
    **{
        "app": "http://saucelabs.com/example_files/ContactManager.apk",
        "clearSystemFiles": True,
        "noReset": True,
        "browserName": "",
        "automationName": "UiAutomator2",
    }
)
@pytest.mark.eyes(hide_scrollbars=False)
def test_android_native(eyes, driver):
    eyes.open(driver, "Contacts!", "My first Appium Python test!")
    eyes.check_window("Contact list!")
    eyes.close()


@pytest.mark.platform("iOS")
@pytest.mark.capabilities(
    **{
        "app": "http://174.138.1.48/doc/Demo_Application.zip",
        "clearSystemFiles": True,
        "noReset": True,
        "browserName": "",
        "automationName": "XCUITest",
    }
)
@pytest.mark.eyes(hide_scrollbars=False)
def test_ios_native(eyes, driver):
    eyes.open(driver, "Contacts!", "My first Appium Python test!")
    eyes.check_window("Contact list!")
    eyes.close()


@pytest.mark.platform("Android", "iOS")
@pytest.mark.test_page_url("https://applitools.com/helloworld")
@pytest.mark.parametrize(
    "eyes",
    [
        {"force_full_page_screenshot": True, "stitch_mode": StitchMode.CSS},
        {"force_full_page_screenshot": False, "stitch_mode": StitchMode.Scroll},
    ],
    indirect=True,
    ids=lambda o: "with FSP" if o["force_full_page_screenshot"] else "no FSP",
)
def test_final_application(eyes_open):
    eyes, driver = eyes_open
    eyes.check_window("Home")


@pytest.mark.platform("Android", "iOS")
@pytest.mark.test_page_url("https://applitools.com/helloworld")
@pytest.mark.parametrize(
    "eyes",
    [{"webdriver_module": appium_webdriver}, {"webdriver_module": selenium_webdriver}],
    indirect=True,
    ids=lambda o: "with Appium"
    if o["webdriver_module"].__name__.startswith("appium.")
    else "with Selenium",
)
def test_selenium_and_appium_work(eyes_open):
    eyes, driver = eyes_open
    eyes.check_window("Home")
