from typing import TYPE_CHECKING, Optional, Text

from appium.webdriver import WebElement as AppiumWebElement
from EyesLibrary.base import LibraryComponent
from robot.api.deco import keyword
from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement

from applitools.common import (
    AccessibilityRegionType,
    MatchLevel,
    Region,
    VisualGridOption,
)
from applitools.selenium.fluent import SeleniumCheckSettings

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import REGION_VALUES


class IgnoreCheckSettingsKeyword:
    @keyword("Ignore Region By Coordinates", types=(int, int, int, int))
    def ignore_region_by_coordinates(
        self,
        left,  # type: int
        top,  # type: int
        width,  # type: int
        height,  # type: int
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object that ignores the region specified in the arguments.
            | =Arguments=   | =Description=                                                       |
            | Left          | *Mandatory* - The left coordinate of the region to ignore e.g. 100  |
            | Top           | *Mandatory* - The top coordinate of the region to ignore e.g. 150   |
            | Width         | *Mandatory* - The width of the region to ignore e.g. 500            |
            | Height        | *Mandatory* - The height of the region to ignore e.g. 120           |

        *Example:*
            | ${target}=        | Ignore Region By Coordinates          | 10  20  100  100  |
            | Eyes Check        | Google Homepage                       | target=${target}  |
        *Example:*
            | ${target}=           | Ignore Region By Coordinates       | 40  59  67  44    |
            | Eyes Check           | ${target}                          |                   |
            | Eyes Check Window    | Google Homepage                    |                   |
            | ...   Ignore Region By Coordinates                        | 40  59  67  44    |
        """
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.ignore(Region(left, top, width, height))

    @keyword("Ignore Region")
    def ignore_region(
        self,
        locator,  # type:REGION_VALUES
        check_settings=None,  # type: Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object that ignores the region of the element specified in the arguments.
            | =Arguments=    | =Description=                           |
            | Locator        | *Mandatory* - The WebElement to ignore  |

        *Example:*
            | ${element}=          | Get Webelement      | //*[@id="hplogo"] |              |
            | ${target}=           | Ignore Region       | ${element}        |              |
            | ${target}=           | Ignore Region       | //*[@id="hplogo"] |   ${target}  |
            | Eyes Check           | ${target}           |                   |              |
            | Eyes Check Window    | Google Homepage     |                   |              |
            | ...   Ignore Region  | //*[@id="hplogo"]   |                   |              |
            | ...   Ignore Region  | ${element}          |                   |              |
        """
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.ignore(locator)


class LayoutCheckSettingsKeyword:
    @keyword("Layout Region By Coordinates", types=(int, int, int, int))
    def layout_region_by_coordinates(
        self,
        left,  # type: int
        top,  # type: int
        width,  # type: int
        height,  # type: int
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with layout region specified in the arguments.
            | =Arguments=  | =Description=                                                  |
            | Left    | *Mandatory* - The left coordinate of the region to layout e.g. 100  |
            | Top     | *Mandatory* - The top coordinate of the region to layout e.g. 150   |
            | Width   | *Mandatory* - The width of the region to layout e.g. 500            |
            | Height  | *Mandatory* - The height of the region to layout e.g. 120           |

        *Example:*
            | ${target}=        | Layout Region By Coordinates          | 10  20  100  100 |
            | Eyes Check        | Google Homepage                       |  ${target}       |
        *Example:*
            | ${target}=           | Layout Region By Coordinates       | 40  59  67  44  |
            | Eyes Check           | ${target}                          |                 |
            | Eyes Check Window    | Google Homepage                    |                 |
            | ...   Ignore Region By Coordinates                        | 40  59  67  44  |
        """
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.layout(Region(left, top, width, height))

    @keyword("Layout Region")
    def layout_region(
        self,
        locator,  # type:REGION_VALUES
        check_settings=None,  # type: Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with layout region specified in the arguments.
            | =Arguments=   | =Description=                            |
            | Locator       | *Mandatory* - The WebElement to layout   |

        *Example:*
            | ${element}=          | Get Webelement      | //*[@id="hplogo"] |              |
            | ${target}=           | Layout Region       | ${element}        |              |
            | ${target}=           | Layout Region       | //*[@id="hplogo"] |   ${target}  |
            | Eyes Check           | ${target}           |                   |              |
            | Eyes Check Window    | Google Homepage     |                   |              |
            | ...   Layout Region  | //*[@id="hplogo"]   |                   |              |
            | ...   Layout Region  | ${element}          |                   |              |
        """
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.layout(locator)


class ContentCheckSettingsKeyword:
    @keyword("Content Region", types=(int, int, int, int))
    def content_region_by_coordinates(
        self,
        left,  # type: int
        top,  # type: int
        width,  # type: int
        height,  # type: int
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.content(Region(left, top, width, height))

    @keyword("Content Region")
    def content_region(
        self,
        locator,  # type:REGION_VALUES
        check_settings=None,  # type: Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.content(locator)


class StrictCheckSettingsKeywords:
    @keyword("Strict Region", types=(int, int, int, int))
    def strict_region_by_coordinates(
        self,
        left,  # type: int
        top,  # type: int
        width,  # type: int
        height,  # type: int
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.strict(Region(left, top, width, height))

    @keyword("Strict Region")
    def strict_region(
        self,
        locator,  # type:REGION_VALUES
        check_settings=None,  # type: Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.strict(locator)


class FloatingCheckSettingsKeywords:
    @keyword(
        "Floating Region By Coordinates With Max Offset",
        types=(int, int, int, int, int),
    )
    def floating_region_by_coordinates_with_max_offset(
        self,
        max_offset,  # type: int
        left,  # type: int
        top,  # type: int
        width,  # type: int
        height,  # type: int
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with floating region specified in the arguments.
            | =Arguments=  | =Description=                                                                                                 |
            | Max Offset   | *Mandatory* - The maximum amount that the region can shift in any direction and still be considered matching. |
            | Left         | *Mandatory* - The left coordinate of the floating e.g. 100                                                    |
            | Top          | *Mandatory* - The top coordinate of the floating e.g. 150                                                     |
            | Width        | *Mandatory* - The width of the floating region e.g. 500                                                       |
            | Height       | *Mandatory* - The height of the floating region e.g. 120                                                      |

        *Example:*
            | Eyes Check                                            |                        |
            | ...   Floating Region By Coordinates With Max Offset  | 5  10  20  100  100    |
        """
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        region = Region(left, top, width, height)
        return check_settings.floating(max_offset, region)

    @keyword(
        "Floating Region By Coordinates", types=(int, int, int, int, int, int, int, int)
    )
    def floating_region_by_coordinates(
        self,
        left,  # type: int
        top,  # type: int
        width,  # type: int
        height,  # type: int
        max_up_offset,  # type: int
        max_down_offset,  # type: int
        max_left_offset,  # type: int
        max_right_offset,  # type: int
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with floating region specified in the arguments.
            | =Arguments=       | =Description=                                                                                              |
            | Left              | *Mandatory* - The left coordinate of the floating e.g. 100                                                 |
            | Top               | *Mandatory* - The top coordinate of the floating e.g. 150                                                  |
            | Width             | *Mandatory* - The width of the floating region e.g. 500                                                   s |
            | Height            | *Mandatory* - The height of the floating region e.g. 120                                                   |
            | Max Up Offset     | *Mandatory* - The maximum amount that the region can shift upwards and still be considered matching.       |
            | Max Down Offset   | *Mandatory* - The maximum amount that the region can shift downwards and still be considered matching.     |
            | Max Left Offset   | *Mandatory* - The maximum amount that the region can shift to the left and still be considered matching.   |
            | Max Right Offset  | *Mandatory* - The maximum amount that the region can shift to the right and still be considered matching.  |

        *Example:*
            | Eyes Check                              |                                |
            | ...     Floating Region By Coordinates  | 10  20  100  100  5  5  5  5   |
        """
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        region = Region(left, top, width, height)
        return check_settings.floating(
            region, max_up_offset, max_down_offset, max_left_offset, max_right_offset
        )

    @keyword(
        "Floating Region With Max Offset",
        types={
            "max_offset": int,
            "locator": (str, AppiumWebElement, SeleniumWebElement),
        },
    )
    def floating_region_with_max_offset(
        self,
        max_offset,  # type: int
        locator,  # type: REGION_VALUES
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with floating region specified in the arguments.
            | =Arguments=   | =Description=                                                                                                    |
            | Max Offset    | *Mandatory* - The maximum amount that the region can shift in any direction and still be considered matching.    |
            | Locator       | *Mandatory* - The WebElement to set as float region                                                              |

        *Example:*
            | Eyes Check                               |                       |
            | ...     Floating Region With Max Offset  | 5  10  20  100  100   |
        """
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.floating(max_offset, locator)

    @keyword(
        "Floating Region",
        types={
            "max_up_offset": int,
            "max_down_offset": int,
            "max_left_offset": int,
            "max_right_offset": int,
        },
    )
    def floating_region(
        self,
        locator,  # type: REGION_VALUES
        max_up_offset,  # type: int
        max_down_offset,  # type: int
        max_left_offset,  # type: int
        max_right_offset,  # type: int
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with floating region specified in the arguments.
            | =Arguments=      | =Description=                                                                                                       |
            | Locator          | *Mandatory* - The WebElement to set as float region.                                                  |
            | Max Up Offset    | *Mandatory* - The maximum amount that the region can shift upwards and still be considered matching.             |
            | Max Down Offset  | *Mandatory* - The maximum amount that the region can shift downwards and still be considered matching.         |
            | Max Left Offset  | *Mandatory* - The maximum amount that the region can shift to the left and still be considered matching.       |
            | Max Right Offset | *Mandatory* - The maximum amount that the region can shift to the right and still be considered matching.     |

        *Example:*
            | Eyes Check               |                                |
            | ...     Floating Region  | 10  20  100  100  5  5  5  5   |
        """
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.floating(
            locator, max_up_offset, max_down_offset, max_left_offset, max_right_offset
        )


class AccessibilityCheckSettingsKeywords:
    @keyword("Accessibility Region", types={"type": str})
    def accessibility_region(
        self,
        locator,  # type: REGION_VALUES
        type,  # type: AccessibilityRegionType
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with accessibility region specified in the arguments.
            | =Arguments=   |   =Description=                                                          |
            | Locator       | *Mandatory* - The WebElement to set as float region.     |
            | Type          | *Mandatory* - Type of AccessibilityRegion. (`IgnoreContrast`, `RegularText`, `LargeText`, `BoldText`, `GraphicalObject`)    |



        *Example:*
            | Eyes Check                    |                                   |
            | ...     Accessibility Region  |  //selector    GraphicalObject    |
        """
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.accessibility(locator, AccessibilityRegionType(type))

    @keyword("Accessibility Region By Coordinates", types=(int, int, int, int))
    def accessibility_region_by_coordinates(
        self,
        left,  # type: int
        top,  # type: int
        width,  # type: int
        height,  # type: int
        type,  # type: AccessibilityRegionType
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        """
        Returns a CheckSettings object with accessibility region specified in the arguments.
            | =Arguments=      | =Description=                                                            |
            | Left             | *Mandatory* - The left coordinate of the accessibility region e.g. 100   |
            | Top              | *Mandatory* - The top coordinate of the accessibility region e.g. 150    |
            | Width            | *Mandatory* - The width of the accessibility region e.g. 500             |
            | Height           | *Mandatory* - The height of the accessibility region e.g. 120            |
            | Type             | *Mandatory* - Type of AccessibilityRegion. (`IgnoreContrast`, `RegularText`, `LargeText`, `BoldText`, `GraphicalObject`)    |

        *Example:*
            | Eyes Check                    |                                  |
            | ...     Accessibility Region  |  //selector    GraphicalObject   |
        """
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.accessibility(
            Region(left, top, width, height), AccessibilityRegionType(type)
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
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.visual_grid_options(VisualGridOption(name, value))

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
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.disable_browser_fetching(disable)

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
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.layout_breakpoints(enable)

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
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        breakpoints = [int(b) for b in breakpoints.split(" ")]
        return check_settings.layout_breakpoints(*breakpoints)

    @keyword("Before Render Screenshot Hook", types=(str,))
    def before_render_screenshot_hook(
        self,
        hook,  # type:str
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.before_render_screenshot_hook(hook)

    @keyword("Use Dom", types=(bool,))
    def use_dom(
        self,
        use,  # type:bool
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.use_dom(use)

    @keyword("Send Dom", types=(bool,))
    def send_dom(
        self,
        senddom,  # type:bool
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.send_dom(senddom)


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
    @keyword("Scroll Root Element")
    def scroll_root_element(
        self,
        locator,  # type: REGION_VALUES
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.scroll_root_element(locator)

    @keyword("Variant Group Id", types=(str,))
    def variation_group_id(
        self,
        variation_group_id,  # type: Text
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.variation_group_id(variation_group_id)

    @keyword("Match Level")
    def match_level(
        self,
        match_level,  # type: MatchLevel
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        match_level = MatchLevel(match_level)
        return check_settings.match_level(match_level)

    @keyword("Enable Patterns", types=(bool,))
    def enable_patterns(
        self,
        enable=True,  # type: bool
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.enable_patterns(enable)

    @keyword("Ignore Displacements", types=(bool,))
    def ignore_displacements(
        self,
        should_ignore=True,  # type: bool
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.ignore_displacements(should_ignore)

    @keyword("Ignore Caret", types=(bool,))
    def ignore_caret(
        self,
        ignore=True,  # type: bool
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.ignore_caret(ignore)

    @keyword("Fully", types=(bool,))
    def fully(
        self,
        fully=True,  # type: bool
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.ignore_caret(fully)

    @keyword("With Name", types=(str,))
    def with_name(
        self,
        name,  # type: Text
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.with_name(name)

    @keyword("Timeout", types=(int,))
    def timeout(
        self,
        timeout,  # type: int
        check_settings=None,  # type:Optional[SeleniumCheckSettings]
    ):
        # type: (...)->SeleniumCheckSettings
        if check_settings is None:
            check_settings = SeleniumCheckSettings()
        return check_settings.timeout(timeout)
