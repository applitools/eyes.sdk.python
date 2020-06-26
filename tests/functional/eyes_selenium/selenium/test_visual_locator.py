import pytest
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver import webdriver as appium_webdriver

from applitools.common import Region
from applitools.core import VisualLocator
from applitools.selenium import Eyes, ClassicRunner, VisualGridRunner


@pytest.mark.parametrize("eyes_runner", [ClassicRunner(), VisualGridRunner(1)])
def test_visual_locator(driver, eyes_runner):
    driver.get("https://applitools.github.io/demo/TestPages/FramesTestPage/")
    eyes = Eyes(eyes_runner)
    test_name = "testVisualLocators"
    if isinstance(eyes_runner, VisualGridRunner):
        test_name += "_VG"
    eyes.open(driver, "Applitools Eyes SDK", test_name)

    result = eyes.locate(VisualLocator.name("applitools_title"))
    eyes.close_async()

    assert len(result) == 1
    assert result["applitools_title"][0] == Region(2, 11, 173, 58)


@pytest.mark.platform("Android")
@pytest.mark.capabilities(
    **{
        "app": "https://applitools.bintray.com/Examples/app-android.apk",
        "clearSystemFiles": True,
        "noReset": True,
        "browserName": "",
        "automationName": "UiAutomator2",
        "platformName": "Android",
        "platformVersion": "6.0",
        "appiumVersion": "1.13.0",
        "deviceName": "Android Emulator",
        "deviceOrientation": "portrait",
    }
)
@pytest.mark.eyes_config(hide_scrollbars=False)
@pytest.mark.driver_config(webdriver_module=appium_webdriver)
def test_android_native_visual_locators(eyes, driver):
    eyes.open(driver, "Android Test Apps", "Test Visual Locators")
    eyes.check_window("Launch screen test")
    locators = eyes.locate(
        VisualLocator.names("list_view_locator", "scroll_view_locator")
    )
    assert locators["list_view_locator"]

    list_view_locator = locators["list_view_locator"][0]
    click_location = list_view_locator.location
    action_press = (
        TouchAction(driver)
        .press(x=click_location.x / 2, y=click_location.y / 2)
        .wait(500)
        .release()
        .perform()
    )
    eyes.check_window("ListView screen")
    eyes.close()
