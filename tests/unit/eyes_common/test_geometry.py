import pytest

from applitools.common import CoordinatesType, Point, RectangleSize, Region
from applitools.common.geometry import SubregionForStitching


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
            physical_crop_area=Region(left=0, top=0, width=200, height=200),
            logical_crop_area=Region(left=0, top=0, width=100, height=100),
        ),
        SubregionForStitching(
            scroll_to=Point(x=0, y=90),
            paste_physical_location=Point(x=0, y=90),
            physical_crop_area=Region(left=0, top=0, width=200, height=200),
            logical_crop_area=Region(left=0, top=5, width=100, height=95),
        ),
        SubregionForStitching(
            scroll_to=Point(x=0, y=100),
            paste_physical_location=Point(x=0, y=166),
            physical_crop_area=Region(left=0, top=120, width=200, height=80),
            logical_crop_area=Region(left=0, top=5, width=100, height=35),
        ),
    ]
