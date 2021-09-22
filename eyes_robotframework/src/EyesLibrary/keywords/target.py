from __future__ import absolute_import, unicode_literals

from typing import TYPE_CHECKING, Any, Text

from appium.webdriver import WebElement as AppiumWebElement
from robot.api.deco import keyword as original_keyword
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement

from applitools.selenium import Target
from applitools.selenium.fluent import SeleniumCheckSettings

from ..base import LibraryComponent
from ..utils import collect_check_settings, parse_region
from .keyword_tags import CHECK_SETTINGS_SUPPORT, TARGET_KEYWORD

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import AnyWebElement

    from ..custom_types import Locator


def keyword(name=None, tags=(), types=()):
    """Keyword with predefined CHECK_SETTINGS_SUPPORT tag"""
    tags = tags + (CHECK_SETTINGS_SUPPORT, TARGET_KEYWORD)
    return original_keyword(name, tags, types)


class TargetKeywords(LibraryComponent):
    @keyword("Target Window")
    def target_window(self, *check_settings_keywords):
        # type: (tuple[Any]) -> SeleniumCheckSettings
        """
        Returns a CheckSettings object with Window selected and any number of Check Settings Keywords.

        *Example:*
            |  ${target}=    | Target Window     |
        """
        return collect_check_settings(
            Target.window(), self.defined_keywords, *check_settings_keywords
        )

    @keyword(
        "Target Region By Element",
        types={"element": (SeleniumWebElement, AppiumWebElement)},
    )
    def target_region_by_element(self, element, *check_settings_keywords):
        # type: (AnyWebElement,tuple[Any]) -> SeleniumCheckSettings
        """
        Returns a CheckSettings object with selected Region and any number of Check Settings Keywords.

            |  =Arguments=  | =Description=                                          |
            | Element       | *Mandatory* - The element to check                     |

        *Example:*
            |  ${target}=  |  Target Region By Element  |  ${element}  |
        """
        return collect_check_settings(
            Target.region(element), self.defined_keywords, *check_settings_keywords
        )

    @keyword(
        "Target Region By Coordinates", types=(str,), tags=(CHECK_SETTINGS_SUPPORT,)
    )
    def target_region_by_coordinates(self, region, *check_settings_keywords):
        # type: (Text,tuple[Any]) -> SeleniumCheckSettings
        """
        Returns a CheckSettings object with selected Region and any number of Check Settings Keywords.

            |  =Arguments=  | =Description=                                                       |
            |  Region       | *Mandatory* - The region to check in format [left top width height] ,e.g. [100 200 300 300]  |

        *Example:*
            |  ${target}=  |  Target Region By Coordinates  |  [10 30 40 50]  |
        """
        return collect_check_settings(
            Target.region(parse_region(region)),
            self.defined_keywords,
            *check_settings_keywords
        )

    @keyword("Target Region By Selector", types=(str,), tags=(CHECK_SETTINGS_SUPPORT,))
    def target_region_by_selector(self, selector, *check_settings_keywords):
        # type: (Text,tuple[Any]) -> SeleniumCheckSettings
        """
        Returns a CheckSettings object with selected Region and any number of Check Settings Keywords.

            | =Arguments=   | =Description=                          |
            |  Selector     | *Mandatory* - The selector to check.   |

        *Example:*
            |  ${target}=  |  Target Frame By Selector  |  css:#selector  |
        """
        return collect_check_settings(
            Target.region(self.from_locator_to_supported_form(selector)),
            self.defined_keywords,
            *check_settings_keywords
        )

    @keyword(
        "Target Frame By Element",
        types={"element": (SeleniumWebElement, AppiumWebElement)},
        tags=(CHECK_SETTINGS_SUPPORT,),
    )
    def target_frame_by_element(self, element, *check_settings_keywords):
        # type: (AnyWebElement,tuple[Any]) -> SeleniumCheckSettings
        """
        Returns a CheckSettings object with selected Frame and any number of Check Settings Keywords.

            | =Arguments=   | =Description=                                        |
            | Element       | *Mandatory* - The frame to check                     |

        *Example:*
            |  ${target}=  |  Target Frame By Element  |  ${element}  |
        """
        return collect_check_settings(
            Target.frame(element), self.defined_keywords, *check_settings_keywords
        )

    @keyword(
        "Target Frame By Selector",
        types=(str,),
        tags=(CHECK_SETTINGS_SUPPORT,),
    )
    def target_frame_by_selector(self, selector, *check_settings_keywords):
        # type: (Locator,tuple[Any]) -> SeleniumCheckSettings
        """
        Returns a CheckSettings object with selected Frame and any number of Check Settings Keywords.

            | =Arguments=   | =Description=                                  |
            |  Selector     | *Mandatory* - Selector of the frame to check.  |

        *Example:*
            |  ${target}=  |  Target Frame By Selector  |  css:#selector  |
        """
        return collect_check_settings(
            Target.frame(self.from_locator_to_supported_form(selector)),
            self.defined_keywords,
            *check_settings_keywords
        )

    @keyword(
        "Target Frame By Index",
        types=(int,),
        tags=(CHECK_SETTINGS_SUPPORT,),
    )
    def target_frame_by_index(self, frame_index, *check_settings_keywords):
        # type: (int,tuple[Any]) -> SeleniumCheckSettings
        """
        Returns a CheckSettings object with selected Frame and any number of Check Settings Keywords.

            | =Arguments=     | =Description=                                   |
            |  Frame Index    | *Mandatory* - Index of the frame to check.      |

        *Example:*
            | ${target}=  |  Target Frame By Index  |  2  |
        """
        return collect_check_settings(
            Target.frame(frame_index), self.defined_keywords, *check_settings_keywords
        )

    @keyword(
        "Target Frame By Name",
        types=(str,),
        tags=(CHECK_SETTINGS_SUPPORT,),
    )
    def target_frame_by_name(self, frame_name, *check_settings_keywords):
        # type: (Text,tuple[Any]) -> SeleniumCheckSettings
        """
        Returns a CheckSettings object with selected Frame and any number of Check Settings Keywords.

            |  =Arguments=   | =Description=                                  |
            |  Frame Name    | *Mandatory* - Name of the frame to check.      |

        *Example:*
            |  ${target}=  |  Target Frame By Name  |  frameName  |
        """
        return collect_check_settings(
            Target.frame(frame_name), self.defined_keywords, *check_settings_keywords
        )
