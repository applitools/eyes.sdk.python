import pytest
import trafaret as t

from applitools.selenium import BrowserType, RectangleSize, StitchMode
from EyesLibrary.config_parser import ToEnumTrafaret, ViewPortTrafaret


def test_to_enum_trafaret():
    assert BrowserType.CHROME == ToEnumTrafaret(BrowserType).check("CHROME")
    assert StitchMode.CSS == ToEnumTrafaret(StitchMode).check("CSS")

    with pytest.raises(t.DataError, match=r"Incorrect value `MissingBrowser`"):
        ToEnumTrafaret(BrowserType).check("MissingBrowser")


def test_viewport_size_trafaret():
    expected_red = RectangleSize(400, 400)
    res = ViewPortTrafaret().check({"width": 400, "height": 400})
    assert res == expected_red
    res = ViewPortTrafaret().check("[400 400]")
    assert res == expected_red
