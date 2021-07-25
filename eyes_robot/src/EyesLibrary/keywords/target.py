from typing import TYPE_CHECKING, Any, List, Text, Tuple, Union

from robot.libraries.BuiltIn import BuiltIn

from applitools.common import MatchResult, Region
from applitools.selenium import Target
from applitools.selenium.fluent import SeleniumCheckSettings

from ..base import LibraryComponent, keyword
from ..utils import collect_check_settings

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import AnyWebElement, FrameReference

    from ..custom_types import Locator


class CheckKeywords(LibraryComponent):
    @keyword("Eyes Check")
    def check(self, *fluent_keywords):
        target = BuiltIn().run_keyword(*fluent_keywords)
        self.current_eyes.check(target)

    @keyword("Eyes Check Region")
    def check_region(
        self,
        locator,  # type: Locator
        tag,  # type:Text
        *fluent_keywords,  # type: tuple[Any]
    ):
        # type: (...) -> MatchResult
        check_settings = collect_check_settings(
            Target.region(self.get_by_selector_or_webelement(locator)),
            self.defined_keywords,
            *fluent_keywords,
        )
        return self.current_eyes.check(check_settings, tag)

    @keyword("Eyes Check Window")
    def check_window(self, tag, *fluent_keywords):
        # type: (Text, tuple[Any]) -> MatchResult
        check_settings = collect_check_settings(
            Target.window(), self.defined_keywords, *fluent_keywords
        )
        return self.current_eyes.check(check_settings, tag)

    @keyword("Eyes Check Frame")
    def check_frame(
        self,
        tag,  # type: Text
        frame_reference,  # type: FrameReference
        *fluent_keywords,  # type: tuple[Any]
    ):
        # type: (...) -> MatchResult
        check_settings = collect_check_settings(
            Target.frame(frame_reference), self.defined_keywords, *fluent_keywords
        )
        return self.current_eyes.check(check_settings, tag)


class TargetKeywords(LibraryComponent):
    @keyword("Eyes Target Window")
    def target_window(self, *keywords):
        # type: (tuple[Any]) -> SeleniumCheckSettings
        return collect_check_settings(Target.window(), self.defined_keywords, *keywords)

    @keyword("Eyes Target Region", tags=("CheckSettings",))
    def target_by_region(self, locator, *keywords):
        # type: (Locator,tuple[Any]) -> SeleniumCheckSettings
        return collect_check_settings(
            Target.region(self.get_by_selector_or_webelement(locator)),
            self.defined_keywords,
            *keywords,
        )

    @keyword("Eyes Target Region By Coordinates", types=(int, int, int, int))
    def target_by_coordinates(self, left, top, width, height, *keywords):
        # type: (int,int,int,int,tuple[Any]) -> SeleniumCheckSettings
        return collect_check_settings(
            Target.region(Region(left, top, width, height)),
            self.defined_keywords,
            *keywords,
        )

    @keyword("Eyes Target Frame")
    def target_by_frame(self, locator, *keywords):
        # type: (Locator,tuple[Any]) -> SeleniumCheckSettings
        return collect_check_settings(
            Target.frame(self.get_by_selector_or_webelement(locator)),
            self.defined_keywords,
            *keywords,
        )
