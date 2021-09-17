from applitools.selenium import Eyes


def test_create_open_eyes(local_chrome_driver):
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/SimpleTestPage"
    )
    eyes = Eyes()
    eyes.open(local_chrome_driver, "App name", "Test name")
    check_result = eyes.check_window()
    close_result = eyes.close()

    assert check_result
    assert close_result
