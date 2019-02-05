import pytest
from applitools.selenium import Eyes, Target


@pytest.mark.browser("chrome")
@pytest.mark.platform("Linux")
@pytest.mark.skip("Depending on Fluent API. Not implemented yet")
def test_server_connector(driver):
    eyes = Eyes("https://localhost.applitools.com")
    driver = eyes.open(
        driver, "Python SDK", "TestDelete", {"width": 800, "height": 599}
    )
    driver.get("https://applitools.com/helloworld")
    eyes.check("Hello", Target.window())
    results = eyes.close()
    results.delete()
    eyes.abort_if_not_closed()


@pytest.mark.browser("chrome")
@pytest.mark.platform("Linux")
def test_directly_set_viewport_size(eyes, driver):
    required_viewport = {"width": 450, "height": 300}
    eyes.set_viewport_size(driver, required_viewport)
    driver = eyes.open(driver, "Python SDK", "TestViewPort-DirectlySetViewportt")
    assert required_viewport == eyes.get_viewport_size(driver)
