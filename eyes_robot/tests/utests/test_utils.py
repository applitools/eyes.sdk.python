import pytest
from EyesLibrary.utils import parse_region, parse_viewport_size

from applitools.common import Region


@pytest.mark.parametrize(
    "to_parse,result",
    [
        ("[34 65]", {"width": 34, "height": 65}),
        ("[34 6.6]", {"width": 34, "height": 7}),
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
