import pytest
from mock import patch

from applitools.common import (
    FloatingBounds,
    FloatingMatchSettings,
    MatchWindowData,
    Region,
)
from applitools.core import CheckSettings, MatchWindowTask


@pytest.fixture
def mwt(
    started_connector,
    running_session,
    configuration,
    eyes_base_mock,
    app_output_provider,
):
    return MatchWindowTask(
        started_connector,
        running_session,
        configuration.match_timeout,
        eyes=eyes_base_mock,
        app_output_provider=app_output_provider,
    )


def test_perform_match_with_no_regions(
    mwt, app_output_with_screenshot, image_match_settings, eyes_base_mock
):
    with patch("applitools.core.server_connector.ServerConnector.match_window") as smw:
        mwt.perform_match(
            app_output_with_screenshot,
            "Name",
            False,
            image_match_settings,
            eyes_base_mock,
        )
        match_window_data = smw.call_args[0][1]  # type: MatchWindowData
        ims = match_window_data.options.image_match_settings

    assert match_window_data.user_inputs == []
    assert ims.ignore == []
    assert ims.layout == []
    assert ims.strict == []
    assert ims.content == []
    assert ims.floating == []


def test_perform_match_collect_regions_from_screenshot(
    mwt, app_output_with_screenshot, image_match_settings, eyes_base_mock
):
    ignore_region = Region(5, 6, 7, 8)
    max_offset = 25
    floating_region = Region(0, 1, 2, 3)
    check_settings = (
        CheckSettings().ignore(ignore_region).floating(max_offset, floating_region)
    )
    with patch("applitools.core.server_connector.ServerConnector.match_window") as smw:
        mwt.perform_match(
            app_output_with_screenshot,
            "Name",
            False,
            image_match_settings,
            eyes_base_mock,
            check_settings=check_settings,
        )
        match_window_data = smw.call_args[0][1]  # type: MatchWindowData
        ims = match_window_data.options.image_match_settings

    assert ims.ignore == [ignore_region]

    assert ims.floating == [
        FloatingMatchSettings(
            region=floating_region,
            bounds=FloatingBounds(
                max_up_offset=max_offset,
                max_down_offset=max_offset,
                max_left_offset=max_offset,
                max_right_offset=max_offset,
            ),
        )
    ]
