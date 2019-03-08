import typing
from abc import ABC

import attr

from applitools.common import logger
from applitools.common.geometry import Region
from applitools.common.match import FloatingMatchSettings, MatchLevel

from .region import (
    FloatingRegionByRectangle,
    GetFloatingRegion,
    GetRegion,
    IgnoreRegionByRectangle,
)

if typing.TYPE_CHECKING:
    from typing import Text, Optional, List, Union

    T = typing.TypeVar("T", bound="CheckSettings")
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
    _timeout = attr.ib(init=False, default=-1)  # type: int

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
        self._timeout = timeout_ms
        return self

    def update_target_region(self, region):
        # type: (Region)  -> None
        self._target_region = region

    def ignore_regions(self, *regions):
        # type: (*Region)  -> T
        """ Adds one or more ignore regions. """
        return self.__regions(regions, method_name="ignore_regions")

    ignore = ignore_regions

    def layout_regions(self, *regions):
        # type: (*Region)  -> T
        """ Adds one or more layout regions. """
        return self.__regions(regions, method_name="layout_regions")

    def strict_regions(self, *regions):
        # type: (*Region)  -> T
        """ Adds one or more strict regions. """
        return self.__regions(regions, method_name="strict_regions")

    def content_regions(self, *regions):
        # type: (*Region)  -> T
        """ Adds one or more content regions. """
        return self.__regions(regions, method_name="content_regions")

    def floating_regions(self, *args):
        # type: (*Region)  -> T
        """ Adds a floating region. Details in :py:func:`_floating_to_region` """
        region_or_container = self._floating_to_region(*args)
        self._floating_regions.append(region_or_container)
        return self

    floating = floating_regions

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
        # type: (Region, Text)  -> T
        if not regions:
            raise TypeError(
                "{name} method called without arguments!".format(name=method_name)
            )

        regions_list = getattr(self, "_" + method_name)
        for region in regions:
            regions_list.append(self._region_to_region_provider(region, method_name))
        return self

    @staticmethod
    def _region_to_region_provider(region, method_name):
        # type: (Union[GetRegion, Region], Text) -> GetRegion
        logger.debug("calling _{}".format(method_name))
        if isinstance(region, Region):
            return IgnoreRegionByRectangle(region)

        if isinstance(region, GetRegion):
            return region

    @staticmethod
    def _floating_to_region(*args):
        region_or_container = args[0]
        if isinstance(region_or_container, GetFloatingRegion):
            logger.debug("_floating: GetFloatingRegion")
            return region_or_container
        elif len(args) > 1 and isinstance(
            region_or_container, FloatingRegionByRectangle
        ):
            max_up_offset = args[1]
            max_down_offset = args[2]
            max_left_offset = args[3]
            max_right_offset = args[4]
            logger.debug("_floating: FloatingRegionByRectangle")
            return FloatingRegionByRectangle(
                Region.from_region(region_or_container),
                max_up_offset,
                max_down_offset,
                max_left_offset,
                max_right_offset,
            )
        elif isinstance(region_or_container, FloatingMatchSettings):
            logger.debug("_floating: FloatingMatchSettings")
            return FloatingRegionByRectangle(
                region_or_container.get_region(),
                region_or_container.max_up_offset,
                region_or_container.max_down_offset,
                region_or_container.max_left_offset,
                region_or_container.max_right_offset,
            )
