import datetime
import json

import pytest
from applitools.common import BatchInfo, EyesError, MatchLevel, StitchMode
from applitools.common.utils import json_utils
from applitools.core import (
    FixedCutProvider,
    NullScaleProvider,
    UnscaledFixedCutProvider,
)
from applitools.selenium import Eyes, Target
from applitools.selenium.visual_grid import VisualGridRunner
from mock import patch


def open_and_get_start_session_info(eyes, driver):
    eyes.api_key = "Some API KEY"
    eyes._is_viewport_size_set = True

    with patch(
        "applitools.core.server_connector.ServerConnector.start_session"
    ) as start_session:
        with patch(
            "applitools.core.eyes_base.EyesBase._EyesBase__ensure_viewport_size"
        ):
            eyes.open(driver, "TestApp", "TestName")
    session_start_info = start_session.call_args_list[0][0][0]
    return session_start_info


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


def test_config_overwriting(eyes):
    eyes.host_app = "Host1"
    eyes2 = Eyes()
    eyes2.host_app = "Host2"
    assert eyes.host_app != eyes2.host_app
    assert eyes.configuration.host_app != eyes2.configuration.host_app

    eyes.configuration.host_app = "Other Host1"
    eyes2.configuration.host_app = "Other Host2"
    assert eyes.host_app != eyes2.host_app
    assert eyes.configuration.host_app != eyes2.configuration.host_app


def test_baseline_name(eyes, driver_mock):
    eyes.baseline_branch_name = "Baseline"
    assert eyes.baseline_branch_name == "Baseline"
    assert eyes.configuration.baseline_branch_name == "Baseline"

    if not eyes._visual_grid_eyes:
        session_info = open_and_get_start_session_info(eyes, driver_mock)
        assert session_info.baseline_branch_name == "Baseline"


def test_branch_name(eyes, driver_mock):
    eyes.branch_name = "Branch"
    assert eyes.branch_name == "Branch"
    assert eyes.configuration.branch_name == "Branch"

    if not eyes._visual_grid_eyes:
        session_info = open_and_get_start_session_info(eyes, driver_mock)
        assert session_info.branch_name == "Branch"


def test_baseline_env_name(eyes, driver_mock):
    eyes.baseline_env_name = "Baseline Env"
    assert eyes.baseline_env_name == "Baseline Env"
    assert eyes.configuration.baseline_env_name == "Baseline Env"

    if not eyes._visual_grid_eyes:
        session_info = open_and_get_start_session_info(eyes, driver_mock)
        assert session_info.baseline_env_name == "Baseline Env"


def test_batch_info_serializing(eyes, driver_mock):
    date = datetime.datetime.strptime("2019-06-04T10:27:15Z", "%Y-%m-%dT%H:%M:%SZ")
    eyes.batch = BatchInfo("Batch Info", date)
    eyes.batch.sequence_name = "Sequence"

    if not eyes._visual_grid_eyes:
        session_info = open_and_get_start_session_info(eyes, driver_mock)
        info_json = json_utils.to_json(session_info)
        batch_info = json.loads(info_json)["startInfo"]["batchInfo"]

        assert batch_info["name"] == "Batch Info"
        assert batch_info["batchSequenceName"] == "Sequence"
        assert batch_info["startedAt"] == "2019-06-04T10:27:15Z"


def test_get_set_cut_provider(eyes):
    if not eyes._visual_grid_eyes:
        eyes.cut_provider = FixedCutProvider(20, 0, 0, 0)
        assert isinstance(eyes._current_eyes._cut_provider, FixedCutProvider)
        assert isinstance(eyes.cut_provider, FixedCutProvider)

        eyes.cut_provider = UnscaledFixedCutProvider(10, 0, 5, 0)
        assert isinstance(eyes._current_eyes._cut_provider, UnscaledFixedCutProvider)
        assert isinstance(eyes.cut_provider, UnscaledFixedCutProvider)


def test_check_without_open_call(eyes):
    with pytest.raises(EyesError):
        eyes.check("Test", Target.window())


def test_eyes_base_abort(eyes):
    eyes.abort()
