import datetime
import json

import pytest
from mock import MagicMock, call, patch

from applitools.common import BatchInfo, EyesError, MatchLevel, StitchMode
from applitools.common.utils import json_utils
from applitools.core import (
    FixedCutProvider,
    NullScaleProvider,
    UnscaledFixedCutProvider,
)
from applitools.selenium import Configuration, Eyes, Target
from applitools.selenium.fluent import SeleniumCheckSettings


def open_and_get_start_session_info(eyes, driver):
    eyes.api_key = "Some API KEY"
    eyes._is_viewport_size_set = True
    driver.is_mobile_app = False

    with patch(
        "applitools.core.server_connector.ServerConnector.start_session"
    ) as start_session:
        with patch(
            "applitools.core.eyes_base.EyesBase._EyesBase__ensure_viewport_size"
        ):
            eyes.open(driver, "TestApp", "TestName")
    return start_session.call_args_list[0][0][0]


@pytest.mark.parametrize(
    "kwargs", [{}, {"test_name": "TestName"}, {"app_name": "AppName"}]
)
def test_open_with_missing_test_name_and_app_name(eyes, driver_mock, kwargs):
    with pytest.raises(ValueError):
        eyes.open(driver_mock, **kwargs)


@pytest.mark.parametrize(
    "config",
    [
        Configuration(),
        Configuration(test_name="TestName"),
        Configuration(app_name="AppName"),
    ],
)
def test_open_with_missing_test_name_and_app_name_with_config(
    eyes, driver_mock, config
):
    with pytest.raises(ValueError):
        eyes.set_configuration(config)
        eyes.open(driver_mock)


def pytest_generate_tests(metafunc):
    if "eyes" in metafunc.fixturenames:
        metafunc.parametrize("eyes", ["selenium", "visual_grid"], indirect=True)


def test_set_get_scale_ratio(eyes):
    eyes.scale_ratio = 2.0
    if eyes._is_visual_grid_eyes:
        assert eyes.scale_ratio == 0
    else:
        assert eyes.scale_ratio == 2.0
        eyes.scale_ratio = None
        assert eyes.scale_ratio == NullScaleProvider.UNKNOWN_SCALE_RATIO


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

    if not eyes._visual_grid_eyes:
        session_info = open_and_get_start_session_info(eyes, driver_mock)
        assert session_info.baseline_branch_name == "Baseline"


def test_branch_name(eyes, driver_mock):
    eyes.branch_name = "Branch"
    assert eyes.branch_name == "Branch"
    assert eyes.configure.branch_name == "Branch"

    if not eyes._visual_grid_eyes:
        session_info = open_and_get_start_session_info(eyes, driver_mock)
        assert session_info.branch_name == "Branch"


def test_baseline_env_name(eyes, driver_mock):
    eyes.baseline_env_name = "Baseline Env"
    assert eyes.baseline_env_name == "Baseline Env"
    assert eyes.configure.baseline_env_name == "Baseline Env"

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


def test_rotation(driver_mock):
    eyes = Eyes()
    eyes.rotation = 2
    assert eyes.rotation is None

    open_and_get_start_session_info(eyes, driver_mock)
    eyes.rotation = 2
    assert eyes.rotation == 2
    assert eyes._driver.rotation == 2


def test_add_clear_properties(eyes):
    eyes.add_property("Name", "val")
    assert eyes.configure.properties == [{"name": "Name", "value": "val"}]
    eyes.clear_properties()
    assert eyes.configure.properties == []


@pytest.fixture
def eyes_check_mock():
    eyes = Eyes()
    eyes._is_opened = True
    eyes._selenium_eyes = MagicMock()
    eyes.calls = eyes._selenium_eyes.check.call_args_list
    return eyes


def test_selenium_eyes_check_args_empty(eyes_check_mock):
    with pytest.raises(
        TypeError, message="missing 1 required positional argument: 'check_settings'"
    ):
        eyes_check_mock.check()


def test_selenium_eyes_check_args_only_name_keyword(eyes_check_mock):
    with pytest.raises(
        TypeError, message="missing 1 required positional argument: 'check_settings'"
    ):
        eyes_check_mock.check(name="A")


def test_selenium_eyes_check_args_only_name_positional(eyes_check_mock):
    eyes_check_mock.check("A")

    assert eyes_check_mock.calls == [call(SeleniumCheckSettings().with_name("A"))]


def test_selenium_eyes_check_args_only_settings_keyword(eyes_check_mock):
    eyes_check_mock.check(check_settings=SeleniumCheckSettings())

    assert eyes_check_mock.calls == [call(SeleniumCheckSettings())]


def test_selenium_eyes_check_args_only_settings_positional(eyes_check_mock):
    eyes_check_mock.check(SeleniumCheckSettings())

    assert eyes_check_mock.calls == [call(SeleniumCheckSettings())]


def test_selenium_eyes_check_args_both_positional(eyes_check_mock):
    eyes_check_mock.check("A", SeleniumCheckSettings())

    assert eyes_check_mock.calls == [call(SeleniumCheckSettings().with_name("A"))]


def test_selenium_eyes_check_args_both_keyword(eyes_check_mock):
    eyes_check_mock.check(check_settings=SeleniumCheckSettings(), name="A")

    assert eyes_check_mock.calls == [call(SeleniumCheckSettings().with_name("A"))]


def test_selenium_eyes_check_args_name_valid_settings_none(eyes_check_mock):
    eyes_check_mock.check("A", None)

    assert eyes_check_mock.calls == [call(SeleniumCheckSettings().with_name("A"))]


def test_selenium_eyes_check_args_both_none(eyes_check_mock):
    eyes_check_mock.check(None, None)

    assert eyes_check_mock.calls == [call(SeleniumCheckSettings())]


def test_selenium_eyes_check_args_name_none_check_settings_valid(eyes_check_mock):
    eyes_check_mock.check(None, SeleniumCheckSettings().with_name("A"))

    assert eyes_check_mock.calls == [call(SeleniumCheckSettings().with_name("A"))]


def test_selenium_eyes_check_args_override_name(eyes_check_mock):
    eyes_check_mock.check("A", SeleniumCheckSettings().with_name("B"))

    assert eyes_check_mock.calls == [call(SeleniumCheckSettings().with_name("A"))]
