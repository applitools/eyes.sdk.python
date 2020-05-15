import pytest
from mock import patch

from applitools.common import (
    FloatingBounds,
    FloatingMatchSettings,
    MatchLevel,
    MatchWindowData,
    Region,
    VisualGridSelector,
)
from applitools.common.accessibility import AccessibilityRegionType
from applitools.common.geometry import AccessibilityRegion, Rectangle
from applitools.core import CheckSettings, MatchWindowTask
from applitools.core.fluent.region import (
    AccessibilityRegionByRectangle,
    RegionByRectangle,
    FloatingRegionByRectangle,
)
from applitools.core.match_window_task import collect_regions_from_selectors


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


def test_collect_regions_from_selectors(mwt, eyes_base_mock):
    REGIONS = [
        Region(1, 1, 1, 1),
        Region(2, 2, 2, 2),
        Region(3, 3, 3, 3),
        Region(4, 4, 4, 4),
        Region(5, 5, 5, 5),
        Region(6, 6, 6, 6),
        FloatingMatchSettings(Region(6, 6, 6, 6), FloatingBounds(0, 2, 0, 0)),
        AccessibilityRegion(7, 7, 7, 7, AccessibilityRegionType.GraphicalObject),
    ]
    REGIONS_SELECTORS = [
        [VisualGridSelector(".selector1", RegionByRectangle(Region(1, 1, 1, 1)))],
        [],
        [
            VisualGridSelector(".selector2", RegionByRectangle(Region(2, 2, 2, 2))),
            VisualGridSelector(".selector3", RegionByRectangle(Region(3, 3, 3, 3))),
        ],
        [
            VisualGridSelector(".selector3", RegionByRectangle(Region(4, 4, 4, 4))),
            VisualGridSelector(".selector3", RegionByRectangle(Region(5, 5, 5, 5))),
            VisualGridSelector(".selector3", RegionByRectangle(Region(6, 6, 6, 6))),
        ],
        [
            VisualGridSelector(
                ".selector4",
                FloatingRegionByRectangle(
                    Rectangle(6, 6, 6, 6), FloatingBounds(0, 2, 0, 0)
                ),
            ),
        ],
        [
            VisualGridSelector(
                ".selector5",
                AccessibilityRegionByRectangle(
                    AccessibilityRegion(
                        7, 7, 7, 7, AccessibilityRegionType.GraphicalObject
                    )
                ),
            )
        ],
        [],
    ]
    check_settings = CheckSettings()
    image_match_settings = mwt.create_image_match_settings(
        check_settings, eyes_base_mock
    )
    img = collect_regions_from_selectors(
        image_match_settings, REGIONS, REGIONS_SELECTORS
    )
    assert img.ignore_regions == [Region(1, 1, 1, 1)]
    assert img.strict_regions == [Region(2, 2, 2, 2), Region(3, 3, 3, 3)]
    assert img.content_regions == [
        Region(4, 4, 4, 4),
        Region(5, 5, 5, 5),
        Region(6, 6, 6, 6),
    ]
    assert img.floating_match_settings == [
        FloatingMatchSettings(Region(6, 6, 6, 6), FloatingBounds(0, 2, 0, 0))
    ]
    assert img.accessibility == [
        AccessibilityRegion(7, 7, 7, 7, AccessibilityRegionType.GraphicalObject)
    ]


def test_perform_match_collect_regions_from_screenshot(
    mwt, app_output_with_screenshot, eyes_base_mock
):
    ignore_region = Region(5, 6, 7, 8)
    max_offset = 25
    floating_region = Region(0, 1, 2, 3)
    content_region = Region(1, 2, 2, 1)
    accessibility_region = AccessibilityRegion(
        1, 2, 1, 2, AccessibilityRegionType.GraphicalObject
    )
    check_settings = (
        CheckSettings()
        .ignore(ignore_region)
        .floating(max_offset, floating_region)
        .content(content_region)
        .accessibility(accessibility_region)
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
    assert ims.accessibility == [accessibility_region]


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
