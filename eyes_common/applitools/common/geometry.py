from __future__ import absolute_import

import math
import typing
from enum import Enum

import attr

from .utils import argument_guard
from .utils.converters import round_converter
from .utils.json_utils import JsonInclude

if typing.TYPE_CHECKING:
    from PIL.Image import Image
    from typing import List, Dict, Union, Optional
    from .utils.custom_types import ViewPort, Num
    from .visual_grid import EmulationDevice

__all__ = ("Point", "Region", "CoordinatesType", "RectangleSize", "EMPTY_REGION")


class DictAccessMixin(object):
    def __getitem__(self, item):
        if item not in self.__slots__:
            raise KeyError
        return getattr(self, item)


class CoordinatesType(Enum):
    """
     Encapsulates the type of coordinates used by the region provider.
    """

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


@attr.s(slots=True, cmp=False, hash=True)
class RectangleSize(DictAccessMixin):
    width = attr.ib(metadata={JsonInclude.THIS: True})  # type: int
    height = attr.ib(metadata={JsonInclude.THIS: True})  # type:int

    def scale(self, ratio):
        # type: (float) -> RectangleSize
        return RectangleSize(round(self.width * ratio), round(self.height * ratio))

    def __eq__(self, other):
        return self.width == other["width"] and self.height == other["height"]

    @classmethod
    def from_(cls, obj):
        # type: (Union[dict, Image, EmulationDevice, RectangleSize]) -> RectangleSize
        if isinstance(obj, dict):
            return cls(width=obj["width"], height=obj["height"])
        return cls(width=obj.width, height=obj.height)


@attr.s(slots=True)
class Point(DictAccessMixin):
    """
    A point with the coordinates (x,y).
    """

    x = attr.ib(
        converter=round_converter, metadata={JsonInclude.THIS: True}
    )  # type: Num
    y = attr.ib(
        converter=round_converter, metadata={JsonInclude.THIS: True}
    )  # type: Num

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Point(self.x * scalar, self.y * scalar)

    def __div__(self, scalar):
        return Point(self.x / scalar, self.y / scalar)

    @classmethod
    def zero(cls):
        return cls(0, 0)

    @classmethod
    def from_(cls, obj):
        # type: (Union[dict, Point]) -> Point
        return cls(obj["x"], obj["y"])

    def length(self):
        # type: () -> Num
        """
        Returns the distance from (0, 0).
        """
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def distance_to(self, p):
        # type: (Point) -> Num
        """
        Calculate the distance between two points.

        :return: The distance to p.
        """
        return (self - p).length()

    def as_tuple(self):
        # type: () -> tuple
        """
        Return the point as a tuple.

        :return: Point as tuple.
        """
        return self.x, self.y

    def clone(self):
        # type: () -> Point
        """
        Return a full copy of this point.

        :return: Cloned point.
        """
        return Point(self.x, self.y)

    def move_to(self, x, y):
        # type: (Num, Num) -> None
        """
        Moves the point to new x, y.

        :param x: Coordinate x.
        :param y: Coordinate y.
        """
        self.x = x
        self.y = y

    def offset(self, dx, dy):
        # type: (Num, Num) -> Point
        """
        Move to new (x+dx,y+dy).

        :param dx: Offset to move coordinate x.
        :param dy: Offset to move coordinate y.
        """
        self.x = self.x + dx
        self.y = self.y + dy
        return self

    def offset_by_location(self, location):
        # type: (Point) -> Point
        self.offset(location.x, location.y)
        return self

    def offset_negative(self, dx, dy):
        # type: (Num, Num) -> Point
        self.x -= dx
        self.y -= dy
        return self

    def rotate(self, rad):
        # type: (Num) -> Point
        """
        Rotate counter-clockwise around the origin by rad radians.

        Positive y goes *up,* as in traditional mathematics.

        Interestingly, you can use this in y-down computer graphics, if
        you just remember that it turns clockwise, rather than
        counter-clockwise.

        :param rad: The radians to rotate the point.
        :return: The new position is returned as a new Point.
        """
        s, c = [f(rad) for f in (math.sin, math.cos)]
        x, y = (c * self.x - s * self.y, s * self.x + c * self.y)
        return Point(x, y)

    def rotate_about(self, p, theta):
        # type: (Point, Num) -> Point
        """
        Rotate counter-clockwise around a point, by theta degrees.

        Positive y goes *up,* as in traditional mathematics.

        The new position is returned as a new Point.

        :param p: A point to rotate around.
        :param theta: Theta degrees to rotate around.
        :return: The result of the rotation.
        """
        result = self.clone()
        result.offset(-p.x, -p.y)
        result.rotate(theta)
        result.offset(p.x, p.y)
        return result

    def scale(self, scale_ratio):
        # type: (Num) -> Point
        return Point(
            int(math.ceil(self.x * scale_ratio)), int(math.ceil(self.y * scale_ratio))
        )


@attr.s(slots=True)
class Region(DictAccessMixin):
    """
    A rectangle identified by left,top, width, height.
    """

    left = attr.ib(
        converter=round_converter, metadata={JsonInclude.THIS: True}
    )  # type: Num
    top = attr.ib(
        converter=round_converter, metadata={JsonInclude.THIS: True}
    )  # type: Num
    width = attr.ib(
        converter=round_converter, metadata={JsonInclude.THIS: True}
    )  # type: Num
    height = attr.ib(
        converter=round_converter, metadata={JsonInclude.THIS: True}
    )  # type: Num
    coordinates_type = attr.ib(
        default=CoordinatesType.SCREENSHOT_AS_IS, metadata={JsonInclude.THIS: True}
    )  # type: CoordinatesType

    def __str__(self):
        return "Region({left}, {top} {width} x {height} {type})".format(
            left=self.left,
            top=self.top,
            width=self.width,
            height=self.height,
            type=self.coordinates_type.value,
        )

    @classmethod
    def create_empty_region(cls):
        return cls(0, 0, 0, 0)

    @classmethod
    def from_(cls, obj, size=None):
        # type: (Union[Image,Region, dict], Optional[dict]) -> Region
        if size:
            return cls(obj["x"], obj["y"], size["width"], size["height"])
        elif isinstance(obj, Region):
            return cls(obj.left, obj.top, obj.width, obj.height, obj.coordinates_type)
        elif isinstance(obj, Image):
            return cls(0, 0, obj.width, obj.height)
        else:
            raise ValueError("Wrong parameters passed")

    @classmethod
    def from_location_size(cls, location, size):
        # type: (Point, Union[Dict,RectangleSize]) -> Region
        return cls(location["x"], location["y"], size["width"], size["height"])

    @property
    def x(self):
        return self.left

    @property
    def y(self):
        return self.top

    @property
    def right(self):
        # type: () -> Num
        return self.left + self.width

    @property
    def bottom(self):
        # type: () -> Num
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
    def bottom_right(self):
        # type: () -> Point
        """Return the bottom-right corner as a Point."""
        return Point(self.right, self.bottom)

    @property
    def size(self):
        # type: () -> ViewPort
        """
        :return: The size of the region.
        """
        return dict(width=self.width, height=self.height)

    def clone(self):
        # type: () -> Region
        """
        Clone the rectangle.

        :return: The new rectangle object.
        """
        return Region(self.left, self.top, self.width, self.height)

    def is_same(self, other):
        # type: (Region) -> bool
        """
        Checks whether the other rectangle has the same coordinates.

        :param other: The other rectangle to check with.
        :return: Whether or not the rectangles have same coordinates.
        :rtype: bool
        """
        return (
            self.left == other.left
            and self.top == other.top
            and self.width == other.width
            and self.height == other.height
        )

    def is_same_size(self, other):
        # type: (Region) -> bool
        """
        Checks whether the other rectangle is the same size.

        :param other: The other rectangle to check with.
        :return: Whether or not the rectangles are the same size.
        """
        return self.width == other.width and self.height == other.height

    def make_empty(self):
        """
        Sets the current instance as an empty instance
        """
        self.left = self.top = self.width = self.height = 0

    def clip_negative_location(self):
        """
        Sets the left/top values to 0 if the value is negative
        """
        self.left = max(self.left, 0)
        self.top = max(self.top, 0)

    @property
    def is_size_empty(self):
        # type: () -> bool
        """
        :return: true if the region's size is 0, false otherwise.
        """
        return self.width <= 0 or self.height <= 0

    @property
    def is_empty(self):
        # type: () -> bool
        """
        Checks whether the rectangle is empty.

        :return: True if the rectangle is empty. Otherwise False.
        """
        return self.left == self.top == self.width == self.height == 0

    def contains(self, pt):
        # type: (Union[Point, Region]) -> bool
        """
        Return true if a point is inside the rectangle.

        :return: True if the point is inside the rectangle. Otherwise False.
        """
        if isinstance(pt, Point):
            x, y = pt.as_tuple()
            return self.left <= x <= self.right and self.top <= y <= self.bottom  # noqa
        else:
            right = self.left + self.width
            pt_right = pt.left + pt.width

            bottom = self.top + self.height
            pt_bottom = pt.top + pt.height

            return (
                self.top <= pt.top
                and self.left <= pt.left
                and bottom >= pt_bottom
                and right >= pt_right
            )

    def overlaps(self, other):
        # type: (Region) -> bool
        """
        Return true if a rectangle overlaps this rectangle.
        """
        return (
            self.left <= other.left <= self.right
            or other.left <= self.left <= other.right
        ) and (
            self.top <= other.top <= self.bottom
            or other.top <= self.top <= other.bottom
        )

    def intersect(self, other):
        # type: (Region) -> None
        # If the regions don't overlap, the intersection is empty
        if not self.overlaps(other):
            self.make_empty()
            return
        intersection_left = self.left if self.left >= other.left else other.left
        intersection_top = self.top if self.top >= other.top else other.top
        intersection_right = self.right if self.right <= other.right else other.right
        intersection_bottom = (
            self.bottom if self.bottom <= other.bottom else other.bottom
        )
        self.left, self.top = intersection_left, intersection_top
        self.width = intersection_right - intersection_left
        self.height = intersection_bottom - intersection_top

    def get_sub_regions(self, max_sub_region_size):
        # type: (RectangleSize) -> List[Region]
        """
        Returns a list of Region objects which compose the current region.
        """
        sub_regions = []
        current_top = self.top
        while current_top < self.height:

            current_bottom = current_top + max_sub_region_size["height"]
            if current_bottom > self.height:
                current_bottom = self.height

            current_left = self.left
            while current_left < self.width:
                current_right = current_left + max_sub_region_size["width"]
                if current_right > self.width:
                    current_right = self.width

                current_height = current_bottom - current_top
                current_width = current_right - current_left

                sub_regions.append(
                    Region(current_left, current_top, current_width, current_height)
                )

                current_left += max_sub_region_size["width"]

            current_top += max_sub_region_size["height"]

        return sub_regions

    @property
    def middle_offset(self):
        # type: () -> Point
        return Point(int(round(self.width / 2)), int(round(self.height / 2)))

    def offset(self, dx, dy):
        # type: (Num, Num) -> Region
        location = self.location.offset(dx, dy)
        return Region(
            left=location.x,
            top=location.y,
            width=self.size["width"],
            height=self.size["height"],
        )

    def scale(self, scale_ratio):
        # type: (Num) -> Region
        return Region(
            left=int(math.ceil(self.left * scale_ratio)),
            top=int(math.ceil(self.top * scale_ratio)),
            width=int(math.ceil(self.width * scale_ratio)),
            height=int(math.ceil(self.height * scale_ratio)),
        )


EMPTY_REGION = Region(0, 0, 0, 0)
