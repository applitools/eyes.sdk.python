import pytest
from mock import patch

from applitools.common import (
    FloatingBounds,
    FloatingMatchSettings,
    MatchLevel,
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

    assert (
        match_window_data.options.image_match_settings.match_level == MatchLevel.STRICT
    )
    assert match_window_data.user_inputs == []
    assert ims.ignore_regions == []
    assert ims.layout_regions == []
    assert ims.strict_regions == []
    assert ims.content_regions == []
    assert ims.floating_match_settings == []


def test_perform_match_collect_regions_from_screenshot(
    mwt, app_output_with_screenshot, eyes_base_mock
):
    ignore_region = Region(5, 6, 7, 8)
    max_offset = 25
    floating_region = Region(0, 1, 2, 3)
    content_region = Region(1, 2, 2, 1)
    check_settings = (
        CheckSettings()
        .ignore(ignore_region)
        .floating(max_offset, floating_region)
        .content(content_region)
    )
    image_match_settings = mwt.create_image_match_settings(
        check_settings, eyes_base_mock
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

    assert ims.content_regions == [content_region]
    assert ims.match_level == MatchLevel.CONTENT
    assert ims.ignore_regions == [ignore_region]

    assert ims.floating_match_settings == [
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


def test_perform_match_with_render_id(
    mwt, app_output_with_screenshot, image_match_settings, eyes_base_mock
):
    check_settings = CheckSettings()
    with patch("applitools.core.server_connector.ServerConnector.match_window") as smw:
        mwt.perform_match(
            app_output_with_screenshot,
            "Name",
            False,
            image_match_settings,
            eyes_base_mock,
            check_settings=check_settings,
            render_id="some-render-id",
        )
        match_window_data = smw.call_args[0][1]  # type: MatchWindowData

    assert match_window_data.render_id == "some-render-id"
    assert match_window_data.options.render_id == "some-render-id"
