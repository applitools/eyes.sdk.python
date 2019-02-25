import mock
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

from applitools.selenium import EyesWebDriver


@pytest.fixture
def driver_mock():
    driver = mock.Mock(EyesWebDriver)
    driver.driver = mock.Mock(WebDriver)

    desired_capabilities = {"platformName": ""}
    driver.desired_capabilities = desired_capabilities
    driver.driver.desired_capabilities = desired_capabilities

    # need to configure below
    driver.driver.execute_script = mock.Mock(side_effect=WebDriverException())
    return driver
