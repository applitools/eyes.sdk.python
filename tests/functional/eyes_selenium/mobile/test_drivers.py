import pytest
from appium import webdriver as appium_webdriver
from selenium import webdriver as selenium_webdriver

from applitools.common import NewTestError


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
@pytest.mark.capabilities(
    **{
        "browserName": "Chrome",
        "platformName": "Android",
        "platformVersion": "6.0",
        "appiumVersion": "1.13.0",
        "deviceName": "Android Emulator",
        "deviceOrientation": "portrait",
    }
)
def test_selenium_and_appium_work(eyes_opened):
    with pytest.raises(NewTestError):
        eyes_opened.check_window("Home")
