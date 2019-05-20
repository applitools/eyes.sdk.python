import typing

import attr
from applitools.common import FloatingBounds, MatchLevel, Region, logger

from .region import (
    FloatingRegionByRectangle,
    GetFloatingRegion,
    GetRegion,
    IgnoreRegionByRectangle,
)

if typing.TYPE_CHECKING:
    from typing import Text, Optional, List, Union, Tuple
    from applitools.common.utils.custom_types import AnyWebElement, Num

    REGION_VALUES = Union[Region, Text, AnyWebElement, Tuple[Text, Text]]
    FLOATING_VALUES = Union[Region, Text, AnyWebElement, Tuple[Text, Text]]
    GR = typing.TypeVar("GR", bound=GetRegion)
    FR = typing.TypeVar("FR", bound=GetFloatingRegion)

__all__ = ("CheckSettings", "CheckSettingsValues")


@attr.s
class CheckSettingsValues(object):
    """
    Access to values stored in :py:class:`CheckSettings`
    """

    target_region = attr.ib(init=False, default=None)  # type: Optional[Region]
    timeout = attr.ib(init=False, default=-1)  # type: Num  # milliseconds

    ignore_caret = attr.ib(init=False, default=False)  # type: bool
    stitch_content = attr.ib(init=False, default=False)  # type: bool
    match_level = attr.ib(init=False, default=None)  # type: Optional[MatchLevel]
    name = attr.ib(init=False, default=None)  # type: Optional[Text]

    send_dom = attr.ib(init=False, default=False)  # type: bool
    use_dom = attr.ib(init=False, default=False)
    enable_patterns = attr.ib(init=False, default=False)
    ignore_regions = attr.ib(init=False, factory=list)  # type: List[GetRegion]
    layout_regions = attr.ib(init=False, factory=list)  # type: List[GetRegion]
    strict_regions = attr.ib(init=False, factory=list)  # type: List[GetRegion]
    content_regions = attr.ib(init=False, factory=list)  # type: List[GetRegion]
    floating_regions = attr.ib(
        init=False, factory=list
    )  # type: List[GetFloatingRegion]


@attr.s
class CheckSettings(object):
    """
    The Match settings object to use in the various Eyes.Check methods.
    """

    values = attr.ib(init=False)

    def __attrs_post_init__(self):
        # type: () -> None
        self.values = CheckSettingsValues()

    def layout(self):
        # type: ()  -> CheckSettings
        """ Shortcut to set the match level to :py:attr:`MatchLevel.LAYOUT`. """
        self.values.match_level = MatchLevel.LAYOUT
        return self

    def exact(self):
        # type: ()  -> CheckSettings

        """ Shortcut to set the match level to :py:attr:`MatchLevel.EXACT`. """
        self.values.match_level = MatchLevel.EXACT
        return self

    def strict(self):
        # type: ()  -> CheckSettings
        """ Shortcut to set the match level to :py:attr:`MatchLevel.STRICT`. """
        self.values.match_level = MatchLevel.STRICT
        return self

    def content(self):
        # type: ()  -> CheckSettings
        """ Shortcut to set the match level to :py:attr:`MatchLevel.CONTENT`. """
        self.values.match_level = MatchLevel.CONTENT
        return self

    def match_level(self, match_level):
        # type: (MatchLevel)  -> CheckSettings
        self.values.match_level = match_level
        return self

    def ignore_caret(self, ignore=True):
        # type: (bool)  -> CheckSettings
        self.values.ignore_caret = ignore
        return self

    def fully(self, fully=True):
        # type: (bool)  -> CheckSettings
        self.values.stitch_content = fully
        return self

    def with_name(self, name):
        # type: (Text)  -> CheckSettings
        self.values.name = name
        return self

    def stitch_content(self, stitch_content=True):
        # type: (bool)  -> CheckSettings
        self.values.stitch_content = stitch_content
        return self

    def timeout(self, timeout):
        # type: (int)  -> CheckSettings
        self.values.timeout = timeout
        return self

    def update_target_region(self, region):
        # type: (Region)  -> None
        self.values.target_region = region

    def ignore_regions(self, *regions):
        # type: (*REGION_VALUES)  -> CheckSettings
        """ Adds one or more ignore regions. """
        self.values.ignore_regions = self.__regions(
            regions, method_name="ignore_regions"
        )
        return self

    ignore = ignore_regions

    def layout_regions(self, *regions):
        # type: (*REGION_VALUES)  -> CheckSettings
        """ Adds one or more layout regions. """
        self.values.layout_regions = self.__regions(
            regions, method_name="layout_regions"
        )
        return self

    def strict_regions(self, *regions):
        # type: (*REGION_VALUES)  -> CheckSettings
        """ Adds one or more strict regions. """
        self.values.strict_regions = self.__regions(
            regions, method_name="strict_regions"
        )
        return self

    def content_regions(self, *regions):
        # type: (*REGION_VALUES)  -> CheckSettings
        """ Adds one or more content regions. """
        self.values.content_regions = self.__regions(
            regions, method_name="content_regions"
        )
        return self

    def floating_region(
        self,
        arg1,  # type: Union[REGION_VALUES, int]
        arg2,  # type: Union[REGION_VALUES, int]
        arg3=None,  # type: Optional[int]
        arg4=None,  # type: Optional[int]
        arg5=None,  # type: Optional[int]
    ):
        # type: (...) -> CheckSettings
        """
        Adds a floating region. Region and max_offset or [max_up_offset, max_down_offset, "
                "max_left_offset, max_right_offset] are required parameters.

        :param arg1: max_offset | Region
        :param arg2: Region     | max_up_offset
        :param arg3: None       | max_down_offset
        :param arg4: None       | max_left_offset
        :param arg5: None       | max_right_offset
        """
        if isinstance(arg1, int) and isinstance(arg2, Region):
            max_offset = arg1  # type: int
            region = arg2  # type: Region
            bounds = FloatingBounds(
                max_up_offset=max_offset,
                max_down_offset=max_offset,
                max_left_offset=max_offset,
                max_right_offset=max_offset,
            )
        elif (
            isinstance(arg2, int)
            and isinstance(arg3, int)
            and isinstance(arg4, int)
            and isinstance(arg5, int)
        ):
            region = arg1
            bounds = FloatingBounds(
                max_up_offset=arg2,
                max_down_offset=arg3,
                max_left_offset=arg4,
                max_right_offset=arg5,
            )
        else:
            raise TypeError("Unsupported parameters")
        logger.info("Adding Region {} with FloatingBounds {}".format(region, bounds))
        region_or_container = self._floating_provider_from(region, bounds)
        self.values.floating_regions.append(region_or_container)
        return self

    floating = floating_region

    def send_dom(self, send=True):
        # type: (bool) -> CheckSettings
        """
         Defines whether to send the document DOM or not.
        """
        self.values.send_dom = send
        return self

    def use_dom(self, use=True):
        # type: (bool) -> CheckSettings
        """
         Defines useDom for enabling the match algorithm to use dom.
        """
        self.values.use_dom = use
        return self

    def enable_patterns(self, enable=True):
        # type: (bool) -> CheckSettings
        self.values.enable_patterns = enable
        return self

    def __regions(self, regions, method_name):
        if not regions:
            raise TypeError(
                "{name} method called without arguments!".format(name=method_name)
            )

        regions_list = getattr(self.values, method_name)
        for region in regions:
            regions_list.append(self._region_provider_from(region, method_name))
        return regions_list

    def _region_provider_from(self, region, method_name):
        logger.debug("calling _{}".format(method_name))
        if isinstance(region, Region):
            logger.debug("{name}: IgnoreRegionByElement".format(name=method_name))
            return IgnoreRegionByRectangle(region)
        raise TypeError("Unknown region type.")

    def _floating_provider_from(self, region, bounds):
        if isinstance(region, Region):
            logger.debug("floating: FloatingRegionByRectangle")
            return FloatingRegionByRectangle(Region.from_(region), bounds)
        raise TypeError("Unknown region type.")
