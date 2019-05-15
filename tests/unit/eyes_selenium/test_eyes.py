import pytest
from applitools.common import MatchLevel

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

    eyes.scale_ratio = None
    assert eyes.scale_ratio == NullScaleProvider.UNKNOWN_SCALE_RATIO


def test_match_level(eyes):
    assert eyes.match_level == MatchLevel.STRICT
    eyes.match_level = MatchLevel.EXACT
    assert eyes.match_level == MatchLevel.EXACT
    eyes.match_level = MatchLevel.LAYOUT
    assert eyes.match_level == MatchLevel.LAYOUT
