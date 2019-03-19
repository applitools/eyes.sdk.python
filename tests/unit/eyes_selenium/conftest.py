import mock
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

from applitools.selenium import EyesWebDriver


@pytest.fixture
def driver_mock():
    driver = mock.Mock(EyesWebDriver)
    driver._driver = mock.Mock(WebDriver)

    desired_capabilities = {"platformName": ""}
    driver.desired_capabilities = desired_capabilities
    driver._driver.desired_capabilities = desired_capabilities

    # need to configure below
    driver._driver.execute_script = mock.Mock(side_effect=WebDriverException())
    return driver
