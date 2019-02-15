import pytest
from selenium.webdriver.common.by import By

from applitools.selenium import (
    FloatingBounds,
    FloatingRegion,
    IgnoreRegionBySelector,
    Region,
    StitchMode,
    Target,
)


@pytest.mark.platform("Android")
@pytest.mark.capabilities(
    **{
        "app": "http://saucelabs.com/example_files/ContactManager.apk",
        "clearSystemFiles": True,
        "noReset": True,
        "browserName": "",
    }
)
@pytest.mark.eyes(hide_scrollbars=False)
def test_android_native(eyes, driver):
    eyes.open(driver, "Contacts!", "My first Appium Python test!")
    eyes.check_window("Contact list!")
    eyes.close()


@pytest.mark.platform("Android", "iOS")
@pytest.mark.test_page_url("http://applitools.com")
@pytest.mark.eyes(force_full_page_screenshot=True, stitch_mode=StitchMode.CSS)
def test_final_application(eyes_open):
    eyes, driver = eyes_open
    eyes.check_window(
        "Home",
        target=(
            Target()
            .ignore(IgnoreRegionBySelector(By.CLASS_NAME, "hero-container"))
            .floating(
                FloatingRegion(Region(10, 20, 30, 40), FloatingBounds(10, 0, 20, 10))
            )
        ),
    )

    hero = driver.find_element_by_class_name("hero-container")
    eyes.check_region_by_element(
        hero,
        "Page Hero",
        target=(Target().ignore(Region(20, 20, 50, 50), Region(40, 40, 10, 20))),
    )
