import pytest
from selenium.webdriver.common.by import By

from applitools.selenium import Region, StitchMode, Target

pytestmark = [
    pytest.mark.platform("Linux"),
    pytest.mark.viewport_size({"width": 700, "height": 460}),
    pytest.mark.test_suite_name("Eyes Selenium SDK - Fluent API Frames"),
    pytest.mark.test_page_url(
        "http://applitools.github.io/demo/TestPages/FramesTestPage/"
    ),
    pytest.mark.parametrize(
        "eyes",
        [dict(stitch_mode=StitchMode.CSS), dict(stitch_mode=StitchMode.Scroll)],
        indirect=True,
        ids=lambda o: "CSS" if o["stitch_mode"] == StitchMode.CSS else "Scroll",
    ),
]


def test_check_frame__fully__fluent(eyes_opened):
    eyes_opened.check("Fluent - Full Frame", Target.frame("frame1").fully())


def test_check_frame__fluent(eyes_opened):
    eyes_opened.hide_scrollbars = False
    eyes_opened.check("Fluent - Frame", Target.frame("frame1"))


def test_check_frame_in_frame__fully__fluent(eyes_opened):
    eyes_opened.check(
        "Fluent - Full Frame in Frame", Target.frame("frame1").frame("frame1-1").fully()
    )


def test_check_region_in_frame__fluent(eyes_opened):
    eyes_opened.check(
        "Fluent - Region in Frame in Frame",
        Target.frame("frame1").region([By.ID, "inner-frame-div"]).fully(),
    )


def test_check_region_in_frame_in_frame__fluent(eyes_opened):
    eyes_opened.check(
        "Fluent - Region in Frame in Frame",
        Target.frame("frame1").frame("frame1-1").region("img").fully(),
    )


def test_check_region_in_frame2__fluent(eyes_opened):
    eyes_opened.check(
        "Fluent - Inner frame div 1",
        Target.frame("frame1")
        .region("#inner-frame-div")
        .fully()
        .timeout(5000)
        .ignore(Region(50, 50, 100, 100)),
    )

    eyes_opened.check(
        "Fluent - Inner frame div 2",
        Target.frame("frame1")
        .region("#inner-frame-div")
        .fully()
        .ignore(Region(50, 50, 100, 100))
        .ignore(Region(70, 170, 90, 90)),
    )

    eyes_opened.check(
        "Fluent - Inner frame div 3",
        Target.frame("frame1").region("#inner-frame-div").fully().timeout(5000),
    )

    eyes_opened.check(
        "Fluent - Inner frame div 4",
        Target.frame("frame1").region("#inner-frame-div").fully(),
    )

    eyes_opened.check(
        "Fluent - Full frame with floating region",
        Target.frame("frame1")
        .fully()
        .layout()
        .floating(25, Region(200, 200, 150, 150)),
    )


def test_check_region_in_frame3__fluent(eyes_opened):
    eyes_opened.check(
        "Fluent - Full frame with floating region",
        Target.frame("frame1")
        .fully()
        .layout()
        .floating(25, Region(200, 200, 150, 150)),
    )


def test_check_region_by_coordinate_in_frame__fully__fluent(eyes_opened):
    eyes_opened.check(
        "Fluent - Inner frame coordinates",
        Target.frame("frame1").region(Region(30, 40, 400, 1200)).fully(),
    )


def test_check_region_by_coordinate_in_frame__fluent(eyes_opened):
    eyes_opened.hide_scrollbars = False
    eyes_opened.check(
        "Fluent - Inner frame coordinates",
        Target.frame("frame1").region(Region(30, 40, 400, 1200)),
    )


def test_check_frame_in_frame__fully__fluent2(eyes_opened):
    eyes_opened.check("Fluent - Window", Target.window().fully())
    eyes_opened.check(
        "Fluent - Full Frame in Frame 2",
        Target.frame("frame1").frame("frame1-1").fully(),
    )


def test_manual_switch_frame(eyes_opened):
    eyes_opened.driver.switch_to.frame("frame1")
    eyes_opened.check("", Target.region("#inner-frame-div"))
