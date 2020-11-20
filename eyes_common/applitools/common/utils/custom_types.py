from __future__ import absolute_import

from typing import TYPE_CHECKING, Any, Dict, List, Text, Tuple, Union

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement

    from applitools.common.geometry import RectangleSize, Region
    from applitools.core.triggers import ActionTrigger
    from applitools.selenium.webdriver import EyesWebDriver
    from applitools.selenium.webelement import EyesWebElement

    ViewPort = Union[Dict[Text, int], RectangleSize]  # typedef
    CodedRegionPadding = Dict[Text, int]  # typedef
    Num = Union[int, float]

    AnyWebDriver = Union[EyesWebDriver, WebDriver]  # typedef
    AnyWebElement = Union[EyesWebElement, WebElement]  # typedef

    FrameNameOrId = Text  # typedef
    FrameIndex = int  # typedef
    FrameReference = Union[FrameNameOrId, FrameIndex, AnyWebElement]  # typedef

    # could contain MouseTrigger, TextTrigger
    UserInputs = List[ActionTrigger]  # typedef
    RegionOrElement = Union[EyesWebElement, Region]  # typedef

    SeleniumBy = Text  # typedef
    BySelector = List[SeleniumBy, Text]  # typedef
    CssSelector = Text  # typedef
    REGION_VALUES = Union[Region, CssSelector, AnyWebElement, BySelector]  # typedef
    FLOATING_VALUES = Union[Region, CssSelector, AnyWebElement, BySelector]  # typedef
