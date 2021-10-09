import pytest

from applitools.common import MatchLevel, RectangleSize, Region
from EyesLibrary.utils import get_enum_by_name, parse_region, parse_viewport_size


@pytest.mark.parametrize(
    "to_parse,result",
    [
        ("[34 65]", RectangleSize(width=34, height=65)),
        ("[34 6.6]", RectangleSize(width=34, height=7)),
    ],
)
def test_parse_viewport_size_success(to_parse, result):
    assert parse_viewport_size(to_parse) == result


@pytest.mark.parametrize("to_parse", ["[34", "[432 234", "234 234", "324 455]"])
def test_parse_viewport_size_failed(to_parse):
    with pytest.raises(ValueError):
        assert parse_viewport_size(to_parse)


@pytest.mark.parametrize(
    "to_parse,result",
    [
        ("[400 200 344 555]", Region(400, 200, 344, 555)),
        ("[0 0.0 0 3.6]", Region(0, 0, 0, 4)),
    ],
)
def test_parse_region_success(to_parse, result):
    assert parse_region(to_parse) == result


@pytest.mark.parametrize("to_parse", ["[34 34 56", "432 234", "[33 324 455]"])
def test_parse_region_failed(to_parse):
    with pytest.raises(ValueError):
        assert parse_region(to_parse)


def test_get_enum_by_name():
    assert get_enum_by_name("LAYOUT", MatchLevel) == MatchLevel.LAYOUT
    assert get_enum_by_name("LayouT", MatchLevel) == MatchLevel.LAYOUT
    assert get_enum_by_name("layout", MatchLevel) == MatchLevel.LAYOUT


def test_get_enum_by_name_failed():
    with pytest.raises(
        ValueError, match="`<enum 'MatchLevel'>` does not contain `Not present`"
    ):
        get_enum_by_name("Not present", MatchLevel)
