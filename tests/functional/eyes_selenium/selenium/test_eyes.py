import pytest
from selenium.webdriver.common.by import By

from applitools.common import Point, RectangleSize, Region
from applitools.selenium import Eyes, Target


@pytest.mark.parametrize(
    "target, expected_layout_region",
    [
        (
            Target.window()
            .scroll_root_element([By.CSS_SELECTOR, "div.pre-scrollable"])
            .layout([By.CSS_SELECTOR, "h3.section-type-TITLE"]),
            Region(102, 137, 533, 33),
        ),
        (
            Target.window()
            .scroll_root_element([By.CSS_SELECTOR, "div.pre-scrollable"])
            .layout([By.CSS_SELECTOR, "h3.section-type-TITLE"])
            .fully(),
            Region(10, 30, 533, 33),
        ),
        (
            Target.region([By.CSS_SELECTOR, "div.pre-scrollable"]).layout(
                [By.CSS_SELECTOR, "h3.section-type-TITLE"]
            ),
            Region(9, 30, 533, 33),
        ),
        (
            Target.region([By.CSS_SELECTOR, "div.pre-scrollable"])
            .layout([By.CSS_SELECTOR, "h3.section-type-TITLE"])
            .fully(),
            Region(10, 30, 533, 33),
        ),
    ],
)
def test_layout_region_calculation_for_targets(
    driver, fake_connector_class, target, expected_layout_region
):
    eyes = Eyes()
    eyes.send_dom = False
    eyes.server_connector = fake_connector_class()
    driver = eyes.open(driver, "a", "b", RectangleSize(height=1024, width=768))
    driver.get(
        "https://applitools.github.io/demo/TestPages/"
        "SimpleTestPage/modal_scrollable.html"
    )

    eyes.check(target)
    _, match_data = eyes.server_connector.calls["match_window"]

    assert match_data.options.image_match_settings.layout_regions == [
        expected_layout_region
    ]


@pytest.mark.skip("Known bug, Trello#1644")
def test_layout_region_calculation_for_frame_target(driver, fake_connector_class):
    eyes = Eyes()
    eyes.server_connector = fake_connector_class()
    driver = eyes.open(driver, "a", "b", RectangleSize(height=1024, width=768))
    driver.get("https://applitools.github.io/demo/TestPages/CorsTestPage/index.html")

    eyes.check(
        Target.frame([By.CSS_SELECTOR, "body>iframe"]).layout(
            [By.ID, "inner-frame-div"]
        )
    )
    _, match_data = eyes.server_connector.calls["match_window"]

    assert match_data.options.image_match_settings.layout_regions == [
        Region(8, 8, 304, 184)
    ]


def test_layout_region_calculation_for_frame_fully_target(driver, fake_connector_class):
    eyes = Eyes()
    eyes.server_connector = fake_connector_class()
    driver = eyes.open(driver, "a", "b", RectangleSize(height=1024, width=768))
    driver.get("https://applitools.github.io/demo/TestPages/CorsTestPage/index.html")

    eyes.check(
        Target.frame([By.CSS_SELECTOR, "body>iframe"])
        .layout([By.ID, "inner-frame-div"])
        .fully()
    )
    _, match_data = eyes.server_connector.calls["match_window"]

    assert match_data.options.image_match_settings.layout_regions == [
        Region(8, 8, 304, 184)
    ]


def test_match_window_fully_screenshot_location(driver, fake_connector_class):
    eyes = Eyes()
    eyes.server_connector = fake_connector_class()
    driver = eyes.open(driver, "a", "b", RectangleSize(height=600, width=800))
    driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage/index.html")

    eyes.check(Target.window().fully())
    _, match_data = eyes.server_connector.calls["match_window"]

    assert match_data.app_output.location == Point(0, 0)


def test_match_window_scrolled_screenshot_location(driver, fake_connector_class):
    eyes = Eyes()
    eyes.server_connector = fake_connector_class()
    driver = eyes.open(driver, "a", "b", RectangleSize(height=600, width=800))
    driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage/index.html")
    driver.execute_script("window.scrollBy(0,1000)")

    eyes.check(Target.window())
    _, match_data = eyes.server_connector.calls["match_window"]

    assert match_data.app_output.location == Point(0, 1000)


def test_match_region_screenshot_location(driver, fake_connector_class):
    eyes = Eyes()
    eyes.server_connector = fake_connector_class()
    driver = eyes.open(driver, "a", "b", RectangleSize(height=600, width=800))
    driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage/index.html")

    eyes.check(Target.region("#overflowing-div > img:nth-child(32)"))
    _, match_data = eyes.server_connector.calls["match_window"]

    assert match_data.app_output.location == Point(8, 2100)


def test_match_frame_fully_location(driver, fake_connector_class):
    eyes = Eyes()
    eyes.server_connector = fake_connector_class()
    driver = eyes.open(driver, "a", "b", RectangleSize(height=600, width=800))
    driver.get("http://applitools.github.io/demo/TestPages/FramesTestPage/")

    eyes.check(Target.frame(0).fully())
    _, match_data = eyes.server_connector.calls["match_window"]

    assert match_data.app_output.location == Point(0, 0)


def test_match_frame_location(driver, fake_connector_class):
    eyes = Eyes()
    eyes.server_connector = fake_connector_class()
    driver = eyes.open(driver, "a", "b", RectangleSize(height=600, width=800))
    driver.get("http://applitools.github.io/demo/TestPages/FramesTestPage/")

    eyes.check(Target.frame(0))
    _, match_data = eyes.server_connector.calls["match_window"]

    assert match_data.app_output.location == Point(58, 506)


def test_match_frame_region_location(driver, fake_connector_class):
    eyes = Eyes()
    eyes.server_connector = fake_connector_class()
    driver = eyes.open(driver, "a", "b", RectangleSize(height=600, width=800))
    driver.get("http://applitools.github.io/demo/TestPages/FramesTestPage/")

    eyes.check(Target.frame(0).region("#inner-frame-div"))
    _, match_data = eyes.server_connector.calls["match_window"]

    assert match_data.app_output.location == Point(8, 8)


def test_match_context_frame_window_fully_location(driver, fake_connector_class):
    eyes = Eyes()
    eyes.server_connector = fake_connector_class()
    driver = eyes.open(driver, "a", "b", RectangleSize(height=600, width=800))
    driver.get("http://applitools.github.io/demo/TestPages/FramesTestPage/")

    driver.switch_to.frame(0)
    eyes.check(Target.window().fully())
    _, match_data = eyes.server_connector.calls["match_window"]

    assert match_data.app_output.location == Point(0, 0)


def test_match_context_frame_region_location(driver, fake_connector_class):
    eyes = Eyes()
    eyes.server_connector = fake_connector_class()
    driver = eyes.open(driver, "a", "b", RectangleSize(height=600, width=800))
    driver.get("http://applitools.github.io/demo/TestPages/FramesTestPage/")

    driver.switch_to.frame(0)
    eyes.check(Target.region("#inner-frame-div"))
    _, match_data = eyes.server_connector.calls["match_window"]

    assert match_data.app_output.location == Point(8, 8)
