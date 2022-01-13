from __future__ import absolute_import

from appium.webdriver import WebElement as AppiumWebElement
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebElement


def is_list_or_tuple(elm):
    return isinstance(elm, (list, tuple))


def is_webelement(elm):

    return isinstance(
        elm,
        (SeleniumWebElement, AppiumWebElement, EventFiringWebElement),
    )
