import pytest

from applitools.core import NullScaleProvider
from applitools.selenium import Eyes
from applitools.selenium.visual_grid import VisualGridRunner


@pytest.fixture(scope="function")
def eyes():
    return Eyes()


@pytest.fixture(scope="function")
def vg_eyes():
    return Eyes(VisualGridRunner())


def test_set_get_scale_ratio(eyes):
    eyes.scale_ratio = 2.0
    assert eyes.scale_ratio == 2.0

    eyes.scale_ratio = None
    assert eyes.scale_ratio == NullScaleProvider.UNKNOWN_SCALE_RATIO


def test_initialization():
    eyes = Eyes()
    eyes
