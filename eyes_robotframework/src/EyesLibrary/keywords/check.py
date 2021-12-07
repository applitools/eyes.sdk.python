from __future__ import absolute_import, unicode_literals

from typing import TYPE_CHECKING, Any, Optional, Text

from appium.webdriver import WebElement as AppiumWebElement
from robot.api.deco import keyword as original_keyword
from robot.libraries.BuiltIn import BuiltIn
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement
from six import string_types as basestring

from applitools.common import MatchResult
from applitools.common.utils import argument_guard
from applitools.selenium import Target

from ..base import LibraryComponent
from ..utils import collect_check_settings, is_webelement_guard, parse_region
from .keyword_tags import CHECK_FLOW, CHECK_SETTINGS_SUPPORT, TARGET_SUPPORT

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import AnyWebElement

    from ..custom_types import Locator


def keyword(name=None, tags=(), types=()):
    """Keyword with predefined CHECK_SETTINGS_SUPPORT tag"""
    tags = tags + (CHECK_SETTINGS_SUPPORT,)
    return original_keyword(name, tags, types)


def try_resolve_tag_and_keyword(tag, check_settings_keywords, defined_keywords):
    if tag in defined_keywords:
        check_settings_keywords = (tag,) + check_settings_keywords
        tag = None
    return check_settings_keywords, tag


class CheckKeywords(LibraryComponent):
    @keyword("Eyes Check Window", types=(str,), tags=(CHECK_FLOW,))
    def check_window(self, tag=None, *check_settings_keywords):
        # type: (Optional[Text], tuple[Any]) -> MatchResult
        """
        Check current browser window

        *Example:*
            |  Eyes Check Window   |
        """
        check_settings_keywords, tag = try_resolve_tag_and_keyword(
            tag, check_settings_keywords, self.defined_keywords
        )
        check_settings = collect_check_settings(
            Target.window(), self.defined_keywords, *check_settings_keywords
        )
        return self.current_eyes.check(check_settings, tag)

    @keyword("Eyes Check Region By Coordinates", tags=(CHECK_FLOW,))
    def check_region_by_coordinates(
        self,
        region,  # type: Locator
        tag=None,  # type: Optional[Text]
        *check_settings_keywords  # type: tuple[Any]
    ):
        # type: (...) -> MatchResult
        """
        Check specified region

          |  =Arguments=  | =Description=                                                       |
          |  Region       | *Mandatory* - The region to check in format [left top width height] ,e.g. [100 200 300 300]  |

        *Example:*
            |  Eyes Check Region By Coordinates   |  [40 50 200 448]  |
        """
        check_settings_keywords, tag = try_resolve_tag_and_keyword(
            tag, check_settings_keywords, self.defined_keywords
        )
        check_settings = collect_check_settings(
            Target.region(parse_region(region)),
            self.defined_keywords,
            *check_settings_keywords
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
        *check_settings_keywords  # type: tuple[Any]
    ):
        # type: (...) -> MatchResult
        """
        Check specified region by element

            |  =Arguments=  | =Description=                                   |
            | Element       | *Mandatory* - The element to check              |

        *Example:*
            |  Eyes Check Region By Element  |  ${element}  |
        """
        is_webelement_guard(element)
        check_settings_keywords, tag = try_resolve_tag_and_keyword(
            tag, check_settings_keywords, self.defined_keywords
        )
        check_settings = collect_check_settings(
            Target.region(element), self.defined_keywords, *check_settings_keywords
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
        *check_settings_keywords  # type: tuple[Any]
    ):
        # type: (...) -> MatchResult
        """
        Check specified region by selector

            | =Arguments=   | =Description=                         |
            |  Selector     | *Mandatory* - The selector to check.  |

        *Example:*
            |  Eyes Check Region By Element  |  css:#selector  |
        """
        check_settings_keywords, tag = try_resolve_tag_and_keyword(
            tag, check_settings_keywords, self.defined_keywords
        )
        check_settings = collect_check_settings(
            Target.region(self.from_locator_to_supported_form(selector)),
            self.defined_keywords,
            *check_settings_keywords
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
        *check_settings_keywords  # type: tuple[Any]
    ):
        # type: (...) -> MatchResult
        """
         Check specified frame by element

            | =Arguments=   | =Description=                                        |
            | Element       | *Mandatory* - The frame to check                     |

        *Example:*
            |  Eyes Check Frame By Element  |  ${element}  |
        """
        is_webelement_guard(element)
        check_settings_keywords, tag = try_resolve_tag_and_keyword(
            tag, check_settings_keywords, self.defined_keywords
        )
        check_settings = collect_check_settings(
            Target.frame(element), self.defined_keywords, *check_settings_keywords
        )
        return self.current_eyes.check(check_settings, tag)

    @keyword("Eyes Check Frame By Index", types=(int, str), tags=(CHECK_FLOW,))
    def check_frame_by_index(
        self,
        frame_index,  # type: int
        tag=None,  # type: Optional[Text]
        *check_settings_keywords  # type: tuple[Any]
    ):
        # type: (...) -> MatchResult
        """
         Check specified frame by index

            | =Arguments=     | =Description=                                                       |
            |  Frame Index    | *Mandatory* - Index of the frame to check. |

        *Example:*
            |  Eyes Check Frame By Index  |  2  |
        """
        argument_guard.is_a(frame_index, int)
        check_settings_keywords, tag = try_resolve_tag_and_keyword(
            tag, check_settings_keywords, self.defined_keywords
        )
        check_settings = collect_check_settings(
            Target.frame(frame_index), self.defined_keywords, *check_settings_keywords
        )
        return self.current_eyes.check(check_settings, tag)

    @keyword("Eyes Check Frame By Name", types=(str, str), tags=(CHECK_FLOW,))
    def check_frame_by_name(
        self,
        frame_name,  # type: Text
        tag=None,  # type: Optional[Text]
        *check_settings_keywords  # type: tuple[Any]
    ):
        # type: (...) -> MatchResult
        """
         Check specified frame by name

            |  =Arguments=   | =Description=                                   |
            |  Frame Name    | *Mandatory* - Name of the frame to check.      |

        *Example:*
            |  Eyes Check Frame By Name  |  frameName  |
        """
        argument_guard.is_a(frame_name, basestring)
        check_settings_keywords, tag = try_resolve_tag_and_keyword(
            tag, check_settings_keywords, self.defined_keywords
        )
        check_settings = collect_check_settings(
            Target.frame(frame_name), self.defined_keywords, *check_settings_keywords
        )
        return self.current_eyes.check(check_settings, tag)

    @keyword("Eyes Check Frame By Selector", types=(str, str), tags=(CHECK_FLOW,))
    def check_frame_by_selector(
        self,
        selector,  # type: Text
        tag=None,  # type: Optional[Text]
        *check_settings_keywords  # type: tuple[Any]
    ):
        # type: (...) -> MatchResult
        """
         Check specified frame by name

            |  =Arguments=   | =Description=                                  |
            |  Selector     | *Mandatory* - Selector of the frame to check.   |

        *Example:*
            |  Eyes Check Frame By Selector  |  css:#selector   |
        """
        argument_guard.is_a(selector, basestring)
        check_settings_keywords, tag = try_resolve_tag_and_keyword(
            tag, check_settings_keywords, self.defined_keywords
        )
        check_settings = collect_check_settings(
            Target.frame(self.from_locator_to_supported_form(selector)),
            self.defined_keywords,
            *check_settings_keywords
        )
        return self.current_eyes.check(check_settings, tag)

    @keyword("Eyes Check", tags=(TARGET_SUPPORT, CHECK_FLOW))
    def check(self, target_keyword, *check_settings_keywords):
        """
         Check with target

            |  =Arguments=      | =Description=                  |
            |  Target Keyword  | *Mandatory* - Target Keyword that market with Target Keyword tag  |

        *Example:*
            |  Eyes Check  |  Target Window   |
            |  Eyes Check  |  Target Region By Coordinates   |  [34 56 78 89]  |
        """
        target = BuiltIn().run_keyword(target_keyword, *check_settings_keywords)
        self.current_eyes.check(target)
