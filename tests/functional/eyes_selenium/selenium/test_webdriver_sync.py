from applitools.selenium import EyesWebDriver


def test_iframe_selected_with_raw_selenium_driver_is_synced(eyes, driver):
    driver.get("https://applitools.github.io/demo/TestPages/CorsTestPage/index.html")
    eyes_driver = EyesWebDriver(driver, eyes)

    driver.switch_to.frame(0)
    driver.switch_to.frame(0)
    eyes_driver.ensure_sync_with_underlying_driver()

    assert (
        eyes_driver.frame_chain.peek.scroll_root_element.get_attribute("class")
        == "no-js"
    )


def test_iframe_unselected_with_raw_selenium_driver_is_synced(eyes, driver):
    driver.get("https://applitools.github.io/demo/TestPages/CorsTestPage/index.html")
    eyes_driver = EyesWebDriver(driver, eyes)

    eyes_driver.switch_to.frame(0)
    driver.switch_to.default_content()
    eyes_driver.ensure_sync_with_underlying_driver()

    assert eyes_driver.frame_chain.peek is None
