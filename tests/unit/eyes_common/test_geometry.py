import pytest

from applitools.common import Region, CoordinatesType, Point, RectangleSize


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
            2.0,
            3.0,
            4.0,
            CoordinatesType.SCREENSHOT_AS_IS,
            Region(1, 2, 3, 4, CoordinatesType.SCREENSHOT_AS_IS),
        ],
    ],
)
def test_region_creation(left, top, width, height, coord_type, result):
    expect = Region(left, top, width, height, coord_type)
    assert expect == result


@pytest.mark.parametrize(
    "x,y,result", [[0, 0, Point(0, 0)], [1, 2.0, Point(1, 2)]],
)
def test_point_creation(x, y, result):
    expect = Point(x, y)
    assert expect == result


@pytest.mark.parametrize(
    "width,height,result", [[0, 0, RectangleSize(0, 0)], [1, 2.0, RectangleSize(1, 2)]],
)
def test_rectangle_size_creation(width, height, result):
    expect = RectangleSize(width, height)
    assert expect == result
