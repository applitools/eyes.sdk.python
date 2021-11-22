import datetime
import json
import sys

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


def pytest_generate_tests(metafunc):
    if "eyes" in metafunc.fixturenames:
        metafunc.parametrize("eyes", ["selenium", "visual_grid"], indirect=True)


def open_and_get_start_session_info(
    eyes,
    driver,
    is_app=False,
    is_mobile_web=False,
    platform_name=None,
    device_name=None,
):
    driver.is_mobile_app = is_app
    driver.is_mobile_platform = is_app or is_mobile_web
    driver.is_mobile_web = is_mobile_web

    driver.desired_capabilities = {}
    if platform_name:
        driver.desired_capabilities["platformName"] = platform_name
    if device_name:
        driver.desired_capabilities["deviceName"] = device_name

    eyes.api_key = "Some API KEY"
    eyes._is_viewport_size_set = True

    with patch(
        "applitools.core.server_connector.ServerConnector.start_session"
    ) as start_session:
        with patch(
            "applitools.core.eyes_base.EyesBase._EyesBase__ensure_viewport_size"
        ):
            eyes.open(driver, "TestApp", "TestName")
    return start_session.call_args_list[0][0][0]


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
    if sys.version_info < (3,):
        message = "takes at least 2 arguments"
    else:
        message = "missing 1 required positional argument: 'check_settings'"
    with pytest.raises(TypeError, match=message):
        eyes_check_mock.check()


def test_selenium_eyes_check_args_only_name_keyword(eyes_check_mock):
    if sys.version_info < (3,):
        message = "takes at least 2 arguments"
    else:
        message = "missing 1 required positional argument: 'check_settings'"
    with pytest.raises(TypeError, match=message):
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


@pytest.mark.parametrize(
    "is_app,platform_name,device_name,is_mobile_web",
    [
        (False, "iOS", "iPhone X", True),
        (False, "Linux", "Desktop", False),
    ],
)
def test_start_session_environment_for_web(
    eyes, driver_mock, is_app, platform_name, device_name, is_mobile_web
):
    if eyes._visual_grid_eyes:
        pytest.skip("Not relevant for UFG")

    driver_mock.user_agent.origin_ua_string = "Some uastring"
    session_info = open_and_get_start_session_info(
        eyes, driver_mock, is_app, is_mobile_web, platform_name, device_name
    )
    assert session_info.environment.device_info == device_name
    assert session_info.environment.inferred == "useragent:Some uastring"


@pytest.mark.parametrize(
    "is_app,platform_name,device_name,is_mobile_web",
    [
        (True, "Android", "Galaxy S9", False),
        (True, "iOS", "iPhone X", False),
    ],
)
def test_start_session_environment_for_app(
    eyes, driver_mock, is_app, platform_name, device_name, is_mobile_web
):
    if eyes._visual_grid_eyes:
        pytest.skip("Not relevant for UFG")

    driver_mock.user_agent = MagicMock()
    driver_mock.user_agent.os_name_with_major_version = "Some os 19"
    driver_mock.user_agent.origin_ua_string = None

    session_info = open_and_get_start_session_info(
        eyes, driver_mock, is_app, is_mobile_web, platform_name, device_name
    )
    assert session_info.environment.os == "Some os 19"
    assert session_info.environment.device_info == device_name
    assert session_info.environment.inferred is None
