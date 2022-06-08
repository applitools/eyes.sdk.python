from typing import TYPE_CHECKING, Optional, Text

from appium.webdriver import WebElement as AppiumWebElement
from robot.api.deco import keyword as original_keyword
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement

from applitools.selenium import TargetPath
from applitools.selenium.fluent.target_path import ShadowDomLocator
from EyesLibrary.base import LibraryComponent
from EyesLibrary.keywords.keyword_tags import TARGET_PATH
from EyesLibrary.utils import is_webelement_guard

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import AnyWebElement
TARGET_PATH_KEYWORDS_LIST = []


def keyword(name=None, tags=(), types=()):
    """Keyword with predefined CHECK_SETTING tag"""
    TARGET_PATH_KEYWORDS_LIST.append(name)
    tags = tags + (TARGET_PATH,)
    return original_keyword(name, tags, types)


def new_or_cur_target_path(target_path):
    # type: (Optional[TargetPath])->TargetPath
    if target_path is None:
        return TargetPath()
    return target_path


class TargetPathKeywords(LibraryComponent):
    @keyword(
        "Shadow By Element",
        types={"element": (SeleniumWebElement, AppiumWebElement)},
    )
    def shadow_by_element(
        self,
        element,  # type: AnyWebElement
        target_path=None,  # type: Optional[TargetPath]
    ):
        # type: (...)-> None
        """
        Returns a TargetPath object with shadow dom specified in the argument.

            | =Arguments=   | =Description=                                     |
            | Element       | *Mandatory* - The element for shadow dom          |

        *Example:*
            | ${element}=   | Get Webelement             | //*[@id="logo"]   |
            | ${target}=    | Shadow By Element          | ${element}        |
        """
        is_webelement_guard(element)
        return new_or_cur_target_path(target_path).shadow(element)

    @keyword("Shadow By Selector", types=(str, str))
    def shadow_by_selector(
        self,
        selector,  # type: Text
        target_path=None,  # type: Optional[TargetPath]
    ):
        # type: (...)->TargetPath
        """
        Returns a TargetPath object with shadow dom specified in the arguments.

            | =Arguments=   |   =Description=                                          |
            | Selector      |  *Mandatory* - The selector for element for shadow dom. Selenium/Appium formats are supported. |

        *Example:*
            | Eyes Check                  |              |
            | ...     Shadow By Selector  |  //selector  |
        """
        return new_or_cur_target_path(target_path).shadow(
            *self.from_locators_to_supported_form(selector)
        )

    @keyword("Region By Selector", types=(str,))
    def region_by_selector(
        self,
        selector,  # type: Text
        target_path=None,  # type: Optional[TargetPath]
    ):
        # type: (...)->TargetPath
        """
        Returns a TargetPath object with region in shadow dom specified in the arguments.

            | =Arguments=   |   =Description=                                          |
            | Selector      |  *Mandatory* - The selector for element for shadow dom. Selenium/Appium formats are supported. |

        *Example:*
            | Eyes Check                  |              |
            | ...     Region By Selector  |  //selector  |
        """
        if not isinstance(target_path, ShadowDomLocator):
            raise ValueError("Shadow * keyword should be used before Region * keyword")
        return target_path.region(*self.from_locators_to_supported_form(selector))

    @keyword(
        "Region By Element",
        types={"element": (SeleniumWebElement, AppiumWebElement)},
    )
    def region_by_element(
        self,
        element,  # type: AnyWebElement
        target_path=None,  # type: Optional[TargetPath]
    ):
        # type: (...)->TargetPath
        """
        Returns a TargetPath object with shadow dom specified in the argument.

            | =Arguments=   | =Description=                                     |
            | Element       | *Mandatory* - The element for shadow dom          |

        *Example:*
            | ${element}=   | Get Webelement             | //*[@id="logo"]   |
            | ${target}=    | Shadow By Element          | ${element}        |
        """
        is_webelement_guard(element)
        if not isinstance(target_path, ShadowDomLocator):
            raise ValueError("Shadow * keyword should be used before Region * keyword")
        return target_path.region(element)
