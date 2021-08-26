import pytest
from mock import Mock
from selenium.webdriver.remote.webelement import WebElement


@pytest.fixture
def defined_keywords():
    return ["Ignore Region", "Ignore Region By Coordinates"]


@pytest.fixture
def web_element():
    return Mock(WebElement)
