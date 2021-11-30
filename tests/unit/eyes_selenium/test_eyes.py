import pytest

from applitools.common import EyesError, MatchLevel, StitchMode
from applitools.core import FixedCutProvider, UnscaledFixedCutProvider
from applitools.selenium import Eyes, Target


def pytest_generate_tests(metafunc):
    if "eyes" in metafunc.fixturenames:
        metafunc.parametrize("eyes", ["selenium", "visual_grid"], indirect=True)


def test_set_get_scale_ratio(eyes):
    eyes.scale_ratio = 2.0
    assert eyes.scale_ratio == 2.0


def test_match_level(eyes):
    assert eyes.match_level == MatchLevel.STRICT
    eyes.match_level = MatchLevel.EXACT
    assert eyes.match_level == MatchLevel.EXACT
    assert eyes.configure.match_level == MatchLevel.EXACT
    eyes.match_level = MatchLevel.LAYOUT
    assert eyes.match_level == MatchLevel.LAYOUT
    assert eyes.configure.match_level == MatchLevel.LAYOUT


def test_stitch_mode(eyes):
    assert eyes.stitch_mode == StitchMode.Scroll
    assert eyes.configure.stitch_mode == StitchMode.Scroll
    eyes.stitch_mode = StitchMode.CSS
    assert eyes.stitch_mode == StitchMode.CSS
    assert eyes.configure.stitch_mode == StitchMode.CSS


def test_config_overwriting(eyes):
    eyes.host_app = "Host1"
    eyes2 = Eyes()
    eyes2.host_app = "Host2"
    assert eyes.host_app != eyes2.host_app
    assert eyes.configure.host_app != eyes2.configure.host_app

    eyes.configure.host_app = "Other Host1"
    eyes2.configure.host_app = "Other Host2"
    assert eyes.host_app != eyes2.host_app
    assert eyes.configure.host_app != eyes2.configure.host_app


def test_baseline_name(eyes, driver_mock):
    eyes.baseline_branch_name = "Baseline"
    assert eyes.baseline_branch_name == "Baseline"
    assert eyes.configure.baseline_branch_name == "Baseline"


def test_branch_name(eyes, driver_mock):
    eyes.branch_name = "Branch"
    assert eyes.branch_name == "Branch"
    assert eyes.configure.branch_name == "Branch"


def test_baseline_env_name(eyes, driver_mock):
    eyes.baseline_env_name = "Baseline Env"
    assert eyes.baseline_env_name == "Baseline Env"
    assert eyes.configure.baseline_env_name == "Baseline Env"


def test_get_set_cut_provider(eyes):
    eyes.cut_provider = FixedCutProvider(20, 0, 0, 0)
    assert isinstance(eyes.cut_provider, FixedCutProvider)

    eyes.cut_provider = UnscaledFixedCutProvider(10, 0, 5, 0)
    assert isinstance(eyes.cut_provider, UnscaledFixedCutProvider)


def test_check_without_open_call(eyes):
    with pytest.raises(EyesError):
        eyes.check("Test", Target.window())


def test_eyes_base_abort(eyes):
    eyes.abort()


def test_rotation():
    eyes = Eyes()
    eyes.rotation = 2
    assert eyes.rotation == 2
    assert eyes.configure.rotation == 2


def test_add_clear_properties(eyes):
    eyes.add_property("Name", "val")
    assert eyes.configure.properties == [{"name": "Name", "value": "val"}]
    eyes.clear_properties()
    assert eyes.configure.properties == []
