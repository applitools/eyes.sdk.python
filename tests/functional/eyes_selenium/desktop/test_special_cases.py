import pytest
from selenium.webdriver.common.by import By

from applitools.selenium import StitchMode, Target

pytestmark = [
    pytest.mark.platform("Linux"),
    pytest.mark.viewport_size({"width": 700, "height": 460}),
    pytest.mark.test_suite_name("Eyes Selenium SDK - Special Cases"),
    pytest.mark.test_page_url(
        "http://applitools.github.io/demo/TestPages/WixLikeTestPage/index.html"
    ),
]


def test_check_region_in_a_very_big_frame(eyes_opened):
    eyes_opened.check("map", Target.frame("frame1").region([By.TAG_NAME, "img"]))


def test_check_region_in_a_very_big_frame_after_manual_switch_to_frame(eyes_opened):
    eyes_opened.driver.switch_to.frame("frame1")

    element = eyes_opened.driver.find_element_by_tag_name("img")
    eyes_opened.driver.execute_script(
        "arguments[0].scrollIntoView(true);", element.element
    )
    eyes_opened.check("", Target.region([By.CSS_SELECTOR, "img"]))


@pytest.mark.selenium_only
@pytest.mark.test_page_url(
    "https://gistcdn.githack.com/skhalymon/048004f61ddcbf2d527daa6d6bc3b82f/raw/06cbf10fe444783445a5812691ae7f37b0db7559/MobileViewCorrect.html"
)
@pytest.mark.viewport_size({"width": 1200, "height": 700})
@pytest.mark.test_name("TestChartsWithScrollRoot")
@pytest.mark.eyes_config(branch_name="master_python")
def test_charts_with_scroll_root(eyes_opened):
    eyes_opened.configure.add_property("Fluent", False)
    driver = eyes_opened.driver
    frame1 = driver.find_element_by_id("mainFrame")
    driver.switch_to.frame(frame1)

    frame2 = driver.find_element_by_id("angularContainerIframe")
    driver.switch_to.frame(frame2)

    checked_element = driver.find_element_by_tag_name("mv-temperature-sensor-graph")
    checked_element2 = driver.find_element_by_tag_name("mv-humidity-sensor-graph")
    scroll_root = driver.find_element_by_tag_name("mat-sidenav-content")

    eyes_opened.check(
        Target.window().region(checked_element).scroll_root_element(scroll_root)
    )
    eyes_opened.check(
        Target.window().region(checked_element2).scroll_root_element(scroll_root)
    )


@pytest.mark.selenium_only
@pytest.mark.test_page_url(
    "https://gistcdn.githack.com/skhalymon/048004f61ddcbf2d527daa6d6bc3b82f/raw/06cbf10fe444783445a5812691ae7f37b0db7559/MobileViewCorrect.html"
)
@pytest.mark.viewport_size({"width": 1200, "height": 700})
@pytest.mark.test_name("TestChartsWithScrollRoot")
@pytest.mark.eyes_config(branch_name="master_python")
def test_charts_with_scroll_root_fluent(eyes_opened):
    eyes_opened.configure.add_property("Fluent", True)
    eyes_opened.check(
        Target.frame("mainFrame")
        .frame("angularContainerIframe")
        .region("mv-temperature-sensor-graph")
        .scroll_root_element("mat-sidenav-content")
    )

    eyes_opened.check(
        Target.frame("mainFrame")
        .frame("angularContainerIframe")
        .region("mv-humidity-sensor-graph")
        .scroll_root_element("mat-sidenav-content")
    )
