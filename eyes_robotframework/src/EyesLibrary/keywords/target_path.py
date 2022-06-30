from typing import TYPE_CHECKING, Optional, Text

from appium.webdriver import WebElement as AppiumWebElement
from robot.api.deco import keyword as original_keyword
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement

from applitools.selenium import TargetPath
from applitools.selenium.fluent.target_path import ShadowDomLocator

from ..base import LibraryComponent
from ..keywords_list import TARGET_PATH_KEYWORDS_LIST
from ..utils import is_webelement_guard
from .keyword_tags import TARGET_PATH

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import AnyWebElement


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
    """
    Target Path keywords are used in combine with:
        - `Eyes Check Region By Target Path`
        - `Target Region By Target Path`
    """

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
            | Shadow By Element          | ${element}        |
        """
        is_webelement_guard(element)
        return new_or_cur_target_path(target_path).shadow(element)

    @keyword("Shadow By Selector", types=(str,))
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
            |  Shadow By Selector  |  //selector  |
        """
        by, selector = self.from_locator_to_supported_form(selector)
        return new_or_cur_target_path(target_path).shadow(by, selector)

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
            |  Region By Selector  |  //selector  |
        """
        if not isinstance(target_path, ShadowDomLocator):
            raise ValueError("Shadow * keyword should be used before Region * keyword")
        by, selector = self.from_locator_to_supported_form(selector)
        return target_path.region(by, selector)

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
            | Shadow By Element  | ${element}        |
        """
        is_webelement_guard(element)
        if not isinstance(target_path, ShadowDomLocator):
            raise ValueError("Shadow * keyword should be used before Region * keyword")
        return target_path.region(element)
