from __future__ import absolute_import

import math
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional, Text, Tuple, Union, overload

import attr
from PIL.Image import Image

from . import logger
from .accessibility import AccessibilityRegionType
from .mixins import DictAccessMixin
from .utils import argument_guard
from .utils.compat import basestring
from .utils.converters import round_converter
from .utils.json_utils import JsonInclude

if TYPE_CHECKING:
    from .ultrafastgrid.render_browser_info import IRenderBrowserinfo
    from .utils.custom_types import CodedRegionPadding

__all__ = (
    "Point",
    "Region",
    "CoordinatesType",
    "RectangleSize",
    "SubregionForStitching",
    "AccessibilityRegion",
)


def dx_and_dy(location_or_dx, dy):
    # type: (Union[Point, int], Optional[int]) -> Tuple[int,int]
    dx = location_or_dx
    if dy is None:
        dx, dy = location_or_dx
    return dx, dy


class CoordinatesType(Enum):
    """Encapsulates the type of coordinates used by the region provider."""

    # The coordinates should be used "as is" on the screenshot image.
    # Regardless of the current context.
    SCREENSHOT_AS_IS = "SCREENSHOT_AS_IS"

    # The coordinates should be used "as is" within the current context. For
    # example, if we're inside a frame, the coordinates are "as is",
    # but within the current frame's viewport.
    CONTEXT_AS_IS = "CONTEXT_AS_IS"

    # Coordinates are relative to the context. For example, if we are in
    # a context of a frame in a web page, then the coordinates are relative to
    # the  frame. In this case, if we want to crop an image region based on
    # an element's region, we will need to calculate their respective "as
    # is" coordinates.
    CONTEXT_RELATIVE = "CONTEXT_RELATIVE"


@attr.s(slots=True, eq=False, hash=True, init=False)
class RectangleSize(DictAccessMixin):
    """Represents a 2D size"""

    width = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    height = attr.ib(metadata={JsonInclude.THIS: True})  # type:int

    def __init__(self, width, height):
        # type: (int, int) -> None
        self.width = round_converter(width)
        self.height = round_converter(height)

    def __str__(self):
        return "RectangleSize({width} x {height})".format(
            width=self.width, height=self.height
        )

    def __eq__(self, other):
        # type: (Union[RectangleSize, Dict]) -> bool
        return self.width == other["width"] and self.height == other["height"]

    def __ne__(self, other):
        # type: (Union[RectangleSize, Dict]) -> bool
        return self.width != other["width"] or self.height != other["height"]

    def __add__(self, other):
        # type: (Union[RectangleSize, Dict]) -> RectangleSize
        return RectangleSize(self.width + other["width"], self.height + other["height"])

    def __radd__(self, other):
        # type: (Union[RectangleSize, Dict]) -> RectangleSize
        return RectangleSize(self.width + other["width"], self.height + other["height"])

    def __sub__(self, other):
        # type: (Union[RectangleSize, Dict]) -> RectangleSize
        return RectangleSize(self.width - other["width"], self.height - other["height"])

    def __rsub__(self, other):
        # type: (Union[RectangleSize, Dict]) -> RectangleSize
        return RectangleSize(other["width"] - self.width, other["height"] - self.height)

    def scale(self, scale_ratio):
        # type: (float) -> RectangleSize
        """Get a scaled version of the current size.

        Args:
            scale_ratio: The ratio by which to scale.

        Returns:
            A scaled version of the current size.
        """
        return RectangleSize(
            round(self.width * scale_ratio), round(self.height * scale_ratio)
        )

    @classmethod
    def from_(cls, obj):
        # type: (Union[dict,Image,IRenderBrowserinfo,RectangleSize])->RectangleSize
        """Creates a new RectangleSize instance."""
        if isinstance(obj, dict):
            return cls(width=obj["width"], height=obj["height"])
        return cls(width=obj.width, height=obj.height)


@attr.s(slots=True, eq=False, init=False)
class Point(DictAccessMixin):
    """A location in a two-dimensional plane."""

    x = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    y = attr.ib(metadata={JsonInclude.THIS: True})  # type: int

    def __init__(self, x, y):
        # type: (int, int) -> None
        self.x = round_converter(x)
        self.y = round_converter(y)

    def __str__(self):
        return "Point({x} x {y})".format(x=self.x, y=self.y)

    def __add__(self, other):
        # type: (Union[Point, int, float]) -> Point
        if isinstance(other, int) or isinstance(other, float):
            return Point(self.x + round(other), self.y + round(other))
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        # type: (Union[Point, int, float]) -> Point
        if isinstance(other, int) or isinstance(other, float):
            return Point(self.x - round(other), self.y - round(other))
        return Point(self.x - other.x, self.y - other.y)

    def __neg__(self):
        # type: () -> Point
        return Point(-self.x, -self.y)

    def __mul__(self, scalar):
        # type: (int) -> Point
        return Point(self.x * scalar, self.y * scalar)

    def __div__(self, scalar):
        # type: (int) -> Point
        return Point(round_converter(self.x / scalar), round_converter(self.y / scalar))

    def __eq__(self, other):
        # type: (Union[RectangleSize, Dict]) -> bool
        return self.x == other["x"] and self.y == other["y"]

    @classmethod  # noqa
    def ZERO(cls):
        # type: () -> Point
        return cls(0, 0)

    @classmethod
    def from_(cls, obj):
        # type: (Union[dict, Point]) -> Point
        """Creates a new Point instance."""
        return cls(obj["x"], obj["y"])

    def clone(self):
        # type: () -> Point
        """Make a full copy of this Point.

        Returns:
            New cloned Point instance
        """
        return Point(self.x, self.y)

    @overload  # noqa
    def offset(self, location):
        # type: (Point) -> Point
        pass

    @overload  # noqa
    def offset(self, dx, dy):
        # type: (int, int) -> Point
        pass

    def offset(self, location_or_dx, dy=None):  # noqa
        # type: (Union[Point, int], Optional[int]) -> Point
        """Get a location translated by the specified amount.

        Args:
            location_or_dx: Full amount to offset or just x-coordinate
            dy: The amount to offset the y-coordinate.

        Returns:
            A location translated by the specified amount.
        """
        dx, dy = dx_and_dy(location_or_dx, dy)
        return Point(self.x + dx, self.y + dy)

    def scale(self, scale_ratio):
        # type: (float) -> Point
        """Get a scaled location.

        Args:
            scale_ratio: The ratio by which to scale the results.

        Returns:
            A scaled copy of the current location.
        """
        return Point(
            int(math.ceil(self.x * scale_ratio)), int(math.ceil(self.y * scale_ratio))
        )


@attr.s(slots=True, init=False)
class Rectangle(DictAccessMixin):
    left = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    top = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    width = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    height = attr.ib(metadata={JsonInclude.THIS: True})  # type: int

    def __init__(
        self,
        left,  # type: int
        top,  # type: int
        width,  # type: int
        height,  # type: int
    ):
        # type: (...) -> None
        self.left = round_converter(left)
        self.top = round_converter(top)
        self.width = round_converter(width)
        self.height = round_converter(height)

    @classmethod  # noqa
    def EMPTY(cls):
        return cls(0, 0, 0, 0)

    @property
    def x(self):
        # type: () -> int
        return self.left

    @property
    def y(self):
        # type: () -> int
        return self.top

    @property
    def right(self):
        # type: () -> int
        return self.left + self.width

    @property
    def bottom(self):
        # type: () -> int
        return self.top + self.height

    @property
    def location(self):
        # type: () -> Point
        """Return the top-left corner as a Point."""
        return Point(self.left, self.top)

    @location.setter
    def location(self, point):
        # type: (Point) -> None
        """Sets the top left corner of the region"""
        argument_guard.not_none(point)
        self.left, self.top = point.x, point.y

    @property
    def area(self):
        return self.width * self.height

    @property
    def bottom_right(self):
        # type: () -> Point
        """
        Returns:
            The bottom-right corner as a Point.
        """
        return Point(self.right, self.bottom)

    @property
    def size(self):
        # type: () -> RectangleSize
        """
        Returns:
            The size of the region.
        """
        return RectangleSize(width=self.width, height=self.height)

    def make_empty(self):
        """Sets the current instance as an empty instance"""
        self.left = self.top = self.width = self.height = 0

    def clip_negative_location(self):
        """Sets the left/top values to 0 if the value is negative"""
        self.left = max(self.left, 0)
        self.top = max(self.top, 0)

    @property
    def is_size_empty(self):
        # type: () -> bool
        """
        Returns:
            true if the region's size is 0, false otherwise.
        """
        return self.width <= 0 or self.height <= 0

    @property
    def is_empty(self):
        # type: () -> bool
        """Checks whether the rectangle is empty.

        Returns:
            True if the rectangle is empty. Otherwise False.
        """
        return self.left == self.top == self.width == self.height == 0

    @property
    def middle_offset(self):
        # type: () -> Point
        return Point(int(round(self.width / 2)), int(round(self.height / 2)))

    @overload  # noqa
    def offset(self, location):
        # type: (Point) -> Region
        pass

    @overload  # noqa
    def offset(self, dx, dy):
        # type: (int, int) -> Region
        pass

    def offset(self, location_or_dx, dy=None):  # noqa
        # type: (Union[Point, int], Optional[int]) -> Rectangle
        """Get an offset region.

        Args:
            location_or_dx: Full amount to offset or just x-coordinate
            dy: The amount to offset the y-coordinate.

        Returns:
            A region with an offset location.
        """
        dx, dy = dx_and_dy(location_or_dx, dy)
        location = self.location.offset(dx, dy)
        return Rectangle(
            left=location.x,
            top=location.y,
            width=self.size["width"],
            height=self.size["height"],
        )


@attr.s(slots=True, init=False)
class AccessibilityRegion(Rectangle):
    """A rectangle identified by left,top, width, height."""

    left = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    top = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    width = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    height = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    type = attr.ib(
        type=AccessibilityRegionType, metadata={JsonInclude.THIS: True}
    )  # type: AccessibilityRegionType

    def __init__(
        self,
        left,  # type: int
        top,  # type: int
        width,  # type: int
        height,  # type: int
        type,  # type: AccessibilityRegionType
    ):
        # type: (...) -> None
        super(AccessibilityRegion, self).__init__(left, top, width, height)
        if isinstance(type, basestring):
            if type == "None":
                self.type = None
                return
        self.type = AccessibilityRegionType(type)

    @overload  # noqa
    def from_(self, accessibility_region):
        # type: (Union[Dict, AccessibilityRegion]) -> AccessibilityRegion
        pass

    @overload  # noqa
    def from_(self, region, accessibility_type):
        # type: (Union[Region,Rectangle],AccessibilityRegionType)->AccessibilityRegion
        pass

    @classmethod  # noqa
    def from_(cls, obj, obj2=None):
        # type: (...)->AccessibilityRegion
        """Creates a new Region instance."""
        if isinstance(obj, AccessibilityRegion):
            return cls(obj.left, obj.top, obj.width, obj.height, obj.type)
        elif (
            isinstance(obj, Region)
            or isinstance(obj, Rectangle)
            and isinstance(obj2, AccessibilityRegionType)
        ):
            return cls(obj.left, obj.top, obj.width, obj.height, obj2)
        elif isinstance(obj, dict):
            return cls(
                obj["left"],
                obj["top"],
                obj["width"],
                obj["height"],
                AccessibilityRegionType(obj["type"]),
            )
        raise ValueError("Wrong parameters passed")

    def offset(self, location_or_dx, dy=None):  # noqa
        # type: (Union[Point, int], Optional[int]) -> AccessibilityRegion
        r = super(AccessibilityRegion, self).offset(location_or_dx, dy)
        return AccessibilityRegion.from_(r, self.type)


@attr.s(slots=True, init=False)
class Region(Rectangle):
    """A rectangle identified by left,top, width, height."""

    left = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    top = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    width = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    height = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    coordinates_type = attr.ib(
        converter=CoordinatesType,
        type=CoordinatesType,
        metadata={JsonInclude.THIS: True},
    )  # type: CoordinatesType

    def __init__(
        self,
        left,  # type: int
        top,  # type: int
        width,  # type: int
        height,  # type: int
        coordinates_type=CoordinatesType.SCREENSHOT_AS_IS,  # type: CoordinatesType
    ):
        # type: (...) -> None
        super(Region, self).__init__(left, top, width, height)
        self.coordinates_type = CoordinatesType(coordinates_type)

    def __str__(self):
        return "Region({left}, {top}, {width} x {height}, {type})".format(
            left=self.left,
            top=self.top,
            width=self.width,
            height=self.height,
            type=self.coordinates_type.value,
        )

    def padding(self, other):
        # type: (CodedRegionPadding) -> Region
        if isinstance(other, dict):
            return Region(
                left=self.left + other.get("left", 0),
                top=self.top + other.get("top", 0),
                width=self.width + other.get("right", 0),
                height=self.height + other.get("bottom", 0),
                coordinates_type=self.coordinates_type,
            )
        else:
            raise TypeError("Unsupported flow")

    @classmethod  # noqa
    @overload
    def from_(cls, location, image):
        # type: (Union[Point, Dict], Image) -> Region
        pass

    @classmethod  # noqa
    @overload
    def from_(cls, location, size):
        # type: (Union[Point, Dict], Union[Dict,RectangleSize]) -> Region
        pass

    @classmethod  # noqa
    @overload
    def from_(cls, image):
        # type: (Image) -> Region
        pass

    @classmethod  # noqa
    @overload
    def from_(cls, region):
        # type: (Union[Region, Dict]) -> Region
        pass

    @classmethod  # noqa
    @overload
    def from_(cls, rectangle, coordinates_type):
        # type: (Rectangle, Optional[CoordinatesType]) -> Region
        pass

    @classmethod  # noqa
    def from_(cls, obj, obj2=None):
        # type:( ... )->Region
        """Creates a new Region instance."""
        if isinstance(obj, Rectangle):
            if isinstance(obj2, CoordinatesType):
                return cls(obj.left, obj.top, obj.width, obj.height, obj2)
            return cls(obj.left, obj.top, obj.width, obj.height)
        if isinstance(obj, Region):
            return cls(obj.left, obj.top, obj.width, obj.height, obj.coordinates_type)
        elif isinstance(obj, Image):
            return cls(0, 0, obj.width, obj.height)
        elif isinstance(obj, Point) or isinstance(obj, dict) and obj2:
            if isinstance(obj2, Image):
                return cls(obj["x"], obj["y"], obj2.width, obj2.height)
            else:
                return cls(obj["x"], obj["y"], obj2["width"], obj2["height"])
        elif isinstance(obj, dict) and obj2 is None:
            return cls(
                obj[
                    "left",
                    obj["right"],
                    obj["height"],
                    obj["width"],
                    CoordinatesType(obj["type"]),
                ]
            )
        raise ValueError("Wrong parameters passed")

    def clone(self):
        # type: () -> Region
        """
        Returns:
            The cloned instance of Region.
        """
        return Region(
            self.left, self.top, self.width, self.height, self.coordinates_type
        )

    def contains(self, other):
        # type: (Union[Point, Region]) -> bool
        """Return true if a point is inside the rectangle.

        Args:
            other: element for check

        Returns:
            True if the point is inside the rectangle. Otherwise False.
        """
        if isinstance(other, Point):
            x, y = other
            return self.left <= x <= self.right and self.top <= y <= self.bottom  # noqa
        else:
            right = self.left + self.width
            pt_right = other.left + other.width

            bottom = self.top + self.height
            pt_bottom = other.top + other.height

            return (
                self.top <= other.top
                and self.left <= other.left
                and bottom >= pt_bottom
                and right >= pt_right
            )

    def overlaps(self, other):
        # type: (Region) -> bool
        """Return true if a rectangle overlaps this rectangle.

        Args:
            other:
        """
        return (
            self.left <= other.left <= self.right
            or other.left <= self.left <= other.right
        ) and (
            self.top <= other.top <= self.bottom
            or other.top <= self.top <= other.bottom
        )

    def is_intersected(self, other):
        return self.overlaps(other)

    def intersect(self, other):
        # type: (Region) -> Region
        # If the regions don't overlap, the intersection is empty
        """
        Args:
            other:
        """
        if not self.overlaps(other):
            return Region.EMPTY()
        intersection_left = self.left if self.left >= other.left else other.left
        intersection_top = self.top if self.top >= other.top else other.top
        intersection_right = self.right if self.right <= other.right else other.right
        intersection_bottom = (
            self.bottom if self.bottom <= other.bottom else other.bottom
        )
        left, top = intersection_left, intersection_top
        width = intersection_right - intersection_left
        height = intersection_bottom - intersection_top
        return Region(left, top, width, height, self.coordinates_type)

    def get_sub_regions(  # noqa
        self,
        max_sub_region_size,  # type: RectangleSize
        logical_overlap,  # type: int
        l2p_scale_ratio,  # type: float
        physical_rect_in_screenshot,  # type: Region
    ):
        # type: (...) -> List[SubregionForStitching]
        sub_regions = []

        double_logical_overlap = logical_overlap * 2
        physical_overlap = round(double_logical_overlap * l2p_scale_ratio)

        need_v_scroll = self.height > physical_rect_in_screenshot.height
        need_h_scroll = self.width > physical_rect_in_screenshot.width

        scroll_y = current_top = 0
        current_logical_height = max_sub_region_size.height

        delta_y = current_logical_height - double_logical_overlap

        is_top_edge = True
        is_bottom_edge = False

        scale_ratio_offset = round(l2p_scale_ratio - 1)

        while not is_bottom_edge:
            current_scroll_top = scroll_y + max_sub_region_size.height
            if current_scroll_top >= self.height:
                if not is_top_edge:
                    scroll_y = self.height - current_logical_height
                    current_logical_height = self.height - current_top
                    current_top = (
                        self.height
                        - current_logical_height
                        - double_logical_overlap
                        - logical_overlap
                        + scale_ratio_offset
                    )
                else:
                    current_logical_height = self.height - current_top
                is_bottom_edge = True

            scroll_x = current_left = 0
            current_logical_width = max_sub_region_size.width

            delta_x = current_logical_width - double_logical_overlap

            is_left_edge = True
            is_right_edge = False

            while not is_right_edge:
                current_scroll_right = scroll_x + max_sub_region_size.width
                if current_scroll_right >= self.width:
                    if not is_left_edge:
                        scroll_x = self.width - current_logical_width
                        current_logical_width = self.width - current_left
                        current_left = (
                            self.width
                            - current_logical_width
                            - double_logical_overlap
                            - logical_overlap
                            + scale_ratio_offset
                        )
                    else:
                        current_logical_width = self.width - current_left
                    is_right_edge = True

                physical_crop_area = Region.from_(physical_rect_in_screenshot)
                logical_crop_area = Region(
                    0, 0, current_logical_width, current_logical_height
                )
                paste_point = Point(current_left, current_top)

                # handle horizontal
                if is_right_edge:
                    physical_width = round(current_logical_width * l2p_scale_ratio)
                    physical_crop_area.left = (
                        physical_rect_in_screenshot.right - physical_width
                    )
                    physical_crop_area.width = physical_width

                if not is_left_edge:
                    logical_crop_area.left += logical_overlap
                    logical_crop_area.width -= logical_overlap

                if is_right_edge and not is_left_edge:
                    physical_crop_area.left -= physical_overlap * 2
                    physical_crop_area.width += physical_overlap * 2
                    logical_crop_area.width += double_logical_overlap * 2

                # handle vertical
                if is_bottom_edge:
                    physical_height = round(current_logical_height * l2p_scale_ratio)
                    physical_crop_area.top = (
                        physical_rect_in_screenshot.bottom - physical_height
                    )
                    physical_crop_area.height = physical_height
                if not is_top_edge:
                    logical_crop_area.top += logical_overlap
                    logical_crop_area.height -= logical_overlap
                if is_bottom_edge and not is_top_edge:
                    physical_crop_area.top -= physical_overlap * 2
                    physical_crop_area.height += physical_overlap * 2
                    logical_crop_area.height += double_logical_overlap * 2

                subregion = SubregionForStitching(
                    Point(scroll_x, scroll_y),
                    Point.from_(paste_point),
                    Region.from_(physical_crop_area),
                    Region.from_(logical_crop_area),
                )
                logger.debug("adding subregion - {}".format(subregion))
                sub_regions.append(subregion)

                current_left += delta_x
                scroll_x += delta_x

                if need_h_scroll and is_left_edge:
                    current_left += logical_overlap + scale_ratio_offset
                is_left_edge = False

            current_top += delta_y
            scroll_y += delta_y

            if need_v_scroll and is_top_edge:
                current_top += logical_overlap + scale_ratio_offset
            is_top_edge = False

        return sub_regions

    def offset(self, location_or_dx, dy=None):  # noqa
        # type: (Union[Point, int], Optional[int]) -> Region
        r = super(Region, self).offset(location_or_dx, dy)
        return Region.from_(r, self.coordinates_type)

    def scale(self, scale_ratio):
        # type: (float) -> Region
        """Get a region which is a scaled version of the current region.
        IMPORTANT: This also scales the LOCATION(!!) of the region (not just its
        size).

        Args:
            scale_ratio: The ratio by which to scale the region.

        Returns:
            A new region which is a scaled version of the current region.
        """
        return Region(
            left=int(math.ceil(self.left * scale_ratio)),
            top=int(math.ceil(self.top * scale_ratio)),
            width=int(math.ceil(self.width * scale_ratio)),
            height=int(math.ceil(self.height * scale_ratio)),
            coordinates_type=self.coordinates_type,
        )


@attr.s
class SubregionForStitching(object):
    scroll_to = attr.ib()  # type: Point
    paste_physical_location = attr.ib()  # type: Point
    physical_crop_area = attr.ib()  # type: Region
    logical_crop_area = attr.ib()  # type: Region
