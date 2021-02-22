import pytest

from applitools.common import CoordinatesType, Point, RectangleSize, Region
from tests.utils import parametrize_ids


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
    ids=parametrize_ids("left,top,width,height,coord_type,result"),
)
def test_region_creation(left, top, width, height, coord_type, result):
    expect = Region(left, top, width, height, coord_type)
    assert expect == result


@pytest.mark.parametrize(
    "x,y,result",
    [[0, 0, Point(0, 0)], [1.6, 2.2, Point(2, 2)]],
    ids=parametrize_ids("x,y,result"),
)
def test_point_creation(x, y, result):
    expect = Point(x, y)
    assert expect == result


@pytest.mark.parametrize(
    "width,height,result",
    [[0, 0, RectangleSize(0, 0)], [1.6, 2.2, RectangleSize(2, 2)]],
    ids=parametrize_ids("width,height,result"),
)
def test_rectangle_size_creation(width, height, result):
    expect = RectangleSize(width, height)
    assert expect == result
