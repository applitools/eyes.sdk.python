from selenium.webdriver.common.by import By

from applitools.selenium import EyesWebDriver


def test_new_tab(eyes, driver):
    driver.get("https://the-internet.herokuapp.com/windows")
    driver.find_element_by_xpath("//a[contains(@href, 'new')]").click()

    # Switch to other tab / close / switch to the original tab
    driver.switch_to.window(driver.window_handles[1])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    # Now use the eyes driver for the same thing...
    eyes_driver = EyesWebDriver(driver, eyes)
    eyes_driver.get("https://the-internet.herokuapp.com/windows")
    eyes_driver.find_element_by_xpath("//a[contains(@href, 'new')]").click()

    eyes_driver.switch_to.window(eyes_driver.window_handles[1])
    eyes_driver.close()
    eyes_driver.switch_to.window(eyes_driver.window_handles[0])


def test_element_find_element(eyes, driver):
    driver.get("https://applitools.com/")
    # Locate element
    element = driver.find_element_by_xpath("//div[@class='content']")
    element.find_element(By.XPATH, "//a[contains(@href, " "'request-demo')]").click()

    eyes_driver = EyesWebDriver(driver, eyes)
    # Navigate the browser to the "hello world!" web-site.
    eyes_driver.get("https://applitools.com/")

    # Locate element
    element = eyes_driver.find_element_by_xpath("//div[@class='content']")
    element.find_element(By.XPATH, "//a[contains(@href, " "'request-demo')]").click()
