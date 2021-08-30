import pytest
from mock import Mock
from selenium.webdriver.remote.webelement import WebElement


@pytest.fixture
def defined_keywords():
    return [
        "Ignore Region By Element",
        "Ignore Region By Coordinates",
        "Fully",
        "Use Dom",
    ]


@pytest.fixture
def web_element():
    return Mock(WebElement)
