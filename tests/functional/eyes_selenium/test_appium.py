import pytest


@pytest.mark.mobile
@pytest.mark.platform('Android')
@pytest.mark.capabilities(**{"app":              "http://saucelabs.com/example_files/ContactManager.apk",
                             "clearSystemFiles": True,
                             "noReset":          True,
                             "browserName":      '',
                             })
@pytest.mark.eyes(hide_scrollbars=False)
def test_android_native(eyes, driver):
    eyes.open(driver, "Contacts!", "My first Appium Python test!")
    eyes.check_window("Contact list!")
    eyes.close()


@pytest.mark.mobile
@pytest.mark.platform('Android')
@pytest.mark.parametrize('eyes', [
    {'force_full_page_screenshot': True, 'hide_scrollbars': False},
    {'force_full_page_screenshot': False, 'hide_scrollbars': False},
],
                         indirect=True,
                         ids=lambda o: "with FSP" if o['force_full_page_screenshot'] else "no FSP")
@pytest.mark.test_page_url('http://applitools.github.io/demo/TestPages/FramesTestPage/')
def test_final_application_android(eyes_open):
    eyes, driver = eyes_open
    eyes.check_window("test2")
    btn_element = driver.find_element_by_css_selector('button')
    eyes.check_region_by_element(btn_element, stitch_content=True)


@pytest.mark.mobile
@pytest.mark.platform('iOS')
@pytest.mark.parametrize('eyes', [
    {'force_full_page_screenshot': True, 'hide_scrollbars': False},
    {'force_full_page_screenshot': False, 'hide_scrollbars': False},
],
                         indirect=True,
                         ids=lambda o: "with FSP" if o['force_full_page_screenshot'] else "no FSP")
@pytest.mark.test_page_url('http://applitools.github.io/demo/TestPages/FramesTestPage/')
def test_final_application_ios(eyes_open):
    eyes, driver = eyes_open
    eyes.check_window()
    btn_element = driver.find_element_by_css_selector('button')
    eyes.check_region_by_element(btn_element, stitch_content=True)
