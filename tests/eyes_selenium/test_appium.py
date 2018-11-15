import pytest
from selenium.webdriver.common.by import By


@pytest.mark.platform('Android')
@pytest.mark.capabilities(**{"app": "http://saucelabs.com/example_files/ContactManager.apk",
                             "clearSystemFiles": True,
                             "noReset": True,
                             "browserName": '',
                             })
@pytest.mark.eyes(hide_scrollbars=False)
def test_android_native(eyes, driver):
    eyes.open(driver, "Contacts!", "My first Appium Python test!")
    eyes.check_window("Contact list!")
    eyes.close()


# TODO: add stitch content to check_region in tests below
@pytest.mark.platform('Android')
@pytest.mark.eyes(hide_scrollbars=False)
@pytest.mark.skip
def test_final_application_android(eyes, driver):
    driver = eyes.open(driver, "sample2", "titleicon5")
    driver.get("http://atom:mota@lgi-www-sat.trimm.net/test/upc/title-with-icon.html")
    eyes.check_window("test2")
    element = driver.find_element(By.XPATH, "html/body/div[2]/h1[5]")
    driver.execute_script("arguments[0].scrollIntoView(true);", element.element)
    eyes.check_region(driver.find_element(By.XPATH, "html/body/div[2]/h1[5]"))
    eyes.close()


@pytest.mark.platform('iPhone')
@pytest.mark.eyes(hide_scrollbars=False)
@pytest.mark.skip
def test_final_application_ios(eyes, driver):
    driver = eyes.open(driver, "sample", "IOS")
    driver.get("http://atom:mota@lgi-www-sat.trimm.net/test/ziggo/title-with-icon.html")
    eyes.check_window()
    element = driver.find_element(By.XPATH, "html/body/div[2]")
    driver.execute_script("arguments[0].scrollIntoView(true);", element.element)
    eyes.checkRegion(driver.find_element(By.XPATH, "html/body/div[2]"))
    eyes.close()
