from applitools.core import NullScaleProvider
from applitools.selenium import Eyes


def test_set_get_scale_ratio():
    eyes = Eyes()
    eyes.scale_ratio = 2.0
    assert eyes.scale_ratio == 2.0

    eyes.scale_ratio = None
    assert eyes.scale_ratio == NullScaleProvider.UNKNOWN_SCALE_RATIO
