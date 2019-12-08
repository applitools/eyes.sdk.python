from selenium.webdriver.common.by import By

import pytest
from applitools.selenium import StitchMode, Target


@pytest.mark.platform("Linux")
@pytest.mark.skip
def test_wix_site(eyes, driver):
    eyes.match_timeout = 0
    eyes.force_full_page_screenshot = False
    driver = eyes.open(driver, app_name="Python SDK", test_name="Wix example")
    # Sign in to the page
    driver.get(
        "https://eventstest.wixsite.com/events-page-e2e/events/ba837913-7dad-41b9-b530-6c2cbfc4c265"
    )
    iframe_id = "TPAMultiSection_j5ocg4p8iframe"
    driver.switch_to.frame(iframe_id)
    # click register button
    driver.find_element_by_css_selector("[data-hook=get-tickets-button]").click()
    # add one ticket
    driver.find_element_by_css_selector("[data-hook=plus-button]").click()
    # just an example, where it make us some problems with scrolling to top of the frame.
    # eyes.check_region(By.CSS_SELECTOR, "[data-hook=plus-button]");
    eyes.check("", Target.region("[data-hook=plus-button]"))
    eyes.close()


@pytest.mark.platform("Linux", "Windows", "macOS")
@pytest.mark.eyes(match_timeout=0, force_full_page_screenshot=False)
def test_w3schools_iframe(eyes, driver):
    driver = eyes.open(
        driver,
        app_name="Python SDK",
        test_name="W3 Schools frame",
        viewport_size={"width": 800, "height": 600},
    )
    driver.get("https://www.w3schools.com/tags/tryit.asp?filename=tryhtml_iframe")
    eyes.check(
        "Entire Frame", Target.frame("iframeResult").region([By.TAG_NAME, "body"])
    )
    eyes.close()


@pytest.mark.platform("Linux")
@pytest.mark.eyes(stitch_mode=StitchMode.CSS, force_full_page_screenshot=True)
def test_omnicomprgroup(eyes, driver):
    driver = eyes.open(
        driver, "Python SDK", "TestOmnicomprgroup_FPS", {"width": 800, "height": 600}
    )
    driver.get("https://www.omnicomprgroup.com/")
    eyes.check_window()
    eyes.close()


@pytest.mark.platform("Linux")
@pytest.mark.eyes(stitch_mode=StitchMode.CSS, force_full_page_screenshot=True)
def test_nationalgeographic(eyes, driver):
    driver = eyes.open(
        driver,
        "Python SDK",
        "TestNationalgeographic_FPS",
        {"width": 800, "height": 600},
    )
    driver.get(
        "https://www.nationalgeographic.com/photography/proof/2016/05/omar-diop-refugee-mbororo-portraits/?disableAds=true"
    )
    eyes.check_window()
    eyes.close()


@pytest.mark.platform("Linux")
@pytest.mark.eyes(send_dom=False, stitch_mode=StitchMode.CSS)
def test_zachs_app(eyes, driver):
    driver.get("https://www.goodrx.com/xarelto/what-is")
    eyes.open(
        driver,
        app_name="Zachs Python app",
        test_name="I_29263 FF CSS transition FULLY",
        viewport_size={"width": 800, "height": 600},
    )
    proscons_ele = driver.find_element_by_xpath('//*[@id="pros-cons"]/..')
    eyes.check("pros-cons", Target.region(proscons_ele).fully())

    warnings_ele = driver.find_element_by_xpath('//*[@id="warnings"]/..')
    eyes.check("warnings", Target.region(warnings_ele).fully())

    eyes.close()


@pytest.mark.platform("Linux")
@pytest.mark.eyes(
    hide_scrollbars=True, stitch_mode=StitchMode.Scroll, wait_before_screenshots=1
)
def test_duo_v3_default(eyes, driver):
    driver.get(
        "http://front-end-testing.appspot.com/duo_v3_default/secondary_auth?user=noone@atest.com"
    )
    driver = eyes.open(driver, "region", "test region", {"width": 1000, "height": 800})
    eyes.check("Frame", Target.frame("duo_iframe"))
    eyes.close()
