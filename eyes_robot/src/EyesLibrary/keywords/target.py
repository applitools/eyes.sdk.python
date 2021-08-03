from typing import TYPE_CHECKING, Any, List, Optional, Text, Tuple, Union

from appium.webdriver import WebElement as AppiumWebElement
from robot.libraries.BuiltIn import BuiltIn
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement

from applitools.common import MatchResult, Region
from applitools.selenium import Target
from applitools.selenium.fluent import SeleniumCheckSettings

from ..base import LibraryComponent, keyword
from ..utils import collect_check_settings, parse_region
from .keyword_tags import CHECK_SETTINGS_SUPPORT, TARGET_SUPPORT

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import AnyWebElement

    from ..custom_types import Locator


class CheckKeywords(LibraryComponent):
    @keyword("Eyes Check Region By Coordinates", tags=(CHECK_SETTINGS_SUPPORT,))
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
        tags=(CHECK_SETTINGS_SUPPORT,),
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
        tags=(CHECK_SETTINGS_SUPPORT,),
    )
    def check_region_by_selector(
        self,
        selector,  # type: Locator
        tag=None,  # type: Optional[Text]
        *check_settings_keywords,  # type: tuple[Any]
    ):
        # type: (...) -> MatchResult
        check_settings = collect_check_settings(
            Target.region(*self.from_locator_to_supported_form(selector)),
            self.defined_keywords,
            *check_settings_keywords,
        )
        return self.current_eyes.check(check_settings, tag)

    @keyword("Eyes Check Window", types=(str,), tags=(CHECK_SETTINGS_SUPPORT,))
    def check_window(self, tag=None, *check_settings_keywords):
        # type: (Optional[Text], tuple[Any]) -> MatchResult
        check_settings = collect_check_settings(
            Target.window(), self.defined_keywords, *check_settings_keywords
        )
        return self.current_eyes.check(check_settings, tag)

    @keyword(
        "Eyes Check Frame By Element",
        types={"element": (SeleniumWebElement, AppiumWebElement), "tag": str},
        tags=(CHECK_SETTINGS_SUPPORT,),
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

    @keyword(
        "Eyes Check Frame By Index", types=(int, str), tags=(CHECK_SETTINGS_SUPPORT,)
    )
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

    @keyword(
        "Eyes Check Frame By Name", types=(str, str), tags=(CHECK_SETTINGS_SUPPORT,)
    )
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

    @keyword(
        "Eyes Check Frame By Selector", types=(str, str), tags=(CHECK_SETTINGS_SUPPORT,)
    )
    def check_frame_by_selector(
        self,
        selector,  # type: Text
        tag=None,  # type: Optional[Text]
        *check_settings_keywords,  # type: tuple[Any]
    ):
        # type: (...) -> MatchResult
        check_settings = collect_check_settings(
            Target.frame(*self.from_locator_to_supported_form(selector)),
            self.defined_keywords,
            *check_settings_keywords,
        )
        return self.current_eyes.check(check_settings, tag)


class TargetKeywords(LibraryComponent):
    @keyword("Eyes Check", tags=(TARGET_SUPPORT, CHECK_SETTINGS_SUPPORT))
    def check(self, target_keyword, *check_settings_keywords):
        target = BuiltIn().run_keyword(target_keyword, *check_settings_keywords)
        self.current_eyes.check(target)

    @keyword("Target Window", tags=(CHECK_SETTINGS_SUPPORT,))
    def target_window(self, *check_settings_keywords):
        # type: (tuple[Any]) -> SeleniumCheckSettings
        """"""
        return collect_check_settings(
            Target.window(), self.defined_keywords, *check_settings_keywords
        )

    @keyword(
        "Target Region By Element",
        types={"element": (SeleniumWebElement, AppiumWebElement)},
        tags=(CHECK_SETTINGS_SUPPORT,),
    )
    def target_region_by_element(self, element, *check_settings_keywords):
        # type: (AnyWebElement,tuple[Any]) -> SeleniumCheckSettings
        return collect_check_settings(
            Target.region(element),
            self.defined_keywords,
            *check_settings_keywords,
        )

    @keyword(
        "Target Region By Coordinates", types=(str,), tags=(CHECK_SETTINGS_SUPPORT,)
    )
    def target_region_by_coordinates(self, region, *check_settings_keywords):
        # type: (Text,tuple[Any]) -> SeleniumCheckSettings
        return collect_check_settings(
            Target.region(parse_region(region)),
            self.defined_keywords,
            *check_settings_keywords,
        )

    @keyword("Target Region By Selector", types=(str,), tags=(CHECK_SETTINGS_SUPPORT,))
    def target_region_by_selector(self, region, *check_settings_keywords):
        # type: (Text,tuple[Any]) -> SeleniumCheckSettings
        return collect_check_settings(
            Target.region(*self.from_locator_to_supported_form(region)),
            self.defined_keywords,
            *check_settings_keywords,
        )

    @keyword(
        "Target Frame By Element",
        types={"element": (SeleniumWebElement, AppiumWebElement)},
        tags=(CHECK_SETTINGS_SUPPORT,),
    )
    def target_frame_by_element(self, element, *check_settings_keywords):
        # type: (AnyWebElement,tuple[Any]) -> SeleniumCheckSettings
        return collect_check_settings(
            Target.frame(element),
            self.defined_keywords,
            *check_settings_keywords,
        )

    @keyword(
        "Target Frame By Selector",
        types=(str,),
        tags=(CHECK_SETTINGS_SUPPORT,),
    )
    def target_frame_by_selector(self, selector, *check_settings_keywords):
        # type: (Locator,tuple[Any]) -> SeleniumCheckSettings
        return collect_check_settings(
            Target.frame(self.from_locator_to_supported_form(selector)),
            self.defined_keywords,
            *check_settings_keywords,
        )

    @keyword(
        "Target Frame By Index",
        types=(int,),
        tags=(CHECK_SETTINGS_SUPPORT,),
    )
    def target_frame_by_index(self, frame_id, *check_settings_keywords):
        # type: (int,tuple[Any]) -> SeleniumCheckSettings
        return collect_check_settings(
            Target.frame(frame_id),
            self.defined_keywords,
            *check_settings_keywords,
        )

    @keyword(
        "Target Frame By Name",
        types=(str,),
        tags=(CHECK_SETTINGS_SUPPORT,),
    )
    def target_frame_by_name(self, frame_name, *check_settings_keywords):
        # type: (Text,tuple[Any]) -> SeleniumCheckSettings
        return collect_check_settings(
            Target.frame(frame_name),
            self.defined_keywords,
            *check_settings_keywords,
        )
