import pytest

from applitools.common import (
    AccessibilityRegionType,
    FloatingBounds,
    FloatingMatchSettings,
    Region,
)
from applitools.common.geometry import AccessibilityRegion
from applitools.selenium import Eyes, Target, VisualGridRunner
from applitools.selenium.visual_grid import VisualGridEyes, dom_snapshot_script


def _retrieve_urls(data):
    return dict(
        blobs=[b["url"] for b in data.get("blobs", [])],
        resource_urls=data.get("resourceUrls", []),
    )


def test_ufg_skip_list(driver, fake_connector_class, spy):
    vg_runner = VisualGridRunner(1)
    eyes = Eyes(vg_runner)
    eyes.server_connector = fake_connector_class()
    driver.get(
        "https://applitools.github.io/demo/TestPages/"
        "VisualGridTestPageWithRelativeBGImage/index.html"
    )
    eyes.open(driver, app_name="TestUFGEyes", test_name="TestUFGSkipList")
    running_test = vg_runner._get_all_running_tests()[0]
    create_dom_snapshot_spy = spy(dom_snapshot_script, "create_dom_snapshot")
    check_spy = spy(running_test, "check")

    eyes.check_window("check 1")
    eyes.check_window("check 2")
    eyes.check_window("check 3")
    eyes.close(False)

    skip_list = create_dom_snapshot_spy.call_args.args[2]
    script_result = _retrieve_urls(check_spy.call_args.kwargs["script_result"])
    assert set(skip_list) - set(script_result["resource_urls"])


def test_disable_browser_fetching(driver, vg_runner, spy, fake_connector_class):
    eyes = Eyes(vg_runner)
    eyes.server_connector = fake_connector_class()
    driver.get("https://applitools.github.io/demo/TestPages/VisualGridTestPage")
    eyes.open(driver, "Test Visual Grid", "Test Disable Browser Fetching Config")
    get_script_result = spy(VisualGridEyes, "get_script_result")

    eyes.check(Target.window().disable_browser_fetching())

    assert get_script_result.call_args_list == [spy.call(spy.ANY, True)]
    assert len(get_script_result.return_list) == 1
    assert get_script_result.return_list[0]["blobs"] == []


@pytest.mark.parametrize(
    "target",
    [Target.window(), Target.window().disable_browser_fetching()],
)
def test_fetch_deep_css_chain(driver, vg_runner, target):
    eyes = Eyes(vg_runner)
    driver.get("https://applitools.github.io/demo/TestPages/CorsCssTestPage/")
    eyes.open(driver, "Test Visual Grid", "Test Deep CSS chain")

    eyes.check(target)

    eyes.close()
    vg_runner.get_all_test_results()


def test_coded_layout_regions_passed_to_match_window_request(
    driver, fake_connector_class, vg_runner, spy
):
    eyes = Eyes(vg_runner)
    match_window_spy = spy(fake_connector_class, "match_window")
    eyes.server_connector = fake_connector_class()
    driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage/index.html")
    eyes.open(driver, "Test Visual Grid", "Test regions are passed to render request")

    eyes.check(
        Target.window()
        .fully()
        .layout(Region(1, 2, 3, 4))
        .floating(5, Region(6, 7, 8, 9))
        .accessibility(Region(10, 11, 12, 13), AccessibilityRegionType.LargeText)
    )

    eyes.close_async()
    vg_runner.get_all_test_results()
    ims = match_window_spy.call_args.args[2].options.image_match_settings

    assert match_window_spy.call_count == 1
    assert ims.layout_regions == [Region(1, 2, 3, 4)]
    assert ims.floating_match_settings == [
        FloatingMatchSettings(Region(6, 7, 8, 9), FloatingBounds(5, 5, 5, 5))
    ]
    assert ims.accessibility == [
        AccessibilityRegion(10, 11, 12, 13, AccessibilityRegionType.LargeText)
    ]
