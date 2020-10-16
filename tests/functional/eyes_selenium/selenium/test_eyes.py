import pytest
from selenium.webdriver.common.by import By

from applitools.common import RectangleSize, Region
from applitools.selenium import Eyes, Target


@pytest.mark.parametrize(
    "target",
    [
        Target.window()
        .scroll_root_element([By.CSS_SELECTOR, "div.pre-scrollable"])
        .layout([By.CSS_SELECTOR, "h3.section-type-TITLE"])
        .fully(),
        Target.region([By.CSS_SELECTOR, "div.pre-scrollable"])
        .layout([By.CSS_SELECTOR, "h3.section-type-TITLE"])
        .fully(),
    ],
)
def test_layout_region_calculation_for_targets(driver, fake_connector_class, target):
    eyes = Eyes()
    eyes.server_connector = fake_connector_class()
    driver = eyes.open(driver, "a", "b", RectangleSize(height=1024, width=768))
    driver.get(
        "https://applitools.github.io/demo/TestPages/"
        "SimpleTestPage/modal_scrollable.html"
    )

    eyes.check(target)
    _, match_data = eyes.server_connector.calls["match_window"]

    assert match_data.options.image_match_settings.layout_regions == [
        Region(10, 30, 533, 33)
    ]


def test_layout_region_calculation_for_frame_target(driver, fake_connector_class):
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
