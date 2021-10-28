import pytest

from applitools.selenium import (
    Region,
    Target,
)
from applitools.selenium.selenium_eyes import SeleniumEyes

pytestmark = [
    pytest.mark.platform("Linux", "macOS"),
    pytest.mark.test_suite_name("Eyes Selenium SDK - Fluent API"),
    pytest.mark.viewport_size({"width": 700, "height": 460}),
    pytest.mark.test_page_url(
        "http://applitools.github.io/demo/TestPages/FramesTestPage/"
    ),
]


def test_check_element_with_ignore_region_by_element__fluent(eyes_opened):
    element = eyes_opened.driver.find_element_by_id("overflowing-div-image")
    ignore_element = eyes_opened.driver.find_element_by_id("overflowing-div")
    eyes_opened.check(
        "Fluent - Region by element - fully",
        Target.region(element).ignore(ignore_element),
    )


@pytest.mark.eyes_config(branch_name="master_python")
def test_check_window_with_match_region_paddings__fluent(
    eyes_opened, check_test_result
):
    eyes_opened.check(
        "Fluent - Window with ignore region by selector stretched",
        Target.window()
        .fully()
        .ignore(".ignore", padding=dict(left=10))
        .content("#stretched", padding=dict(top=10))
        .layout("#centered", padding=dict(top=10, right=50))
        .strict("overflowing-div", padding=dict(bottom=100)),
    )
    # regions are different for latest UFG chrome vs classic chrome
    if isinstance(eyes_opened._current_eyes, SeleniumEyes):
        expected_regions = [
            Region(10 + 10, 286, 800, 500),
            Region(122 + 10, 933, 456, 306),
            Region(8 + 10, 1277, 690, 206),
        ]
    else:
        expected_regions = [
            Region(10 + 10, 285, 800, 501),
            Region(122 + 10, 932, 456, 307),
            Region(8 + 10, 1276, 690, 207),
        ]

    check_test_result.send(
        [
            {
                "actual_name": "ignore",
                "expected": expected_regions,
            }
        ]
    )


def test_manual_switch_frame(eyes_opened):
    eyes_opened.driver.switch_to.frame("frame1")
    eyes_opened.check("", Target.region("#inner-frame-div"))
