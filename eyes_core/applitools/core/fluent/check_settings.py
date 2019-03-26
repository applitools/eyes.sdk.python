import typing

import attr

from applitools.common import FloatingBounds, logger
from applitools.common.geometry import Region
from applitools.common.match import MatchLevel
from applitools.common.utils import ABC

from .region import (
    FloatingRegionByRectangle,
    GetFloatingRegion,
    GetRegion,
    IgnoreRegionByRectangle,
)

if typing.TYPE_CHECKING:
    from typing import Text, Optional, List, Union, Tuple
    from applitools.common.utils.custom_types import AnyWebElement

    T = typing.TypeVar("T", bound="CheckSettings")
    REGION_VALUES = Union[Region, Text, AnyWebElement, Tuple[Text, Text]]
    FLOATING_VALUES = Union[Region, Text, AnyWebElement, Tuple[Text, Text]]
    GR = typing.TypeVar("GR", bound=GetRegion)
    FR = typing.TypeVar("FR", bound=GetFloatingRegion)

__all__ = ("CheckSettings",)


@attr.s
class CheckSettingsValues(object):
    """
    Access to values stored in :py:class:`CheckSettings`
    """

    _check_settings = attr.ib(repr=False)  # type: CheckSettings

    def __getattr__(self, attr_name):
        return getattr(self._check_settings, "_{name}".format(name=attr_name))


@attr.s
class CheckSettings(ABC):
    """
    The Match settings object to use in the various Eyes.Check methods.
    """

    _target_region = attr.ib(init=False, default=None)  # type: Optional[Region]
    _timeout = attr.ib(init=False, default=-1)  # type: float  # seconds

    _ignore_caret = attr.ib(init=False, default=False)  # type: bool
    _stitch_content = attr.ib(init=False, default=False)  # type: bool
    _match_level = attr.ib(init=False, default=None)  # type: Optional[MatchLevel]
    _name = attr.ib(init=False, default=None)  # type: Optional[Text]

    _send_dom = attr.ib(init=False, default=False)  # type: bool
    _use_dom = attr.ib(init=False, default=False)
    _enable_patterns = attr.ib(init=False, default=False)
    _ignore_regions = attr.ib(init=False, factory=list)  # type: List[GetRegion]
    _layout_regions = attr.ib(init=False, factory=list)  # type: List[GetRegion]
    _strict_regions = attr.ib(init=False, factory=list)  # type: List[GetRegion]
    _content_regions = attr.ib(init=False, factory=list)  # type: List[GetRegion]
    _floating_regions = attr.ib(
        init=False, factory=list
    )  # type: List[GetFloatingRegion]

    @property
    def values(self):
        return CheckSettingsValues(self)

    def layout(self):
        # type: ()  -> T
        """ Shortcut to set the match level to :py:attr:`MatchLevel.LAYOUT`. """
        self._match_level = MatchLevel.LAYOUT
        return self

    def exact(self):
        # type: ()  -> T

        """ Shortcut to set the match level to :py:attr:`MatchLevel.EXACT`. """
        self._match_level = MatchLevel.EXACT
        return self

    def strict(self):
        # type: ()  -> T
        """ Shortcut to set the match level to :py:attr:`MatchLevel.STRICT`. """
        self._match_level = MatchLevel.STRICT
        return self

    def content(self):
        # type: ()  -> T
        """ Shortcut to set the match level to :py:attr:`MatchLevel.CONTENT`. """
        self._match_level = MatchLevel.CONTENT
        return self

    def match_level(self, match_level):
        # type: (MatchLevel)  -> T
        self._match_level = match_level
        return self

    def ignore_caret(self, ignore=True):
        # type: (bool)  -> T
        self._ignore_caret = ignore
        return self

    def fully(self, fully=True):
        # type: (bool)  -> T
        self._stitch_content = fully
        return self

    def with_name(self, name):
        # type: (Text)  -> T
        self._name = name
        return self

    def stitch_content(self, stitch_content=True):
        # type: (bool)  -> T
        self._stitch_content = stitch_content
        return self

    def timeout(self, timeout_ms):
        # type: (int)  -> T
        self._timeout = timeout_ms / 1000.0  # secs
        return self

    def update_target_region(self, region):
        # type: (Region)  -> None
        self._target_region = region

    def ignore_regions(self, *regions):
        # type: (*REGION_VALUES)  -> T
        """ Adds one or more ignore regions. """
        self._ignore_regions = self.__regions(regions, method_name="ignore_regions")
        return self

    ignore = ignore_regions

    def layout_regions(self, *regions):
        # type: (*REGION_VALUES)  -> T
        """ Adds one or more layout regions. """
        self._layout_regions = self.__regions(regions, method_name="layout_regions")
        return self

    def strict_regions(self, *regions):
        # type: (*REGION_VALUES)  -> T
        """ Adds one or more strict regions. """
        self._strict_regions = self.__regions(regions, method_name="strict_regions")
        return self

    def content_regions(self, *regions):
        # type: (*REGION_VALUES)  -> T
        """ Adds one or more content regions. """
        self._content_regions = self.__regions(regions, method_name="content_regions")
        return self

    def floating_region(
        self,
        arg1,  # type: Union[REGION_VALUES, int]
        arg2,  # type: Union[REGION_VALUES, int]
        arg3=None,  # type: Optional[int]
        arg4=None,  # type: Optional[int]
        arg5=None,  # type: Optional[int]
    ):
        # type: (...) -> T
        """
        Adds a floating region. Region and max_offset or [max_up_offset, max_down_offset, "
                "max_left_offset, max_right_offset] are required parameters.

        :param arg1: max_offset | Region
        :param arg2: Region     | max_up_offset
        :param arg3: None       | max_down_offset
        :param arg4: None       | max_left_offset
        :param arg5: None       | max_right_offset
        """
        if isinstance(arg1, int):
            max_offset = arg1
            region = arg2
            bounds = FloatingBounds(
                max_up_offset=max_offset,
                max_down_offset=max_offset,
                max_left_offset=max_offset,
                max_right_offset=max_offset,
            )
        else:
            region = arg1
            bounds = FloatingBounds(
                max_up_offset=arg2,
                max_down_offset=arg3,
                max_left_offset=arg4,
                max_right_offset=arg5,
            )
        logger.info("Adding Region {} with FloatingBounds {}".format(region, bounds))
        region_or_container = self._floating_provider_from(region, bounds)
        self._floating_regions.append(region_or_container)
        return self

    floating = floating_region

    def send_dom(self, send=True):
        # type: (bool) -> T
        """
         Defines whether to send the document DOM or not.
        """
        self._send_dom = send
        return self

    def use_dom(self, use=True):
        # type: (bool) -> T
        """
         Defines useDom for enabling the match algorithm to use dom.
        """
        self._use_dom = use
        return self

    def enable_patterns(self, enable=True):
        # type: (bool) -> T
        self._enable_patterns = enable
        return self

    def __regions(self, regions, method_name):
        if not regions:
            raise TypeError(
                "{name} method called without arguments!".format(name=method_name)
            )

        regions_list = getattr(self, "_" + method_name)
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
