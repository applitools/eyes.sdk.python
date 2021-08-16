from typing import TYPE_CHECKING, Any, Optional, Text

from appium.webdriver import WebElement as AppiumWebElement
from robot.libraries.BuiltIn import BuiltIn
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement

from applitools.common import MatchResult
from applitools.selenium import Target
from EyesLibrary.base import LibraryComponent
from EyesLibrary.keywords.keyword_tags import (
    CHECK_FLOW,
    CHECK_SETTINGS_SUPPORT,
    TARGET_SUPPORT,
)
from EyesLibrary.keywords.target import keyword as original_keyword
from EyesLibrary.utils import collect_check_settings, parse_region

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import AnyWebElement
    from EyesLibrary.custom_types import Locator


def keyword(name=None, tags=(), types=()):
    """Keyword with predefined CHECK_SETTINGS_SUPPORT tag"""
    tags = tags + (CHECK_SETTINGS_SUPPORT,)
    return original_keyword(name, tags, types)


class CheckKeywords(LibraryComponent):
    @keyword("Eyes Check Window", types=(str,), tags=(CHECK_FLOW,))
    def check_window(self, tag=None, *check_settings_keywords):
        # type: (Optional[Text], tuple[Any]) -> MatchResult
        """
        Check Window  Check Settings Keywords.
            |  =Arguments=  | =Description=                                                       |
            |  Tag       | he region to check in format [left top width height] ,e.g. [100 200 300 300]  |

        *Example:*
            |  ${target}=    | Target Window     |
        """
        if tag in self.defined_keywords:
            check_settings_keywords += (tag,)
            tag = None
        check_settings = collect_check_settings(
            Target.window(), self.defined_keywords, *check_settings_keywords
        )
        return self.current_eyes.check(check_settings, tag)

    @keyword("Eyes Check Region By Coordinates", tags=(CHECK_FLOW,))
    def check_region_by_coordinates(
        self,
        region,  # type: Locator
        tag=None,  # type: Optional[Text]
        *check_settings_keywords,  # type: tuple[Any]
    ):
        # type: (...) -> MatchResult
        check_settings = collect_check_settings(
            Target.region(parse_region(region)),
            self.defined_keywords,
            *check_settings_keywords,
        )
        return self.current_eyes.check(check_settings, tag)

    @keyword(
        "Eyes Check Region By Element",
        types={"element": (SeleniumWebElement, AppiumWebElement), "tag": str},
        tags=(CHECK_FLOW,),
    )
    def check_region_by_element(
        self,
        element,  # type: Locator
        tag=None,  # type: Optional[Text]
        *check_settings_keywords,  # type: tuple[Any]
    ):
        # type: (...) -> MatchResult
        check_settings = collect_check_settings(
            Target.region(element),
            self.defined_keywords,
            *check_settings_keywords,
        )
        return self.current_eyes.check(check_settings, tag)

    @keyword(
        "Eyes Check Region By Selector",
        types=(str, str),
        tags=(CHECK_FLOW,),
    )
    def check_region_by_selector(
        self,
        selector,  # type: Locator
        tag=None,  # type: Optional[Text]
        *check_settings_keywords,  # type: tuple[Any]
    ):
        # type: (...) -> MatchResult
        check_settings = collect_check_settings(
            Target.region(self.from_locator_to_supported_form(selector)),
            self.defined_keywords,
            *check_settings_keywords,
        )
        return self.current_eyes.check(check_settings, tag)

    @keyword(
        "Eyes Check Frame By Element",
        types={"element": (SeleniumWebElement, AppiumWebElement), "tag": str},
        tags=(CHECK_FLOW,),
    )
    def check_frame_by_element(
        self,
        element,  # type: AnyWebElement
        tag=None,  # type: Optional[Text]
        *check_settings_keywords,  # type: tuple[Any]
    ):
        # type: (...) -> MatchResult
        check_settings = collect_check_settings(
            Target.frame(element), self.defined_keywords, *check_settings_keywords
        )
        return self.current_eyes.check(check_settings, tag)

    @keyword("Eyes Check Frame By Index", types=(int, str), tags=(CHECK_FLOW,))
    def check_frame_by_index(
        self,
        frame_index,  # type: int
        tag=None,  # type: Optional[Text]
        *check_settings_keywords,  # type: tuple[Any]
    ):
        # type: (...) -> MatchResult
        check_settings = collect_check_settings(
            Target.frame(frame_index), self.defined_keywords, *check_settings_keywords
        )
        return self.current_eyes.check(check_settings, tag)

    @keyword("Eyes Check Frame By Name", types=(str, str), tags=(CHECK_FLOW,))
    def check_frame_by_name(
        self,
        frame_name,  # type: Text
        tag=None,  # type: Optional[Text]
        *check_settings_keywords,  # type: tuple[Any]
    ):
        # type: (...) -> MatchResult
        check_settings = collect_check_settings(
            Target.frame(frame_name), self.defined_keywords, *check_settings_keywords
        )
        return self.current_eyes.check(check_settings, tag)

    @keyword("Eyes Check Frame By Selector", types=(str, str), tags=(CHECK_FLOW,))
    def check_frame_by_selector(
        self,
        selector,  # type: Text
        tag=None,  # type: Optional[Text]
        *check_settings_keywords,  # type: tuple[Any]
    ):
        # type: (...) -> MatchResult
        check_settings = collect_check_settings(
            Target.frame(self.from_locator_to_supported_form(selector)),
            self.defined_keywords,
            *check_settings_keywords,
        )
        return self.current_eyes.check(check_settings, tag)

    @keyword("Eyes Check", tags=(TARGET_SUPPORT, CHECK_FLOW))
    def check(self, target_keyword, *check_settings_keywords):
        target = BuiltIn().run_keyword(target_keyword, *check_settings_keywords)
        self.current_eyes.check(target)
