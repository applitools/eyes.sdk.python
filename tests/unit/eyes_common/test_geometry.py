from itertools import chain

import pytest

from applitools.common import CoordinatesType, Point, RectangleSize, Region
from applitools.common.geometry import (
    Rectangle,
    SubregionForStitching,
    rectangle_overlapping_tiles,
    rectangle_tiles,
)


def flatten(*lists):
    return list(chain(*lists))


@pytest.mark.parametrize(
    "left,top,width,height,coord_type,result",
    [
        [
            0,
            0,
            0,
            0,
            CoordinatesType.CONTEXT_AS_IS,
            Region(0, 0, 0, 0, CoordinatesType.CONTEXT_AS_IS),
        ],
        [
            1,
            2.6,
            3.5,
            4.1,
            CoordinatesType.SCREENSHOT_AS_IS,
            Region(1, 3, 4, 4, CoordinatesType.SCREENSHOT_AS_IS),
        ],
    ],
)
def test_region_creation(left, top, width, height, coord_type, result):
    expect = Region(left, top, width, height, coord_type)
    assert expect == result


@pytest.mark.parametrize("x,y,result", [[0, 0, Point(0, 0)], [1.6, 2.2, Point(2, 2)]])
def test_point_creation(x, y, result):
    expect = Point(x, y)
    assert expect == result


@pytest.mark.parametrize(
    "width,height,result",
    [[0, 0, RectangleSize(0, 0)], [1.6, 2.2, RectangleSize(2, 2)]],
)
def test_rectangle_size_creation(width, height, result):
    expect = RectangleSize(width, height)
    assert expect == result


def test_rectangle_size_equality():
    a = RectangleSize(800, 600)
    b = RectangleSize(800, 600)
    c = RectangleSize(200, 200)

    assert a == b
    assert not a == c


def test_rectangle_size_inequality():
    a = RectangleSize(800, 600)
    b = RectangleSize(800, 600)
    c = RectangleSize(200, 200)

    assert a != c
    assert not a != b


def test_access_by_keys_to_inherited_obj():
    r = Region(0, 1, 2, 3)
    assert r.left == r["left"]
    assert r.top == r["top"]
    assert r.width == r["width"]
    assert r.height == r["height"]
    assert r.coordinates_type == r["coordinates_type"]


def test_access_by_int_to_inherited_obj():
    r = Region(0, 1, 2, 3)
    assert r.left == r[0]
    assert r.top == r[1]
    assert r.width == r[2]
    assert r.height == r[3]
    assert r.coordinates_type == r[4]


def test_not_accessible_attr():
    r = Region(0, 1, 2, 3)
    with pytest.raises(KeyError):
        r["someattr"]
    with pytest.raises(IndexError):
        r[6]


def test_sub_regions():
    r = Region(0, 0, 100, 200)

    subregions = r.get_sub_regions(
        RectangleSize(100, 100), 5, 2, Region(0, 0, 200, 200)
    )

    assert subregions == [
        SubregionForStitching(
            scroll_to=Point(x=0, y=0),
            paste_physical_location=Point(x=0, y=0),
            physical_crop_area=Region(left=0, top=0, width=200, height=40),
            logical_crop_area=Region(left=0, top=0, width=100, height=20),
        ),
        SubregionForStitching(
            scroll_to=Point(x=0, y=10),
            paste_physical_location=Point(x=0, y=15),
            physical_crop_area=Region(left=0, top=0, width=200, height=200),
            logical_crop_area=Region(left=0, top=5, width=100, height=95),
        ),
        SubregionForStitching(
            scroll_to=Point(x=0, y=100),
            paste_physical_location=Point(x=0, y=105),
            physical_crop_area=Region(left=0, top=0, width=200, height=200),
            logical_crop_area=Region(left=0, top=5, width=100, height=95),
        ),
    ]


def test_sub_regions_offsetted_location():
    r = Region(0, 0, 100, 200)

    subregions = r.get_sub_regions(
        RectangleSize(100, 100), 5, 2, Region(31, 32, 200, 200)
    )

    assert subregions == [
        SubregionForStitching(
            scroll_to=Point(x=0, y=0),
            paste_physical_location=Point(x=0, y=0),
            physical_crop_area=Region(left=31, top=32, width=200, height=40),
            logical_crop_area=Region(left=0, top=0, width=100, height=20),
        ),
        SubregionForStitching(
            scroll_to=Point(x=0, y=10),
            paste_physical_location=Point(x=0, y=15),
            physical_crop_area=Region(left=31, top=32, width=200, height=200),
            logical_crop_area=Region(left=0, top=5, width=100, height=95),
        ),
        SubregionForStitching(
            scroll_to=Point(x=0, y=100),
            paste_physical_location=Point(x=0, y=105),
            physical_crop_area=Region(left=31, top=32, width=200, height=200),
            logical_crop_area=Region(left=0, top=5, width=100, height=95),
        ),
    ]


def test_sub_regions_even_division_minus_double_overlap():
    r = Region(0, 0, 100, 200 - 10)

    subregions = r.get_sub_regions(
        RectangleSize(100, 100), 5, 2, Region(0, 0, 200, 200)
    )

    assert subregions == [
        SubregionForStitching(
            scroll_to=Point(x=0, y=0),
            paste_physical_location=Point(x=0, y=0),
            physical_crop_area=Region(left=0, top=0, width=200, height=200),
            logical_crop_area=Region(left=0, top=0, width=100, height=100),
        ),
        SubregionForStitching(
            scroll_to=Point(x=0, y=90),
            paste_physical_location=Point(x=0, y=95),
            physical_crop_area=Region(left=0, top=0, width=200, height=200),
            logical_crop_area=Region(left=0, top=5, width=100, height=95),
        ),
    ]


def test_break_rectangle_10x10():
    subrects = rectangle_tiles(Rectangle(0, 0, 10, 10), RectangleSize(10, 10))

    assert subrects == [Rectangle(0, 0, 10, 10)]


def test_break_rectangle_5x5():
    subrects = rectangle_tiles(Rectangle(0, 0, 5, 5), RectangleSize(10, 10))

    assert subrects == [Rectangle(0, 0, 5, 5)]


def test_break_rectangle_10x20():
    subrects = rectangle_tiles(Rectangle(0, 0, 10, 20), RectangleSize(10, 10))

    assert subrects == [
        Rectangle(0, 0, 10, 10),
        Rectangle(0, 10, 10, 10),
    ]


def test_break_rectangle_20x10():
    subrects = rectangle_tiles(Rectangle(0, 0, 20, 10), RectangleSize(10, 10))

    assert subrects == [Rectangle(0, 0, 10, 10), Rectangle(10, 0, 10, 10)]


def test_break_rectangle_20x20():
    subrects = rectangle_tiles(Rectangle(0, 0, 20, 20), RectangleSize(10, 10))

    assert subrects == flatten(
        [Rectangle(0, 0, 10, 10), Rectangle(10, 0, 10, 10)],
        [Rectangle(0, 10, 10, 10), Rectangle(10, 10, 10, 10)],
    )


def test_break_rectangle_10x11():
    subrects = rectangle_tiles(Rectangle(0, 0, 10, 11), RectangleSize(10, 10))

    assert subrects == [
        Rectangle(0, 0, 10, 1),
        Rectangle(0, 1, 10, 10),
    ]


def test_break_rectangle_11x10():
    subrects = rectangle_tiles(Rectangle(0, 0, 11, 10), RectangleSize(10, 10))

    assert subrects == [Rectangle(0, 0, 1, 10), Rectangle(1, 0, 10, 10)]


def test_break_rectangle_10x21():
    subrects = rectangle_tiles(Rectangle(0, 0, 10, 21), RectangleSize(10, 10))

    assert subrects == [
        Rectangle(0, 0, 10, 1),
        Rectangle(0, 1, 10, 10),
        Rectangle(0, 11, 10, 10),
    ]


def test_break_rectangle_21x10():
    subrects = rectangle_tiles(Rectangle(0, 0, 21, 10), RectangleSize(10, 10))

    assert subrects == list(
        [Rectangle(0, 0, 1, 10), Rectangle(1, 0, 10, 10), Rectangle(11, 0, 10, 10)]
    )


def test_break_rectangle_11x11():
    subrects = rectangle_tiles(Rectangle(0, 0, 11, 11), RectangleSize(10, 10))

    assert subrects == flatten(
        [Rectangle(0, 0, 1, 1), Rectangle(1, 0, 10, 1)],
        [Rectangle(0, 1, 1, 10), Rectangle(1, 1, 10, 10)],
    )


def test_break_rectangle_21x21():
    subrects = rectangle_tiles(Rectangle(0, 0, 21, 21), RectangleSize(10, 10))

    assert subrects == flatten(
        [Rectangle(0, 0, 1, 1), Rectangle(1, 0, 10, 1), Rectangle(11, 0, 10, 1)],
        [Rectangle(0, 1, 1, 10), Rectangle(1, 1, 10, 10), Rectangle(11, 1, 10, 10)],
        [Rectangle(0, 11, 1, 10), Rectangle(1, 11, 10, 10), Rectangle(11, 11, 10, 10)],
    )


def test_break_offsetted_rectangle_10x10():
    subrects = rectangle_tiles(Rectangle(5, 5, 10, 10), RectangleSize(10, 10))

    assert subrects == [Rectangle(5, 5, 10, 10)]


def test_break_offsetted_rectangle_5x5():
    subrects = rectangle_tiles(Rectangle(5, 5, 5, 5), RectangleSize(10, 10))

    assert subrects == [Rectangle(5, 5, 5, 5)]


def test_break_offsetted_rectangle_21x21():
    subrects = rectangle_tiles(Rectangle(5, 5, 21, 21), RectangleSize(10, 10))

    assert subrects == flatten(
        [Rectangle(5, 5, 1, 1), Rectangle(6, 5, 10, 1), Rectangle(16, 5, 10, 1)],
        [Rectangle(5, 6, 1, 10), Rectangle(6, 6, 10, 10), Rectangle(16, 6, 10, 10)],
        [Rectangle(5, 16, 1, 10), Rectangle(6, 16, 10, 10), Rectangle(16, 16, 10, 10)],
    )


def test_rectangle_overlapping_overcropped_tiles_5x5():
    tiles = rectangle_overlapping_tiles(Rectangle(0, 0, 5, 5), RectangleSize(10, 10), 2)

    assert tiles == [Rectangle(0, 0, 5, 5)]


def test_rectangle_overlapping_overcropped_tiles_10x10():
    tiles = rectangle_overlapping_tiles(
        Rectangle(0, 0, 10, 10), RectangleSize(10, 10), 2
    )

    assert tiles == [Rectangle(0, 0, 10, 10)]


def test_rectangle_overlapping_overcropped_tiles_20x10():
    tiles = rectangle_overlapping_tiles(
        Rectangle(0, 0, 20, 10), RectangleSize(10, 10), 2
    )

    assert tiles == list(
        [Rectangle(0, 0, 4, 10), Rectangle(2, 0, 10, 10), Rectangle(10, 0, 10, 10)]
    )


def test_rectangle_overlapping_overcropped_tiles_18x10():
    tiles = rectangle_overlapping_tiles(
        Rectangle(0, 0, 18, 10), RectangleSize(10, 10), 2
    )

    assert tiles == [Rectangle(0, 0, 10, 10), Rectangle(8, 0, 10, 10)]


def test_rectangle_overlapping_overcropped_tiles_10x18():
    tiles = rectangle_overlapping_tiles(
        Rectangle(0, 0, 10, 18), RectangleSize(10, 10), 2
    )

    assert tiles == [
        Rectangle(0, 0, 10, 10),
        Rectangle(0, 8, 10, 10),
    ]
