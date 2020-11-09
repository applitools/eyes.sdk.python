import pytest
from mock import MagicMock, patch
from selenium.webdriver.remote.webelement import WebElement

from applitools.common import CoordinatesType, Point, Region
from applitools.selenium import Eyes
from applitools.selenium.useragent import UserAgent
from applitools.selenium.webelement import EyesWebElement, adapt_element


@pytest.fixture
def eyes():
    return Eyes()


@pytest.fixture
def eyes_element_mock(driver_mock):
    element_mock = MagicMock(WebElement)
    eyes_element_mock = MagicMock(EyesWebElement)
    eyes_element_mock.element = element_mock
    eyes_element_mock.driver = driver_mock
    eyes_element_mock.eyes = eyes
    return eyes_element_mock


def test_mobilesafariwebelement(eyes, driver_mock, eyes_element_mock):
    eyes.configure.is_simulator = True
    eyes_element_mock.element.location = Point(0, 10)
    eyes_element_mock.element.rect = dict(x=0, y=0, width=600, height=400)

    driver_mock.user_agent = UserAgent(os="iOS", browser="Mobile Safari")

    mobile_safari_element = adapt_element(eyes_element_mock)
    with patch(
        "applitools.selenium.webelement.eyes_selenium_utils.get_current_position",
        return_value=Point(0, 50),
    ):
        assert mobile_safari_element.location == Point(0, 60)
        assert mobile_safari_element.rect == dict(x=0, y=60, width=600, height=400)
        assert mobile_safari_element.bounds == Region(
            0, 60, 1, 1, CoordinatesType.CONTEXT_RELATIVE
        )


def test_mobileandroidebelement(eyes, driver_mock, eyes_element_mock):
    eyes.configure.is_simulator = True
    driver_mock.user_agent = UserAgent(os="Android", browser="Chrome Mobile")

    mobile_chrome_element = adapt_element(eyes_element_mock)
    assert mobile_chrome_element.element._w3c
