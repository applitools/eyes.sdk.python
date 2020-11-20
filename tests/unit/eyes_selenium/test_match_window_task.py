import mock
import pytest
from selenium.webdriver.common.by import By

from applitools.common import (
    FloatingBounds,
    FloatingMatchSettings,
    Region,
    VisualGridSelector,
)
from applitools.common.accessibility import AccessibilityRegionType
from applitools.common.geometry import AccessibilityRegion, Rectangle
from applitools.core import CheckSettings, MatchWindowTask
from applitools.core.fluent.region import (
    AccessibilityRegionByRectangle,
    FloatingRegionByRectangle,
    RegionByRectangle,
)
from applitools.core.match_window_task import collect_regions_from_selectors
from applitools.selenium.fluent import RegionBySelector, RegionByElement


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


def test_collect_regions_from_selectors(mwt, eyes_base_mock):
    REGIONS = [
        Region(1, 1, 1, 1),
        Region(2, 2, 2, 2),
        Region(3, 3, 3, 3),
        Region(4, 4, 4, 4),
        Region(5, 5, 5, 5),
        Region(6, 6, 6, 6),
        Region(6, 6, 6, 6),
        Region(7, 7, 7, 7),
    ]
    REGIONS_SELECTORS = [
        [
            VisualGridSelector(
                ".selector1", RegionBySelector(By.TAG_NAME, "html", padding=None)
            )
        ],
        [],
        [
            VisualGridSelector(
                ".selector2",
                RegionByElement(mock.ANY, padding={"top": 20, "left": 100}),
            ),
            VisualGridSelector(".selector3", RegionByRectangle(Region(3, 3, 3, 3))),
        ],
        [
            VisualGridSelector(".selector3", RegionByRectangle(Region(4, 4, 4, 4))),
            VisualGridSelector(
                ".selector3",
                RegionBySelector(
                    By.CLASS_NAME, "some-class", {"width": 40, "height": 10}
                ),
            ),
            VisualGridSelector(
                ".selector3", RegionByElement(mock.ANY, padding={"left": 10})
            ),
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
    assert img.strict_regions == [Region(102, 22, 2, 2), Region(3, 3, 3, 3)]
    assert img.content_regions == [
        Region(4, 4, 4, 4),
        Region(5, 5, 45, 15),
        Region(16, 6, 6, 6),
    ]
    assert img.floating_match_settings == [
        FloatingMatchSettings(Region(6, 6, 6, 6), FloatingBounds(0, 2, 0, 0))
    ]
    assert img.accessibility == [
        AccessibilityRegion(7, 7, 7, 7, AccessibilityRegionType.GraphicalObject)
    ]
