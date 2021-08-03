from typing import TYPE_CHECKING, Optional, Text

from appium.webdriver import WebElement as AppiumWebElement
from EyesLibrary.base import LibraryComponent
from EyesLibrary.keywords.keyword_tags import CHECK_SETTING
from EyesLibrary.utils import parse_region
from robot.api.deco import keyword as original_kyeword
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement

from applitools.common import AccessibilityRegionType, MatchLevel, VisualGridOption
from applitools.common.utils import argument_guard
from applitools.selenium.fluent import SeleniumCheckSettings
from applitools.selenium.validators import is_webelement

if TYPE_CHECKING:
    from EyesLibrary.custom_types import Locator

    from applitools.common.utils.custom_types import AnyWebElement


def keyword(name=None, tags=(), types=()):
    tags = tags + (CHECK_SETTING,)
    return original_kyeword(name, tags, types)


def new_or_cur_check_settings(check_settings):
    # type: (Optional[SeleniumCheckSettings])->SeleniumCheckSettings
    if check_settings is None:
        return SeleniumCheckSettings()
    return check_settings


def is_webelement_guard(element):
    argument_guard.is_valid_type(
        is_webelement(element),
        "element argument should be type Selenium or Appium Web Element",
    )


class IgnoreCheckSettingsKeyword:
    @keyword("Ignore Region By Coordinates", types=(str,))
    def ignore_region_by_coordinates(
        self,
        region,  # type: Text
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object that ignores the region specified in the argument.
            | =Arguments=   | =Description=                                                       |
            | Region          | *Mandatory* - The region to ignore in format [left top width height] ,e.g. [100 200 300 300]  |

        *Example:*
            | Ignore Region By Coordinates           | [10 20 100 100]  |
        """
        return new_or_cur_check_settings(check_settings).ignore(parse_region(region))

    @keyword(
        "Ignore Region By Element",
        types={"element": (SeleniumWebElement, AppiumWebElement)},
    )
    def ignore_region_by_element(
        self,
        element,  # type: AnyWebElement
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object that ignores the region specified in the argument.
            | =Arguments=   | =Description=                                           |
            | Element       | *Mandatory* - The element to ignore                     |

        *Example:*
            | ${element}=   | Get Webelement                | //*[@id="logo"]   |
            | ${target}=    | Ignore Region By Element      | ${element}        |
        """
        is_webelement_guard(element)
        return new_or_cur_check_settings(check_settings).ignore(element)

    @keyword("Ignore Region By Selector", types=(str,))
    def ignore_region_by_selector(
        self,
        selector,  # type: Locator
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object that ignores the region specified in the argument.
            | =Arguments=   | =Description=                                               |
            | Selector       | *Mandatory* - The selector for element to ignore. Selenium/Appium formats are supported. |

        *Example:*
            | Ignore Region By Selector      | css:div         |
        """
        return new_or_cur_check_settings(check_settings).ignore(
            *self.from_locators_to_supported_form(selector)
        )


class LayoutCheckSettingsKeyword:
    @keyword("Layout Region By Coordinates", types=(str,))
    def layout_region_by_coordinates(
        self,
        region,  # type: Text
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with layout region specified in the argument.
            | =Arguments=   | =Description=                                                       |
            | Region        | *Mandatory* - The layout region in format [left top width height] ,e.g. [100 200 300 300]  |

        *Example:*
            | Leyout Region By Coordinates           | [10 20 100 100]  |
        """
        return new_or_cur_check_settings(check_settings).layout(parse_region(region))

    @keyword(
        "Layout Region By Element",
        types={"element": (SeleniumWebElement, AppiumWebElement)},
    )
    def layout_region_by_element(
        self,
        element,  # type: AnyWebElement
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with layout region specified in the argument.
            | =Arguments=   | =Description=                                               |
            | Element       | *Mandatory* - The element with layout region e.g. [100 200 300 300]  |

        *Example:*
            | ${element}=   | Get Webelement                | //*[@id="logo"]   |
            | ${target}=    | Layout Region By Element      | ${element}        |
        """
        is_webelement_guard(element)
        return new_or_cur_check_settings(check_settings).layout(element)

    @keyword("Layout Region By Selector", types=(str,))
    def layout_region_by_selector(
        self,
        selector,  # type: Locator
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with layout region specified in the argument.
            | =Arguments=   | =Description=                                               |
            | Selector      | *Mandatory* - The selector for element for layout region. Selenium/Appium formats are supported. |

        *Example:*
            | Layout Region By Selector      | css:div         |
        """
        return new_or_cur_check_settings(check_settings).layout(
            *self.from_locators_to_supported_form(selector)
        )


class ContentCheckSettingsKeyword:
    @keyword("Content Region By Coordinates", types=(str,))
    def content_region_by_coordinates(
        self,
        region,  # type: Text
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with content region specified in the argument.
            | =Arguments=   | =Description=                                                       |
            | Region        | *Mandatory* - The content region in format [left top width height] ,e.g. [100 200 300 300]  |

        *Example:*
            | Content Region By Coordinates           | [10 20 100 100]  |
        """
        return new_or_cur_check_settings(check_settings).content(parse_region(region))

    @keyword(
        "Content Region By Element",
        types={"element": (SeleniumWebElement, AppiumWebElement)},
    )
    def content_region_by_element(
        self,
        element,  # type: AnyWebElement
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with content region specified in the argument.
            | =Arguments=   | =Description=                                       |
            | Element       | *Mandatory* - The element to become content region  |

        *Example:*
            | ${element}=   | Get Webelement                | //*[@id="logo"]   |
            | ${target}=    | Content Region By Element     | ${element}        |
        """
        is_webelement_guard(element)
        return new_or_cur_check_settings(check_settings).content(element)

    @keyword("Content Region By Selector", types=(str,))
    def content_region_by_selector(
        self,
        selector,  # type: Locator
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with content region specified in the argument.
            | =Arguments=   | =Description=                                               |
            | Selector      | *Mandatory* - The selector for element for content region. Selenium/Appium formats are supported. |

        *Example:*
            | Content Region By Selector      | css:div         |
        """
        return new_or_cur_check_settings(check_settings).content(
            *self.from_locators_to_supported_form(selector)
        )


class StrictCheckSettingsKeywords:
    @keyword("Strict Region By Coordinates", types=(str,))
    def strict_region_by_coordinates(
        self,
        region,  # type: Text
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with content region specified in the argument.
            | =Arguments=   | =Description=                                                       |
            | Region        | *Mandatory* - The strict region in format [left top width height] ,e.g. [100 200 300 300]  |

        *Example:*
            | Strict Region By Coordinates           | [10 20 100 100]  |
        """
        return new_or_cur_check_settings(check_settings).strict(parse_region(region))

    @keyword(
        "Strict Region By Element",
        types={"element": (SeleniumWebElement, AppiumWebElement)},
    )
    def strict_region_by_coordinates(
        self,
        element,  # type: AnyWebElement
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with strict region specified in the argument.
            | =Arguments=   | =Description=                                         |
            | Element       | *Mandatory* - The element to become strict region     |

        *Example:*
            | ${element}=   | Get Webelement                | //*[@id="logo"]   |
            | ${target}=    | Strict Region By Element      | ${element}        |
        """
        is_webelement_guard(element)
        return new_or_cur_check_settings(check_settings).strict(element)

    @keyword("Strict Region By Selector", types=(str,))
    def strict_region_by_coordinates(
        self,
        selector,  # type: Locator
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with strict region specified in the argument.
            | =Arguments=   | =Description=                                               |
            | Selector      | *Mandatory* - The selector for element for strict region. Selenium/Appium formats are supported. |

        *Example:*
            | Eyes Check                         |          |
            |...  Strict Region By Selector      | css:div  |
        """
        return new_or_cur_check_settings(check_settings).strict(
            *self.from_locators_to_supported_form(selector)
        )


class FloatingCheckSettingsKeywords:
    @keyword(
        "Floating Region With Max Offset By Coordinates",
        types=(int, str),
    )
    def floating_region_with_max_offset_by_coordinates(
        self,
        max_offset,  # type: int
        region,  # type: Text
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with floating region specified in the arguments.
            | =Arguments=  | =Description=                                                                                                 |
            | Max Offset   | *Mandatory* - The maximum amount that the region can shift in any direction and still be considered matching. |
            | Region       | *Mandatory* - The floating region e.g. [100 200 300 300]                                                       |

        *Example:*
            | Eyes Check                                            |     |                   |
            | ...   Floating Region With Max Offset By Coordinates  |  5  |  [10 20 100 100]  |
        """
        return new_or_cur_check_settings(check_settings).floating(
            max_offset, parse_region(region)
        )

    @keyword(
        "Floating Region With Max Offset By Element",
        types={"max_offset": int, "element": (SeleniumWebElement, AppiumWebElement)},
    )
    def floating_region_with_max_offset_by_element(
        self,
        max_offset,  # type: int
        element,  # type: AnyWebElement
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with floating region specified in the arguments.
            | =Arguments=  | =Description=                                                                                                 |
            | Max Offset   | *Mandatory* - The maximum amount that the region can shift in any direction and still be considered matching. |
            | Element       | *Mandatory* - The element to become floating region

        *Example:*
            | ${element}=   | Get Webelement                        |  //*[@id="logo"]  |              |
            | Eyes Check                                            |                   |              |
            | ...   Floating Region With Max Offset By Element      |       5           |  ${element}  |
        """
        is_webelement_guard(element)
        return new_or_cur_check_settings(check_settings).floating(max_offset, element)

    @keyword(
        "Floating Region With Max Offset By Selector",
        types=(str, str),
    )
    def floating_region_with_max_offset_by_selector(
        self,
        max_offset,  # type: int
        selector,  # type: Locator
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with floating region specified in the arguments.
            | =Arguments=  | =Description=                                                                                                 |
            | Max Offset   | *Mandatory* - The maximum amount that the region can shift in any direction and still be considered matching. |
            | Selector     | *Mandatory* - The selector to become floating region e.g. //*[@id="logo"]                                     |

        *Example:*
            | Eyes Check                                            |                   |                    |
            | ...   Floating Region With Max Offset By Selector     |       5           |  //*[@id="logo"]   |
        """
        return new_or_cur_check_settings(check_settings).floating(
            max_offset, *self.from_locators_to_supported_form(selector)
        )

    @keyword(
        "Floating Region By Coordinates",
        types=(str, int, int, int, int),
    )
    def floating_region_by_coordinates(
        self,
        region,  # type: Text
        max_up_offset=0,  # type: int
        max_down_offset=0,  # type: int
        max_left_offset=0,  # type: int
        max_right_offset=0,  # type: int
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with floating region specified in the arguments.
            | =Arguments=       | =Description=                                                                                              |
            | Region            | *Mandatory* - The floating region e.g. [100 200 300 300]                                                        |
            | Max Up Offset     | The maximum amount that the region can shift upwards and still be considered matching.       |
            | Max Down Offset   | The maximum amount that the region can shift downwards and still be considered matching.     |
            | Max Left Offset   | The maximum amount that the region can shift to the left and still be considered matching.   |
            | Max Right Offset  | The maximum amount that the region can shift to the right and still be considered matching.  |

        *Example:*
            | Eyes Check Window                       |                   |     |     |    |     |
            | ...     Floating Region By Coordinates  |  [10 20 100 100]  |  5  |  5  | 5  |  5  |
            | ...     Floating Region By Coordinates  |  [10 20 100 100]  |  max_right_offset=5  |   |   |    |
        """
        return new_or_cur_check_settings(check_settings).floating(
            parse_region(region),
            max_up_offset,
            max_down_offset,
            max_left_offset,
            max_right_offset,
        )

    @keyword(
        "Floating Region By Element",
        types={
            "element": (SeleniumWebElement, AppiumWebElement),
            "max_up_offset": int,
            "max_down_offset": int,
            "max_left_offset": int,
            "max_right_offset": int,
        },
    )
    def floating_region_by_element(
        self,
        element,  # type: AnyWebElement
        max_up_offset=0,  # type: int
        max_down_offset=0,  # type: int
        max_left_offset=0,  # type: int
        max_right_offset=0,  # type: int
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with floating region specified in the arguments.
            | =Arguments=      | =Description=                                                                                                       |
            | Element          | *Mandatory* - The WebElement to set as float region.                                                  |
            | Max Up Offset    | The maximum amount that the region can shift upwards and still be considered matching.             |
            | Max Down Offset  | The maximum amount that the region can shift downwards and still be considered matching.         |
            | Max Left Offset  | The maximum amount that the region can shift to the left and still be considered matching.       |
            | Max Right Offset | The maximum amount that the region can shift to the right and still be considered matching.     |

        *Example:*
            | ${element}=                           |  Get Webelement  |  //*[@id="logo"]  |  |  |  |
            | Eyes Check Window                     |               |     |     |     |     |
            | ...   Floating Region By Element      |  ${element}   |  5  |  5  |  5  |  5  |
            | ...   Floating Region By Element      |  ${element}   |  max_left_offset=5 |   |   |    |

        """
        is_webelement_guard(element)
        return new_or_cur_check_settings(check_settings).floating(
            element,
            max_up_offset,
            max_down_offset,
            max_left_offset,
            max_right_offset,
        )

    @keyword(
        "Floating Region By Selector",
        types=(str, int, int, int, int),
    )
    def floating_region_by_selector(
        self,
        selector,  # type: Text
        max_up_offset=0,  # type: int
        max_down_offset=0,  # type: int
        max_left_offset=0,  # type: int
        max_right_offset=0,  # type: int
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with floating region specified in the arguments.
            | =Arguments=       | =Description=                                                                                |
            | Selector          | The selector to become floating region e.g. //*[@id="logo"]                                  |
            | Max Up Offset     | The maximum amount that the region can shift upwards and still be considered matching.       |
            | Max Down Offset   | The maximum amount that the region can shift downwards and still be considered matching.     |
            | Max Left Offset   | The maximum amount that the region can shift to the left and still be considered matching.   |
            | Max Right Offset  | The maximum amount that the region can shift to the right and still be considered matching.  |

        *Example:*
            | Eyes Check Window                       |                  |     |     |     |      |
            | ...     Floating Region By Selector     |  //*[@id="logo"] |  5  |  5  |  5  |  5   |
            | ...     Floating Region By Selector     |  //*[@id="logo"] |  max_left_offset=5 |   |   |    |
        """
        return new_or_cur_check_settings(check_settings).floating(
            self.from_locators_to_supported_form(selector)[0],
            max_up_offset,
            max_down_offset,
            max_left_offset,
            max_right_offset,
        )


class AccessibilityCheckSettingsKeywords:
    @keyword("Accessibility Region By Selector", types=(str, str))
    def accessibility_region_by_selector(
        self,
        selector,  # type: Text
        type,  # type: AccessibilityRegionType
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with accessibility region specified in the arguments.
            | =Arguments=   |   =Description=                                          |
            | Selector      |  *Mandatory* - The selector for element for accessibility region. Selenium/Appium formats are supported. |
            | Type          | *Mandatory* - Type of AccessibilityRegion. (`IgnoreContrast`, `RegularText`, `LargeText`, `BoldText`, `GraphicalObject`)    |

        *Example:*
            | Eyes Check                                |              |                  |
            | ...     Accessibility Region By Selector  |  //selector  |  GraphicalObject |
        """
        return new_or_cur_check_settings(check_settings).accessibility(
            *self.from_locators_to_supported_form(selector),
            type=AccessibilityRegionType(type)
        )

    @keyword(
        "Accessibility Region By Element",
        types={"element": (SeleniumWebElement, AppiumWebElement), "type": str},
    )
    def accessibility_region_by_element(
        self,
        element,  # type: Text
        type,  # type: AccessibilityRegionType
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with accessibility region specified in the arguments.
            | =Arguments=      | =Description=                                                            |
            | Element          | *Mandatory* - The accessibility region e.g. [100 200 300 300]                                                             |
            | Type             | *Mandatory* - Type of AccessibilityRegion. (`IgnoreContrast`, `RegularText`, `LargeText`, `BoldText`, `GraphicalObject`)  |

        *Example:*
            | Eyes Check                                   |              |                   |
            | ...     Accessibility Region By Coordinates  |  ${element}  |  GraphicalObject  |
        """
        is_webelement_guard(element)
        return new_or_cur_check_settings(check_settings).accessibility(
            element, type=AccessibilityRegionType(type)
        )

    @keyword(
        "Accessibility Region By Coordinates",
        types=(str, str),
    )
    def accessibility_region_by_coordinates(
        self,
        region,  # type: Text
        type,  # type: AccessibilityRegionType
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with accessibility region specified in the arguments.
            | =Arguments=      | =Description=                                                            |
            | Region           | *Mandatory* - The accessibility region e.g. [100 200 300 300]                                                        |
            | Type             | *Mandatory* - Type of AccessibilityRegion. (`IgnoreContrast`, `RegularText`, `LargeText`, `BoldText`, `GraphicalObject`)    |

        *Example:*
            | Eyes Check                                   |                 |                   |
            | ...     Accessibility Region By Coordinates  |  [10 20 30 40]  |  GraphicalObject  |
        """
        return new_or_cur_check_settings(check_settings).accessibility(
            region=parse_region(region), type=AccessibilityRegionType(type)
        )


class UFGCheckSettingsKeywords:
    @keyword("Visual Grid Option", types=(str, str))
    def visual_grid_option(
        self,
        name,  # type: Text
        value,  # type: Text
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with VisualGridOption specified in the arguments.
            | =Arguments=   | =Description=                              |                                                           |
            | name          | *Mandatory* - The VisualGridOption name.   |                                                     |                                                         |
            | value         | *Mandatory* - The VisualGridOption value.  |

        *Example:*
            | Eyes Check                  |
            | ...     Visual Grid Option  |  key name     value   |
            | ...     Visual Grid Option  |  key name2    value   |
        """
        return new_or_cur_check_settings(check_settings).visual_grid_options(
            VisualGridOption(name, value)
        )

    @keyword("Disable Browser Fetching", types=(bool,))
    def disable_browser_fetching(
        self,
        disable=True,  # type:bool
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with disable_browser_fetching specified in the arguments.
            | =Arguments=      | =Description=               |
            | disable          | Disable browser fetching    |

        *Example:*
            | Eyes Check                        |           |
            | ...     Disable Browser Fetching  |           |
            | ...     Disable Browser Fetching  |  False    |
        """
        return new_or_cur_check_settings(check_settings).disable_browser_fetching(
            disable
        )

    @keyword("Enable Layout Breakpoints", types=(bool,))
    def layout_breakpoints(
        self,
        enable=True,  # type:bool
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with enabled layout_breakpoints specified in the arguments.
            | =Arguments=   | =Description=               |
            | enable        | Enable layout breakpoints   |

        *Example:*
            | Eyes Check                         |          |
            | ...     Enable Layout Breakpoints  |          |
            | ...     Enable Layout Breakpoints  |  False   |
        """
        return new_or_cur_check_settings(check_settings).layout_breakpoints(enable)

    @keyword("Layout Breakpoints", types=(str,))
    def layout_breakpoints(
        self,
        breakpoints,  # type:str
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object specified layout_breakpoints in the arguments.
            | =Arguments=     | =Description=                             |
            | breakpoints     | Specify layout breakpoint, e.g. 25 56 89  |

        *Example:*
            | Eyes Check                  |             |
            | ...     Layout Breakpoints  |             |
            | ...     Layout Breakpoints  |   False     |
        """
        breakpoints = [int(b) for b in breakpoints.split(" ")]
        return new_or_cur_check_settings(check_settings).layout_breakpoints(
            *breakpoints
        )

    @keyword("Before Render Screenshot Hook", types=(str,))
    def before_render_screenshot_hook(
        self,
        hook,  # type:str
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        return new_or_cur_check_settings(check_settings).before_render_screenshot_hook(
            hook
        )

    @keyword("Use Dom", types=(bool,))
    def use_dom(
        self,
        use,  # type:bool
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        return new_or_cur_check_settings(check_settings).use_dom(use)

    @keyword("Send Dom", types=(bool,))
    def send_dom(
        self,
        senddom,  # type:bool
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        return new_or_cur_check_settings(check_settings).send_dom(senddom)


class CheckSettingsKeywords(
    LibraryComponent,
    IgnoreCheckSettingsKeyword,
    LayoutCheckSettingsKeyword,
    ContentCheckSettingsKeyword,
    StrictCheckSettingsKeywords,
    FloatingCheckSettingsKeywords,
    AccessibilityCheckSettingsKeywords,
    UFGCheckSettingsKeywords,
):
    @keyword("Scroll Root Element By Selector")
    def scroll_root_element_by_selector(
        self,
        selector,  # type: Locator
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        return new_or_cur_check_settings(check_settings).scroll_root_element(
            self.from_locator_to_supported_form(selector)
        )

    @keyword("Scroll Root Element By Element")
    def scroll_root_element_by_element(
        self,
        element,  # type: Locator
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        is_webelement_guard(element)
        return new_or_cur_check_settings(check_settings).scroll_root_element(element)

    @keyword("Variant Group Id", types=(str,))
    def variation_group_id(
        self,
        variation_group_id,  # type: Text
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object specified variant group id.
            | =Arguments=  | =Description=                                                      |
            | variation_group_id  | will be associated with all of the test result steps that result from executing this checkpoint |

        *Example:*
            | Eyes Check   |  Target Window  |  Variant Group Id  |  variation1 |
        """
        return new_or_cur_check_settings(check_settings).variation_group_id(
            variation_group_id
        )

    @keyword("Match Level", types=(str,), tags=(CHECK_SETTING,))
    def match_level(
        self,
        match_level,  # type: Text
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object specified match level.
            | =Arguments=  | =Description=                                                      |
            | match_level  | Specify the match level that should be used for the target area (NONE LAYOUT CONTENT STRICT EXACT) |

        *Example:*
            | Eyes Check   |  Target Window  |  Match Level  STRICT |
        """
        match_level = MatchLevel(match_level.upper())
        return new_or_cur_check_settings(check_settings).match_level(match_level)

    @keyword("Enable Patterns", types=(bool,), tags=(CHECK_SETTING,))
    def enable_patterns(
        self,
        enable=True,  # type: bool
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        return new_or_cur_check_settings(check_settings).enable_patterns(enable)

    @keyword("Ignore Displacements", types=(bool,), tags=(CHECK_SETTING,))
    def ignore_displacements(
        self,
        should_ignore=True,  # type: bool
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object specified ignore displacements.
            | =Arguments=     | =Description=                                                             |
            |  should_ignore  | Specifies the state of the ignore displacements flag for this checkpoint  |

        *Example:*
            | Eyes Check   |  Target Window  |  Ignore Displacements |
        """
        return new_or_cur_check_settings(check_settings).ignore_displacements(
            should_ignore
        )

    @keyword("Ignore Caret", types=(bool,), tags=(CHECK_SETTING,))
    def ignore_caret(
        self,
        ignore=True,  # type: bool
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object specified ignore caret.
            | =Arguments=  | =Description=                                                                |
            |  ignore      | Specify that Eyes should eliminate mismatches reported because of artifacts introduced by a blinking cursor |

        *Example:*
            | Eyes Check   |  Target Window  |  Ignore Caret |
        """
        return new_or_cur_check_settings(check_settings).ignore_caret(ignore)

    @keyword("Fully", types=(bool,), tags=(CHECK_SETTING,))
    def fully(
        self,
        fully=True,  # type: bool
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object specified fully.
            | =Arguments=  | =Description=                                                                     |
            |  fully       | Request that the entire content on the page is matched and not just the viewport  |

        *Example:*
            | Eyes Check   |  Target Window  |  Fully |
        """
        return new_or_cur_check_settings(check_settings).ignore_caret(fully)

    @keyword("With Name", types=(str,), tags=(CHECK_SETTING,))
    def with_name(
        self,
        name,  # type: Text
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object specified tag from argument.
            | =Arguments=  | =Description=                                                                |
            | name         | Specifies a tag for this target (instead of a parameter to the Eyes Check )  |

        *Example:*
            | Eyes Check         |    Target Window        |
            | ...     With Name  |   User Check Step name  |
        """
        return new_or_cur_check_settings(check_settings).with_name(name)

    @keyword("Timeout", types=(int,), tags=(CHECK_SETTING,))
    def timeout(
        self,
        timeout,  # type: int
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object specified maximum amount of time that Eyes should retry capturing the window content if there are mismatches.
            | =Arguments=  | =Description=                                       |
            | timeout      | Specify timeout in milliseconds, e.g. 1000 (1 sec)  |

        *Example:*
            | Eyes Check         |    Target Window    |
            | ...     Timeout    |   3000              |
        """
        return new_or_cur_check_settings(check_settings).timeout(timeout)
