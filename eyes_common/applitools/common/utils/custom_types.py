from __future__ import absolute_import

import typing as tp

if tp.TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement

    from applitools.common.geometry import Region, RectangleSize
    from applitools.selenium.webdriver import EyesWebDriver
    from applitools.selenium.webelement import EyesWebElement

    ViewPort = tp.Union[tp.Dict[tp.Text, int], RectangleSize]
    Num = tp.Union[int, float]

    AnyWebDriver = tp.Union[EyesWebDriver, WebDriver]
    AnyWebElement = tp.Union[EyesWebElement, WebElement]
    FrameReference = tp.Union[tp.Text, int, EyesWebElement, WebElement]
    # could contain MouseTrigger, TextTrigger
    UserInputs = tp.List
    RegionOrElement = tp.Union[EyesWebElement, Region]
