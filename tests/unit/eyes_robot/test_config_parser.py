import pytest
import trafaret as t

from applitools.selenium import BrowserType, RectangleSize, StitchMode
from EyesLibrary.config_parser import ToEnumTrafaret, ViewPortTrafaret


def test_to_enum_trafaret():
    assert BrowserType.CHROME == ToEnumTrafaret(BrowserType, "browser_type").check(
        "CHROME"
    )
    assert StitchMode.CSS == ToEnumTrafaret(StitchMode, "stitch_mode").check("CSS")

    with pytest.raises(t.DataError, match=r"Incorrect value for `browser_type`"):
        ToEnumTrafaret(BrowserType, "browser_type").check("MissingBrowser")


def test_viewport_size_trafaret():
    expected_red = RectangleSize(400, 400)
    res = ViewPortTrafaret().check({"width": 400, "height": 400})
    assert res == expected_red
    res = ViewPortTrafaret().check("[400 400]")
    assert res == expected_red
