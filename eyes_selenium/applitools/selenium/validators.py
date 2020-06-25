from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement

from applitools.common.validators import *  # noqa
from applitools.selenium.webelement import EyesWebElement


def is_webelement(elm):
    return (
        isinstance(elm, EyesWebElement)
        or isinstance(elm, SeleniumWebElement)
        or isinstance(getattr(elm, "_element", None), SeleniumWebElement)
    )
