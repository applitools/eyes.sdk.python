from time import sleep

import pytest
from selenium.webdriver.common.by import By

from applitools.common import RectangleSize, Region
from applitools.selenium import Eyes, Target, VisualGridRunner, eyes_selenium_utils
from applitools.selenium.visual_grid import visual_grid_eyes


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
            Region(9, 30, 533, 33),
        ),
    ],
)
@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/SimpleTestPage/modal_scrollable.html"
)
def test_layout_region_calculation_for_targets(
    chrome_driver, fake_connector_class, target, expected_layout_region
):
    eyes = Eyes()
    eyes.send_dom = False
    eyes.server_connector = fake_connector_class()
    driver = eyes.open(chrome_driver, "a", "b", RectangleSize(height=1024, width=768))

    eyes.check(target)
    _, match_data = eyes.server_connector.calls["match_window"]

    assert match_data.options.image_match_settings.layout_regions == [
        expected_layout_region
    ]


@pytest.mark.skip("Known bug, Trello#1644")
@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/CorsTestPage/index.html"
)
def test_layout_region_calculation_for_frame_target(
    chrome_driver, fake_connector_class
):
    eyes = Eyes()
    eyes.server_connector = fake_connector_class()
    driver = eyes.open(chrome_driver, "a", "b", RectangleSize(height=1024, width=768))

    eyes.check(
        Target.frame([By.CSS_SELECTOR, "body>iframe"]).layout(
            [By.ID, "inner-frame-div"]
        )
    )
    _, match_data = eyes.server_connector.calls["match_window"]

    assert match_data.options.image_match_settings.layout_regions == [
        Region(8, 8, 304, 184)
    ]


@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/CorsTestPage/index.html"
)
def test_layout_region_calculation_for_frame_fully_target(
    chrome_driver, fake_connector_class
):
    eyes = Eyes()
    eyes.server_connector = fake_connector_class()
    eyes.open(chrome_driver, "a", "b", RectangleSize(height=1024, width=768))

    eyes.check(
        Target.frame([By.CSS_SELECTOR, "body>iframe"])
        .layout([By.ID, "inner-frame-div"])
        .fully()
    )
    _, match_data = eyes.server_connector.calls["match_window"]

    assert match_data.options.image_match_settings.layout_regions == [
        Region(8, 8, 304, 184)
    ]


def test_agent_run_id(fake_connector_class, driver_mock, monkeypatch, spy):
    monkeypatch.setattr(eyes_selenium_utils, "set_viewport_size", lambda *_: None)
    random_alphanum_spy = spy(visual_grid_eyes, "random_alphanum")
    eyes = Eyes(VisualGridRunner(1))
    eyes.server_connector = fake_connector_class()

    eyes.open(driver_mock, "A", "B", {"width": 100, "height": 100})
    eyes.abort_async()
    while "start_session" not in eyes.server_connector.calls:
        sleep(1)  # wait until runner opens session in background thread
    assert (
        eyes.server_connector.calls["start_session"].agent_run_id
        == "B_" + random_alphanum_spy.return_list[0]
    )


@pytest.mark.test_page_url("https://applitools.github.io/demo/TestPages/ModalsPage")
def test_scrollable_modal_on_scrolled_down_page(chrome_driver):
    eyes = Eyes()
    driver = eyes.open(
        chrome_driver,
        "TestModal",
        "ScrollableModalOnScrolledDownPage",
        RectangleSize(width=1024, height=768),
    )
    # Scroll page to the bottom-most paragraph
    driver.execute_script(
        "arguments[0].scrollIntoView()",
        driver.find_element_by_css_selector("body > main > p:nth-child(17)"),
    )
    # Show popup without clicking a button on top to avoid scrolling up
    driver.execute_script("openModal('scrollable_content_modal')")

    content = driver.find_element_by_css_selector(
        ".modal-content.modal-content--scrollable"
    )
    eyes.check(Target.region(content).scroll_root_element(content).fully())

    eyes.close()


@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/CorsTestPage/index.html"
)
def test_layout_region_calculation_within_frame(chrome_driver, fake_connector_class):
    eyes = Eyes()
    eyes.server_connector = fake_connector_class()
    eyes.open(chrome_driver, "a", "b", RectangleSize(width=1024, height=768))

    eyes.check(Target.frame("frame1").region("body").layout("#inner-frame-div"))

    _, match_data = eyes.server_connector.calls["match_window"]
    assert match_data.options.image_match_settings.layout_regions == [
        Region(0, 0, 304, 184)
    ]
