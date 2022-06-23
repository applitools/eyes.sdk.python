import pytest
from AppiumLibrary import AppiumLibrary
from mock import Mock
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from SeleniumLibrary import SeleniumLibrary

from applitools.common.selenium import Configuration
from applitools.selenium import ClassicRunner, Eyes
from EyesLibrary import (
    CheckKeywords,
    ConfigurationKeywords,
    EyesLibrary,
    LocatorConverter,
    SelectedRunner,
    SessionKeywords,
)


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


@pytest.fixture()
def css_selector():
    return "css:#some-id"


@pytest.fixture()
def by_selector():
    return [By.CSS_SELECTOR, "#some-id"]


@pytest.fixture
def eyes_library(defined_keywords):
    eyes_lib = EyesLibrary()
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
    eyes_library._selected_runner = SelectedRunner.web
    eyes_library._configuration = Configuration()
    eyes_library.current_library = selenium_library
    eyes_library._locator_converter = LocatorConverter(eyes_library)
    return eyes_library


@pytest.fixture
def eyes_library_with_appium(eyes_library, appium_library):
    eyes_library._selected_runner = SelectedRunner.mobile_native
    eyes_library._configuration = Configuration()
    eyes_library.current_library = appium_library
    eyes_library._locator_converter = LocatorConverter(eyes_library)
    return eyes_library


@pytest.fixture
def session_keyword(eyes_library_with_selenium):
    eyes_library_with_selenium.eyes_runner = ClassicRunner()
    keyword = SessionKeywords(eyes_library_with_selenium)
    return keyword


@pytest.fixture()
def check_keyword(defined_keywords, eyes_library_with_selenium):
    results = []

    def collect_result(*args):
        check_settings = args[0]
        tag = check_settings.values.name
        results.append((check_settings, tag))

    eyes_library_with_selenium.register_eyes(Mock(Eyes), None)
    eyes_library_with_selenium.current_eyes.check = collect_result
    check = CheckKeywords(eyes_library_with_selenium)
    check.results = results
    return check


@pytest.fixture
def configuration_keyword(eyes_library_with_selenium):
    eyes_library_with_selenium.eyes_runner = ClassicRunner()
    keyword = ConfigurationKeywords(eyes_library_with_selenium)
    return keyword
