from appium.webdriver import WebElement as AppiumWebElement
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebElement

from applitools.common.validators import *  # noqa
from applitools.selenium.webelement import EyesWebElement


def is_webelement(elm):
    def check(elem):
        return isinstance(
            elm,
            (
                EyesWebElement,
                SeleniumWebElement,
                AppiumWebElement,
                EventFiringWebElement,
            ),
        )

    return check(elm) or check(getattr(elm, "_element", None))
