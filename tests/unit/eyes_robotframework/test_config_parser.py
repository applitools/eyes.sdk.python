import pytest
import trafaret as t

from applitools.selenium import BrowserType, RectangleSize, StitchMode
from EyesLibrary.config_parser import (
    TextToEnumTrafaret,
    ViewPortTrafaret,
    UpperTextToEnumTrafaret,
)


def test_text_to_enum_trafaret():
    assert BrowserType.CHROME == TextToEnumTrafaret(BrowserType).check("CHROME")
    assert StitchMode.CSS == TextToEnumTrafaret(StitchMode).check("CSS")

    with pytest.raises(t.DataError, match=r"Incorrect value `MissingBrowser`"):
        TextToEnumTrafaret(BrowserType).check("MissingBrowser")


def test_upper_text_to_enum_trafaret():
    assert BrowserType.CHROME == UpperTextToEnumTrafaret(BrowserType).check("CHROmE")
    assert StitchMode.CSS == UpperTextToEnumTrafaret(StitchMode).check("CSs")

    with pytest.raises(t.DataError, match=r"Incorrect value `MissingBrowser`"):
        UpperTextToEnumTrafaret(BrowserType).check("MissingBrowser")


def test_viewport_size_trafaret():
    expected_red = RectangleSize(400, 400)
    res = ViewPortTrafaret().check({"width": 400, "height": 400})
    assert res == expected_red
    res = ViewPortTrafaret().check("[400 400]")
    assert res == expected_red
