from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from applitools.selenium import EyesWebDriver
from tests.utils import get_resource_path


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
    driver.get("https://applitools.com/helloworld/")
    # Locate element
    element = driver.find_element_by_xpath("//div[@class='demo-page center']")
    element.find_element(By.XPATH, "//a[contains(@href, 'diff1')]").click()

    eyes_driver = EyesWebDriver(driver, eyes)
    # Navigate the browser to the "hello world!" web-site.
    eyes_driver.get("https://applitools.com/helloworld/")

    # Locate element
    element = eyes_driver.find_element_by_xpath("//div[@class='demo-page center']")
    element.find_element(By.XPATH, "//a[contains(@href, 'diff1')]").click()


def test_eyes_element_and_element_with_Select(eyes, driver):
    driver.get("file://{}".format(get_resource_path("unit/multiple-selects.html")))

    eyes_driver = EyesWebDriver(driver, eyes)

    element = driver.find_element_by_xpath("//select[contains(@id, 'device')]")
    sel_select = Select(element)
    sel_options = sel_select.options
    for index, option in enumerate(sel_options):
        option.click()

    eyes_element = eyes_driver.find_element_by_xpath(
        "//select[contains(@id, 'device')]"
    )
    eyes_select = Select(eyes_element)
    eyes_options = eyes_select.options
    for index, option in enumerate(eyes_options):
        option.click()

    assert sel_options == eyes_options
    assert sel_select.all_selected_options == eyes_select.all_selected_options
    assert sel_select.first_selected_option == eyes_select.first_selected_option


def test_find_inside_element(eyes, driver):
    driver.get("file://{}".format(get_resource_path("unit/multiple-selects.html")))

    eyes_driver = EyesWebDriver(driver, eyes)
    element = driver.find_element_by_xpath("//select[contains(@id, 'device')]")
    eyes_element = eyes_driver.find_element_by_xpath(
        "//select[contains(@id, 'device')]"
    )
    assert element.find_element_by_xpath(
        '//option[@selected="selected"]'
    ) == eyes_element.find_element_by_xpath('//option[@selected="selected"]')
    assert element.find_elements(By.TAG_NAME, "options") == eyes_element.find_elements(
        By.TAG_NAME, "options"
    )


def test_driver_and_element_dir(eyes, driver):
    driver.get("https://applitools.com/helloworld/")

    eyes_driver = EyesWebDriver(driver, eyes)
    _dir = dir(eyes_driver)
    assert all(elem in _dir for elem in dir(driver) if not elem.startswith("_"))

    element = driver.find_element_by_xpath("//div[@class='demo-page center']")
    eyes_element = eyes_driver.find_element_by_xpath("//div[@class='demo-page center']")
    _dir = dir(eyes_element)
    assert all(elem in _dir for elem in dir(element) if not elem.startswith("_"))
