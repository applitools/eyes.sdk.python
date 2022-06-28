from __future__ import absolute_import

from typing import TYPE_CHECKING, Dict, List, Text, Union

if TYPE_CHECKING:
    from appium.webdriver import WebElement as AppiumWebElement
    from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement

    from applitools.common.geometry import RectangleSize, Region
    from applitools.core.triggers import ActionTrigger

    ViewPort = Union[Dict[Text, int], RectangleSize]  # typedef
    CodedRegionPadding = Union[int, Dict[Text, int]]  # typedef
    Num = Union[int, float]

    AnyWebElement = Union[SeleniumWebElement, AppiumWebElement]  # typedef

    FrameNameOrId = Text  # typedef
    FrameIndex = int  # typedef
    FrameReference = Union[FrameNameOrId, FrameIndex, AnyWebElement]  # typedef

    # could contain MouseTrigger, TextTrigger
    UserInputs = List[ActionTrigger]  # typedef
    RegionOrElement = Union[AnyWebElement, Region]  # typedef

    SeleniumBy = Text  # typedef
    BySelector = List[SeleniumBy, Text]  # typedef
    CssSelector = Text  # typedef
    REGION_VALUES = Union[Region, CssSelector, AnyWebElement, BySelector]  # typedef
    FLOATING_VALUES = Union[Region, CssSelector, AnyWebElement, BySelector]  # typedef
