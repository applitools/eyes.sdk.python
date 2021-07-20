from unittest.mock import Mock

import pytest
from EyesLibrary import CheckSettingsKeywords
from selenium.webdriver.remote.webelement import WebElement

from applitools.common import Region
from applitools.selenium.fluent import SeleniumCheckSettings


@pytest.fixture()
def check_settings():
    return CheckSettingsKeywords(Mock())


@pytest.fixture()
def web_element():
    return Mock(WebElement)


def test_ignore_region_by_coordinates(check_settings):
    res = SeleniumCheckSettings().ignore(Region(23, 44, 55, 66))
    assert res == check_settings.ignore_region_by_coordinates(23, 44, 55, 66)


def test_ignore_region_by_coordinates_target(check_settings):
    org = check_settings.ignore_region_by_coordinates(11, 111, 11, 11)
    res = (
        SeleniumCheckSettings()
        .ignore(Region(11, 111, 11, 11))
        .ignore(Region(23, 44, 55, 66))
    )
    assert res == check_settings.ignore_region_by_coordinates(23, 44, 55, 66, org)


def test_ignore_region(check_settings, web_element):
    res = SeleniumCheckSettings().ignore("//selector")
    assert res == check_settings.ignore_region("//selector")
    res = SeleniumCheckSettings().ignore(web_element)
    assert res == check_settings.ignore_region(web_element)


def test_layout_region_by_coordinates(check_settings):
    res = SeleniumCheckSettings().layout(Region(23, 44, 55, 66))
    assert res == check_settings.layout_region_by_coordinates(23, 44, 55, 66)


def test_layout_region(check_settings, web_element):
    res = SeleniumCheckSettings().ignore("//selector")
    assert res == check_settings.ignore_region("//selector")
    res = SeleniumCheckSettings().ignore(web_element)
    assert res == check_settings.ignore_region(web_element)


def test_floating_region_by_coordinates(check_settings):
    res = SeleniumCheckSettings().floating(34, Region(23, 44, 55, 66))
    assert res == check_settings.layout_region_by_coordinates(23, 44, 55, 66)


def test_floating_region(check_settings, web_element):
    res = SeleniumCheckSettings().ignore("//selector")
    assert res == check_settings.ignore_region("//selector")
    res = SeleniumCheckSettings().ignore(web_element)
    assert res == check_settings.ignore_region(web_element)
