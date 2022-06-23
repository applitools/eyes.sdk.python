from applitools.core import TextRegionSettings


def test_text_region_settings():
    data = TextRegionSettings("one")
    assert data._patterns == ["one"]

    data = TextRegionSettings("one", "two")
    assert data._patterns == ["one", "two"]
    data = TextRegionSettings(["one", "two"])
    assert data._patterns == ["one", "two"]
