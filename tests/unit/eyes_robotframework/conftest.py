import pytest
from AppiumLibrary import AppiumLibrary
from mock import Mock
from selenium.webdriver.remote.webelement import WebElement
from SeleniumLibrary import SeleniumLibrary

from applitools.selenium import Eyes
from EyesLibrary import EyesLibrary, LocatorConverter, SelectedRunner


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


@pytest.fixture
def eyes_library(defined_keywords):
    eyes_lib = Mock(EyesLibrary)
    eyes_lib.current_eyes = Mock(Eyes)
    eyes_lib.keywords = {k: "" for k in defined_keywords}
    return eyes_lib


@pytest.fixture
def appium_library():
    return Mock(AppiumLibrary)


@pytest.fixture
def selenium_library():
    return Mock(SeleniumLibrary)


@pytest.fixture
def eyes_library_with_selenium(eyes_library, selenium_library):
    eyes_library.selected_runner = SelectedRunner.web
    eyes_library.current_library = selenium_library
    eyes_library._locator_converter = LocatorConverter(eyes_library)
    return eyes_library


@pytest.fixture
def eyes_library_with_appium(eyes_library, appium_library):
    eyes_library.selected_runner = SelectedRunner.mobile_native
    eyes_library.current_library = appium_library
    eyes_library._locator_converter = LocatorConverter(eyes_library)
    return eyes_library
