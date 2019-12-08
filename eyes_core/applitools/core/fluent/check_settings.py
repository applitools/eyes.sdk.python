from typing import TYPE_CHECKING, List, Optional, Text, TypeVar, overload

import attr

from applitools.common import FloatingBounds, MatchLevel, Region, logger

from .region import (
    FloatingRegionByRectangle,
    GetFloatingRegion,
    GetRegion,
    RegionByRectangle,
)

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import Num

__all__ = ("CheckSettings", "CheckSettingsValues")


@attr.s
class CheckSettingsValues(object):
    """
    Access to values stored in :py:class:`CheckSettings`
    """

    target_region = attr.ib(init=False, default=None)  # type: Optional[Region]
    timeout = attr.ib(init=False, default=-1)  # type: Num  # milliseconds

    ignore_caret = attr.ib(init=False, default=None)  # type: Optional[bool]
    stitch_content = attr.ib(init=False, default=None)  # type: Optional[bool]
    match_level = attr.ib(init=False, default=None)  # type: Optional[MatchLevel]
    name = attr.ib(init=False, default=None)  # type: Optional[Text]

    send_dom = attr.ib(init=False, default=None)  # type: Optional[bool]
    use_dom = attr.ib(init=False, default=None)  # type: Optional[bool]
    enable_patterns = attr.ib(init=False, default=None)  # type: Optional[bool]
    ignore_displacements = attr.ib(init=False, default=None)  # type: Optional[bool]

    ignore_regions = attr.ib(init=False, factory=list)  # type: List[GetRegion]
    layout_regions = attr.ib(init=False, factory=list)  # type: List[GetRegion]
    strict_regions = attr.ib(init=False, factory=list)  # type: List[GetRegion]
    content_regions = attr.ib(init=False, factory=list)  # type: List[GetRegion]
    floating_regions = attr.ib(
        init=False, factory=list
    )  # type: List[GetFloatingRegion]


Self = TypeVar("Self", bound="CheckSettings")  # typedef


@attr.s
class CheckSettings(object):
    """
    The Match settings object to use in the various Eyes.Check methods.
    """

    values = attr.ib(
        init=False, factory=CheckSettingsValues
    )  # type: CheckSettingsValues

    def layout(self, *regions):
        # type: (Self, *Region)  -> Self
        """ Shortcut to set the match level to :py:attr:`MatchLevel.LAYOUT`. """
        self.values.match_level = MatchLevel.LAYOUT
        if not regions:
            return self
        self.values.layout_regions = self.__regions(
            regions, method_name="layout_regions"
        )
        return self

    def exact(self):
        """ Shortcut to set the match level to :py:attr:`MatchLevel.EXACT`. """
        self.values.match_level = MatchLevel.EXACT
        return self

    def strict(self, *regions):
        # type: (Self, *Region)  -> Self
        """ Shortcut to set the match level to :py:attr:`MatchLevel.STRICT`. """
        self.values.match_level = MatchLevel.STRICT
        if not regions:
            return self
        self.values.strict_regions = self.__regions(
            regions, method_name="strict_regions"
        )
        return self

    def content(self, *regions):
        # type: (Self, *Region)  -> Self
        """ Shortcut to set the match level to :py:attr:`MatchLevel.CONTENT`. """
        self.values.match_level = MatchLevel.CONTENT
        if not regions:
            return self
        self.values.content_regions = self.__regions(
            regions, method_name="content_regions"
        )
        return self

    def ignore(self, *regions):
        # type: (Self, *Region)  -> Self
        """ Adds one or more ignore regions. """
        self.values.ignore_regions = self.__regions(
            regions, method_name="ignore_regions"
        )
        return self

    @overload  # noqa
    def floating(self, max_offset, region):
        # type: (Self, int, Region) -> Self
        pass

    @overload  # noqa
    def floating(
        self, region, max_up_offset, max_down_offset, max_left_offset, max_right_offset
    ):
        # type: (Self, Region, int, int, int, int) -> Self
        pass

    def floating(self, *args):  # noqa
        """
        Adds a floating region. Region and max_offset or [max_up_offset, max_down_offset, "
                "max_left_offset, max_right_offset] are required parameters.

        :param arg1: max_offset | Region
        :param arg2: Region     | max_up_offset
        :param arg3: None       | max_down_offset
        :param arg4: None       | max_left_offset
        :param arg5: None       | max_right_offset
        """
        if isinstance(args[0], int) and isinstance(args[1], Region):
            max_offset = args[0]  # type: int
            region = args[1]  # type: ignore
            bounds = FloatingBounds(
                max_up_offset=max_offset,
                max_down_offset=max_offset,
                max_left_offset=max_offset,
                max_right_offset=max_offset,
            )
        elif (
            isinstance(args[1], int)
            and isinstance(args[2], int)
            and isinstance(args[3], int)
            and isinstance(args[4], int)
        ):
            region = args[0]  # type: ignore
            bounds = FloatingBounds(
                max_up_offset=args[1],
                max_down_offset=args[2],
                max_left_offset=args[3],
                max_right_offset=args[4],
            )
        else:
            raise TypeError("Unsupported parameters")
        logger.info("Adding Region {} with FloatingBounds {}".format(region, bounds))
        region_or_container = self._floating_provider_from(region, bounds)
        self.values.floating_regions.append(region_or_container)
        return self

    def send_dom(self, senddom=True):
        # type: (Self, bool) -> Self
        """
         Defines whether to send the document DOM or not.
        """
        self.values.send_dom = senddom
        return self

    def use_dom(self, use=True):
        # type: (Self, bool) -> Self
        """
         Defines useDom for enabling the match algorithm to use dom.
        """
        self.values.use_dom = use
        return self

    def enable_patterns(self, enable=True):
        # type: (Self, bool) -> Self
        self.values.enable_patterns = enable
        return self

    def ignore_displacements(self, should_ignore=True):
        # type: (Self, bool) -> Self
        self.values.ignore_displacements = should_ignore
        return self

    def match_level(self, match_level):
        # type: (Self, MatchLevel)  -> Self
        self.values.match_level = match_level
        return self

    def ignore_caret(self, ignore=True):
        # type: (Self, bool)  -> Self
        self.values.ignore_caret = ignore
        return self

    def fully(self, fully=True):
        # type: (Self, bool)  -> Self
        self.values.stitch_content = fully
        return self

    def with_name(self, name):
        # type: (Self, Text)  -> Self
        self.values.name = name
        return self

    def stitch_content(self, stitch_content=True):
        # type: (Self, bool)  -> Self
        self.values.stitch_content = stitch_content
        return self

    def timeout(self, timeout):
        # type: (Self, int)  -> Self
        self.values.timeout = timeout
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
            logger.debug("{name}: RegionByRegion".format(name=method_name))
            return RegionByRectangle(region)
        raise TypeError("Unknown region type.")

    def _floating_provider_from(self, region, bounds):
        if isinstance(region, Region):
            logger.debug("floating: FloatingRegionByRectangle")
            return FloatingRegionByRectangle(Region.from_(region), bounds)
        raise TypeError("Unknown region type.")
