import time

import pytest

from applitools.core.feature import Feature
from applitools.selenium import (
    EyesWebDriver,
    EyesWebElement,
    Region,
    StitchMode,
    Target,
)
from applitools.selenium.selenium_eyes import SeleniumEyes
from tests.functional.conftest import check_image_match_settings


@pytest.mark.skip("Old test. test_hello_world implemented instead of this one")
@pytest.mark.platform("Linux")
@pytest.mark.test_page_url("https://applitools.com/helloworld")
def test_quickstart_example(eyes, driver):
    required_viewport = {"width": 1200, "height": 800}
    eyes.set_viewport_size(driver, required_viewport)
    eyes.open(
        driver=driver,
        app_name="TestQuickstartExample",
        test_name="My first Selenium Python test!",
        viewport_size={"width": 800, "height": 600},
    )

    eyes.check_window("Hello!")

    driver.find_element_by_css_selector("button").click()
    eyes.check_window("Click!")

    eyes.check_region(Region(20, 20, 50, 50), "step")

    eyes.close()


@pytest.mark.browser("chrome")
@pytest.mark.platform("Linux")
def test_directly_set_viewport_size(eyes, driver):
    required_viewport = {"width": 800, "height": 600}
    eyes.set_viewport_size(driver, required_viewport)
    driver = eyes.open(driver, "Python SDK", "TestViewPort-DirectlySetViewportt")
    assert required_viewport == eyes.get_viewport_size(driver)
    eyes.close()


@pytest.mark.browser("chrome")
@pytest.mark.platform("Linux")
@pytest.mark.eyes_config(hide_scrollbars=True)
@pytest.mark.test_page_url("http://applitools.github.io/demo/TestPages/FramesTestPage/")
def test_check_window_with_send_dom(eyes, driver):
    eyes.open(
        driver,
        "Eyes Selenium SDK - Fluent API",
        "TestCheckWindowWithSendDom",
        {"width": 800, "height": 600},
    )
    driver.find_element_by_tag_name("input").send_keys("My Input")
    eyes.check(
        "Fluent - Window with Ignore region",
        Target.window().send_dom().use_dom().ignore_caret(),
    )
    assert "data-applitools-scroll" in driver.page_source
    assert "data-applitools-original-overflow" in driver.page_source
    eyes.close()


@pytest.mark.test_page_url("data:text/html,<p>Test</p>")
def test_abort_eyes(eyes, driver):
    eyes.open(driver, "Test Abort", "Test Abort", {"width": 1200, "height": 800})
    eyes.check("SEL", Target.window())
    time.sleep(15)
    eyes.abort()


@pytest.mark.platform("Linux")
@pytest.mark.test_page_url("https://applitools.com/helloworld")
@pytest.mark.eyes_config(branch_name="master_python")
def test_coordinates_resolving(eyes, driver):
    driver = eyes.open(
        driver,
        "Python Selenium",
        "TestCoordinatesResolving",
        {"width": 800, "height": 600},
    )
    element = driver.find_element_by_css_selector("button")
    left = element.location["x"]
    top = element.location["y"]
    width = element.size["width"]
    height = element.size["height"]

    eyes.check("web element", Target.region(element))
    eyes.check("coordinates", Target.region(Region(left, top, width, height)))

    eyes.close()


@pytest.mark.parametrize(
    "eyes",
    [
        {"force_full_page_screenshot": True, "stitch_mode": StitchMode.CSS},
        {"force_full_page_screenshot": False, "stitch_mode": StitchMode.CSS},
        {"force_full_page_screenshot": True, "stitch_mode": StitchMode.Scroll},
        {"force_full_page_screenshot": False, "stitch_mode": StitchMode.Scroll},
    ],
    indirect=True,
    ids=lambda o: "CSS" if o["stitch_mode"] == StitchMode.CSS else "Scroll",
)
@pytest.mark.platform("Windows")
@pytest.mark.browser("internet explorer")
@pytest.mark.test_page_url("http://applitools.github.io/demo/TestPages/FramesTestPage")
def test_ie_viewport_screenshot_with_scrolling(eyes, driver):
    test_name = "TestIEViewportScreenshot"
    if eyes.force_full_page_screenshot:
        test_name += "_FPS"
    test_name += "_%s" % eyes.stitch_mode.value
    eyes.open(driver, "Python SDK", test_name)

    eyes.check_window()

    driver.execute_script(
        "arguments[0].scrollIntoView();",
        driver.find_element_by_id("overflowing-div-image"),
    )
    eyes.check_window()
    eyes.close()


@pytest.mark.test_page_url("http://applitools.github.io/demo/TestPages/FramesTestPage/")
@pytest.mark.eyes_config(parent_branch_name="master", branch_name="master_python")
def test_switch_back_to_frame_after_check(eyes, driver):
    eyes_driver = eyes.open(
        driver,
        "Python Selenium",
        "TestSwitchBackToFrameAfterCheck",
        {"width": 800, "height": 600},
    )

    # switch driver context to frame
    frame = driver.find_element_by_css_selector("body > iframe")
    eyes_driver.switch_to.frame(frame)

    # locate element inside the frame - succeed
    eyes_driver.find_element_by_css_selector("#inner-frame-div")

    # take screenshot
    eyes.check("step name", Target.window())

    # locate the same element inside the frame - failed
    eyes_driver.find_element_by_css_selector("#inner-frame-div")
    eyes.close()


@pytest.mark.platform("Linux")
@pytest.mark.browser("chrome")
def test_execute_script_with_eyes_webelement(driver, eyes):
    elem = driver.find_element_by_tag_name("html")
    e_elem = EyesWebElement(elem, driver)
    driver.execute_script("arguments[0].scrollIntoView();", elem)

    eyes_driver = EyesWebDriver(driver, eyes)
    eyes_driver.execute_script("arguments[0].scrollIntoView();", elem)
    eyes_driver.execute_script("arguments[0].scrollIntoView();", e_elem)


@pytest.mark.parametrize(
    "params",
    [
        (
            "https://applitools.github.io/demo/TestPages/SpecialCases/everchanging.html",
            [False, True],
        ),
        (
            "https://applitools.github.io/demo/TestPages/SpecialCases/neverchanging.html",
            [False],
        ),
        (
            "https://applitools.github.io/demo/TestPages/SimpleTestPage/index.html",
            [False],
        ),
    ],
)
def test_replace_matched_step(params, driver, eyes, fake_connector_class):
    test_url, replace_last_expected = params
    driver.get(test_url)
    eyes.server_connector = fake_connector_class()
    eyes.open(
        driver,
        "Applitools Eyes SDK",
        "testReplaceMatchedStep",
        {"width": 700, "height": 460},
    )
    eyes.check_window("Step 1")
    eyes.close(False)
    match_data_results = eyes.server_connector.input_calls["match_window"]
    for match_data_result, expected in zip(match_data_results, replace_last_expected):
        _, match_data = match_data_result
        assert match_data.options.replace_last == expected


def test_screenshot_too_big(driver, eyes, fake_connector_class):
    eyes.server_connector = fake_connector_class()
    driver = eyes.open(
        driver,
        "Applitools Eyes SDK",
        "Test Screenshot Too Big",
        {"width": 800, "height": 800},
    )
    r_info = eyes.server_connector.render_info()
    eyes.save_debug_screenshots = True
    screenshots = []
    eyes._selenium_eyes._debug_screenshots_provider.save = (
        lambda image, suffix: screenshots.append(image)
    )
    driver.get("https://applitools.github.io/demo/TestPages/FramesTestPage/")
    driver.find_element_by_id("stretched").click()
    frame = driver.find_element_by_css_selector("#modal2 iframe")
    driver.switch_to.frame(frame)
    element = driver.find_element_by_tag_name("html")
    eyes.check("Step 1", Target.region(element).fully())
    eyes.close(False)

    image = screenshots[-1]
    assert r_info.max_image_height == image.height


def test_feature_target_window_captures_selected_frame(eyes, driver):
    driver.get("http://applitools.github.io/demo/TestPages/FramesTestPage/")
    eyes.configure.set_features(Feature.TARGET_WINDOW_CAPTURES_SELECTED_FRAME)
    eyes_driver = eyes.open(
        driver=driver,
        app_name="Applitools Eyes SDK",
        test_name="Target window captures selected frame feature",
        viewport_size={"width": 800, "height": 600},
    )
    frame = eyes_driver.find_element_by_css_selector("body > iframe")
    eyes_driver.switch_to.frame(frame)

    eyes.check("step name", Target.window())
    eyes.close()


def test_capture_element_on_pre_scrolled_down_page(eyes, driver):
    driver.get(
        "http://applitools.github.io/demo/TestPages/FramesTestPage/longframe.html"
    )
    eyes.open(
        driver=driver,
        app_name="Applitools Eyes SDK",
        test_name="Test capture element on pre scrolled down page",
        viewport_size={"width": 800, "height": 600},
    )
    driver.execute_script("window.scrollTo(0, 300)")
    eyes.check("Row 10", Target.region("body > table > tr:nth-child(10)"))
    eyes.check("Row 20", Target.region("body > table > tr:nth-child(20)"))
    eyes.close()


def test_charts_with_scroll_root(eyes, driver):
    driver.get(
        "https://gistcdn.githack.com/skhalymon/048004f61ddcbf2d527daa6d6bc3b82f/raw/06cbf10fe444783445a5812691ae7f37b0db7559/MobileViewCorrect.html"
    )
    eyes_driver = eyes.open(
        driver=driver,
        app_name="Applitools Eyes SDK",
        test_name="TestChartsWithScrollRoot",
        viewport_size={"width": 1200, "height": 700},
    )
    eyes.configure.branch_name = "master_python"

    frame1 = eyes_driver.find_element_by_id("mainFrame")
    eyes_driver.switch_to.frame(frame1)

    frame2 = eyes_driver.find_element_by_id("angularContainerIframe")
    eyes_driver.switch_to.frame(frame2)

    checked_element = driver.find_element_by_tag_name("mv-temperature-sensor-graph")
    checked_element2 = driver.find_element_by_tag_name("mv-humidity-sensor-graph")
    scroll_root = driver.find_element_by_tag_name("mat-sidenav-content")

    eyes.check(Target.window().region(checked_element).scroll_root_element(scroll_root))
    eyes.check(
        Target.window().region(checked_element2).scroll_root_element(scroll_root)
    )
    eyes.close()


def test_charts_with_scroll_root_fluent(eyes, driver):
    driver.get(
        "https://gistcdn.githack.com/skhalymon/048004f61ddcbf2d527daa6d6bc3b82f/raw/06cbf10fe444783445a5812691ae7f37b0db7559/MobileViewCorrect.html"
    )
    eyes.open(
        driver=driver,
        app_name="Applitools Eyes SDK",
        test_name="TestChartsWithScrollRoot",
        viewport_size={"width": 1200, "height": 700},
    )
    eyes.configure.branch_name = "master_python"
    eyes.check(
        Target.frame("mainFrame")
        .frame("angularContainerIframe")
        .region("mv-temperature-sensor-graph")
        .scroll_root_element("mat-sidenav-content")
    )

    eyes.check(
        Target.frame("mainFrame")
        .frame("angularContainerIframe")
        .region("mv-humidity-sensor-graph")
        .scroll_root_element("mat-sidenav-content")
    )
    eyes.close()


def test_check_window_with_match_region_paddings__fluent(eyes, driver):
    driver.get("http://applitools.github.io/demo/TestPages/FramesTestPage/")
    eyes_driver = eyes.open(
        driver=driver,
        app_name="Applitools Eyes SDK",
        test_name="TestCheckWindowWithMatchRegionPaddings_Fluent",
        viewport_size={"width": 1200, "height": 700},
    )
    eyes.configure.branch_name = "master_python"

    eyes.check(
        "Fluent - Window with ignore region by selector stretched",
        Target.window()
        .fully()
        .ignore(".ignore", padding=dict(left=10))
        .content("#stretched", padding=dict(top=10))
        .layout("#centered", padding=dict(top=10, right=50))
        .strict("overflowing-div", padding=dict(bottom=100)),
    )
    # regions are different for latest UFG chrome vs classic chrome
    if isinstance(eyes._current_eyes, SeleniumEyes):
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
    test_result = eyes.close(False)
    check_image_match_settings(
        eyes,
        test_result,
        [
            {
                "actual_name": "ignore",
                "expected": expected_regions,
            }
        ],
    )
