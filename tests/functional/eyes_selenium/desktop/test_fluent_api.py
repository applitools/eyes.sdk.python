import pytest

from applitools.selenium import Region, StitchMode, Target

pytestmark = [
    pytest.mark.platform("Linux", "macOS"),
    pytest.mark.test_suite_name("Eyes Selenium SDK - Fluent API"),
    pytest.mark.viewport_size({"width": 700, "height": 460}),
    pytest.mark.test_page_url(
        "http://applitools.github.io/demo/TestPages/FramesTestPage/"
    ),
]


def test_check_window_with_ignore_region__fluent(eyes_opened):
    eyes_opened.driver.find_element_by_tag_name("input").send_keys("My Input")
    eyes_opened.check(
        "Fluent - Window with Ignore region",
        Target.window()
        .fully()
        .timeout(5000)
        .ignore_caret()
        .ignore(Region(left=50, top=50, width=100, height=100)),
    )


def test_check_region_with_ignore_region__fluent(eyes_opened):
    eyes_opened.check(
        "Fluent - Region with Ignore region",
        Target.region("#overflowing-div").ignore(
            Region(left=50, top=50, width=100, height=100)
        ),
    )


def test_check_check_window__fluent(eyes_opened):
    eyes_opened.check("Fluent - Window", Target.window())


def test_scrollbars_hidden_and_returned__fluent(eyes_opened):
    eyes_opened.check("Fluent - Window (Before)", Target.window().fully())
    eyes_opened.check(
        "Fluent - Inner frame div",
        Target.frame("frame1").region("#inner-frame-div").fully(),
    )
    eyes_opened.check("Fluent - Window (After)", Target.window().fully())


def test_check_window_with_ignore_by_selector__fluent(eyes_opened):
    eyes_opened.check(
        "Fluent - Window with ignore region by selector",
        Target.window().ignore("#overflowing-div"),
    )


def test_check_window_with_floating_by_selector_fluent(eyes_opened):
    eyes_opened.check(
        "Fluent - Window with floating region by selector",
        Target.window().floating("#overflowing-div", 3, 3, 20, 30),
    )


def test_check_window_with_floating_by_region__fluent(eyes_opened):
    eyes_opened.check(
        "Fluent - Window with floating region by selector",
        Target.window().floating(Region(10, 10, 10, 10), 3, 3, 20, 30),
    )


def test_check_element_fully__fluent(eyes_opened):
    element = eyes_opened.driver.find_element_by_css_selector("#overflowing-div-image")
    eyes_opened.check(
        "Fluent - Region by element - fully", Target.region(element).fully()
    )


def test_check_element_with_ignore_region_by_element__fluent(eyes_opened):
    element = eyes_opened.driver.find_element_by_id("overflowing-div-image")
    ignore_element = eyes_opened.driver.find_element_by_id("overflowing-div")
    eyes_opened.check(
        "Fluent - Region by element - fully",
        Target.region(element).ignore(ignore_element),
    )


def test_check_element_fluent(eyes_opened):
    element = eyes_opened.driver.find_element_by_id("overflowing-div-image")
    eyes_opened.check("Fluent - Region by element - fully", Target.region(element))


def test_check_element_with_ignore_region_by_element_outside_the_viewport__fluent(
    eyes_opened
):
    element = eyes_opened.driver.find_element_by_id("overflowing-div-image")
    ignore_element = eyes_opened.driver.find_element_by_id("overflowing-div")
    eyes_opened.check(
        "Fluent - Region by element", Target.region(element).ignore(ignore_element)
    )


def test_check_element_with_ignore_region_by_same_element__fluent(eyes_opened):
    element = eyes_opened.driver.find_element_by_id("overflowing-div-image")
    eyes_opened.check(
        "Fluent - Region by element", Target.region(element).ignore(element)
    )


def test_check_full_window_with_multiple_ignore_regions_by_selector__fluent(
    eyes_opened
):
    eyes_opened.check(
        "Fluent - Region by element", Target.window().fully().ignore(".ignore")
    )


def test_check_overflowing_region_by_coordinates__fluent(eyes_opened):
    eyes_opened.check(
        "Fluent - Region by overflowing coordinates",
        Target.region(Region(50, 110, 90, 550)),
    )


@pytest.mark.skip("Not implemented")
def test_check_many(eyes_opened):
    eyes_opened.check(
        Target.region("#overflowing-div-image").with_name("overflowing div image"),
        Target.region("overflowing-div").with_name("overflowing div"),
        Target.region("overflowing-div-image")
        .fully()
        .with_name("overflowing div image (fully)"),
        Target.frame("frame1")
        .frame("frame1-1")
        .fully()
        .with_name("Full Frame in Frame"),
        Target.frame("frame1").with_name("frame1"),
        Target.region(Region(30, 50, 300, 620)).with_name("rectangle"),
    )


def test_check_region_by_coordinates__fluent(eyes_opened):
    eyes_opened.check(
        "Fluent - Region by coordinates", Target.region(Region(50, 70, 90, 110))
    )


def test_check_scrollable_modal(eyes_opened):
    eyes_opened.driver.find_element_by_id("centered").click()
    scroll_root_sel = (
        "#modal-content" if eyes_opened.stitch_mode == StitchMode.CSS else "#modal"
    )
    eyes_opened.check(
        "Scrollable Modal",
        Target.region("#modal-content").fully().scroll_root_element(scroll_root_sel),
    )


def test_check_window_with_ignore_by_selector__centered__fluent(eyes_opened):
    eyes_opened.check(
        "Fluent - Window with ignore region by selector centered",
        Target.window().ignore("#centered"),
    )
    # TODO: setExpectedIgnoreRegions(new Region(122, 928, 456, 306))


def test_check_window_with_ignore_by_selector__stretched__fluent(eyes_opened):
    eyes_opened.check(
        "Fluent - Window with ignore region by selector stretched",
        Target.region("#stretched"),
        # TODO: add analog setExpectedIgnoreRegions(new Region(8, 1270, 690, 206))
    )


def test_check_region_by_selector_after_manual_scroll__fluent(eyes_opened):
    eyes_opened.driver.execute_script("window.scrollBy(0,900)")
    eyes_opened.check(
        "Fluent - Region by selector after manual scroll", Target.region("#centered")
    )


def test_simple_region(eyes_opened):
    eyes_opened.check("Simple Region", Target.window().region(Region(50, 50, 100, 100)))


@pytest.mark.parametrize("ignore_displacements", [True, False])
def test_ignore_displacements(eyes_opened, ignore_displacements):
    eyes_opened.check(
        "Fluent - Ignore Displacements = ({})".format(ignore_displacements),
        Target.window().ignore_displacements(ignore_displacements).fully(),
    )
    # TODO: add analog addExpectedProperty("IgnoreDisplacements", ignoreDisplacements)
