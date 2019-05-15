import pytest
from applitools.common import MatchLevel, StitchMode

from applitools.core import NullScaleProvider
from applitools.selenium import Eyes
from applitools.selenium.visual_grid import VisualGridRunner


def pytest_generate_tests(metafunc):
    if "eyes" in metafunc.fixturenames:
        metafunc.parametrize("eyes", ["selenium", "visual_grid"], indirect=True)


@pytest.fixture(scope="function")
def eyes(request):
    if request.param == "selenium":
        return Eyes()
    elif request.param == "visual_grid":
        return Eyes(VisualGridRunner())
    else:
        raise ValueError("invalid internal test config")


def test_set_get_scale_ratio(eyes):
    eyes.scale_ratio = 2.0
    assert eyes.scale_ratio == 2.0

    if not eyes._is_visual_grid_eyes:
        eyes.scale_ratio = None
        assert eyes.scale_ratio == NullScaleProvider.UNKNOWN_SCALE_RATIO


def test_match_level(eyes):
    assert eyes.match_level == MatchLevel.STRICT
    eyes.match_level = MatchLevel.EXACT
    assert eyes.match_level == MatchLevel.EXACT
    assert eyes.configuration.match_level == MatchLevel.EXACT
    eyes.match_level = MatchLevel.LAYOUT
    assert eyes.match_level == MatchLevel.LAYOUT
    assert eyes.configuration.match_level == MatchLevel.LAYOUT


def test_stitch_mode(eyes):
    assert eyes.stitch_mode == StitchMode.Scroll
    assert eyes.configuration.stitch_mode == StitchMode.Scroll
    eyes.stitch_mode = StitchMode.CSS
    assert eyes.stitch_mode == StitchMode.CSS
    assert eyes.configuration.stitch_mode == StitchMode.CSS
