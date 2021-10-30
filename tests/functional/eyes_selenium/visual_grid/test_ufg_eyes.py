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


@pytest.mark.skip("Skip list temporary disabled. Trello 2363")
@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/"
    "VisualGridTestPageWithRelativeBGImage/index.html"
)
def test_ufg_skip_list(chrome_driver, fake_connector_class, spy):
    vg_runner = VisualGridRunner(1)
    eyes = Eyes(vg_runner)
    eyes.server_connector = fake_connector_class()
    eyes.open(chrome_driver, app_name="TestUFGEyes", test_name="TestUFGSkipList")
    create_dom_snapshot_spy = spy(dom_snapshot_script, "create_dom_snapshot")
    rc_task_factory_spy = spy(VisualGridEyes, "_resource_collection_task")

    eyes.check_window("check 1")
    eyes.check_window("check 2")
    eyes.check_window("check 3")
    eyes.close(False)

    skip_list = create_dom_snapshot_spy.call_args.args[2]
    script_result = _retrieve_urls(rc_task_factory_spy.call_args.args[4])
    assert set(skip_list) - set(script_result["resource_urls"])


@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/VisualGridTestPage"
)
def test_disable_browser_fetching(chrome_driver, vg_runner, spy, fake_connector_class):
    eyes = Eyes(vg_runner)
    eyes.server_connector = fake_connector_class()
    eyes.open(chrome_driver, "Test Visual Grid", "Test Disable Browser Fetching Config")
    get_script_result = spy(VisualGridEyes, "get_script_result")

    eyes.check(Target.window().disable_browser_fetching())

    assert get_script_result.call_args_list == [spy.call(spy.ANY, True)]
    assert len(get_script_result.return_list) == 1
    assert get_script_result.return_list[0]["blobs"] == []


@pytest.mark.parametrize(
    "target",
    [Target.window(), Target.window().disable_browser_fetching()],
)
@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/CorsCssTestPage/"
)
def test_fetch_deep_css_chain(chrome_driver, vg_runner, target):
    eyes = Eyes(vg_runner)
    eyes.open(chrome_driver, "Test Visual Grid", "Test Deep CSS chain")

    eyes.check(target)

    eyes.close()
    vg_runner.get_all_test_results()


@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/SimpleTestPage/index.html"
)
def test_coded_layout_regions_passed_to_match_window_request(
    chrome_driver, fake_connector_class, vg_runner, spy
):
    eyes = Eyes(vg_runner)
    eyes.server_connector = fake_connector_class()
    eyes.open(
        chrome_driver, "Test Visual Grid", "Test regions are passed to render request"
    )

    eyes.check(
        Target.window()
        .fully()
        .layout(Region(1, 2, 3, 4))
        .floating(5, Region(6, 7, 8, 9))
        .accessibility(Region(10, 11, 12, 13), AccessibilityRegionType.LargeText)
    )

    eyes.close_async()
    server_connector = vg_runner._get_all_running_tests()[0].eyes.server_connector
    vg_runner.get_all_test_results(False)
    _, match_data = server_connector.input_calls["match_window"][0]
    ims = match_data.options.image_match_settings

    assert len(server_connector.input_calls["match_window"]) == 1
    assert ims.layout_regions == [Region(1, 2, 3, 4)]
    assert ims.floating_match_settings == [
        FloatingMatchSettings(Region(6, 7, 8, 9), FloatingBounds(5, 5, 5, 5))
    ]
    assert ims.accessibility == [
        AccessibilityRegion(10, 11, 12, 13, AccessibilityRegionType.LargeText)
    ]


@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/CookiesTestPage/"
)
def test_cookies_passed_to_download_resource_request(
    chrome_driver, fake_connector_class, spy
):
    vg_runner = VisualGridRunner(1)
    eyes = Eyes(vg_runner)
    eyes.server_connector = fake_connector_class()
    download_resource_spy = spy(eyes.server_connector, "download_resource")
    eyes.open(
        chrome_driver,
        app_name="Visual Grid Render Test",
        test_name="TestRenderResourceNotFound",
    )

    eyes.check(Target.window().disable_browser_fetching())
    eyes.close(False)
    vg_runner.get_all_test_results(False)

    download_resource_spy.call_args_list.sort(key=lambda a: (a.args[0], len(a.args[1])))
    assert download_resource_spy.call_args_list == [
        spy.call(
            # otherdir don't have subdir cookie
            "http://applitools.github.io/demo/TestPages/CookiesTestPage/"
            "otherdir/cookie.png",
            [
                {
                    "domain": "applitools.github.io",
                    "httpOnly": False,
                    "name": "frame1",
                    "path": "/demo/TestPages/CookiesTestPage",
                    "secure": False,
                    "value": "1",
                },
                {
                    "domain": "applitools.github.io",
                    "httpOnly": False,
                    "name": "index",
                    "path": "/demo/TestPages/CookiesTestPage",
                    "secure": False,
                    "value": "1",
                },
            ],
        ),
        # subdir has all the cookies
        spy.call(
            "http://applitools.github.io/demo/TestPages/CookiesTestPage/"
            "subdir/cookie.png",
            [
                {
                    "domain": "applitools.github.io",
                    "httpOnly": False,
                    "name": "frame1",
                    "path": "/demo/TestPages/CookiesTestPage",
                    "secure": False,
                    "value": "1",
                },
                {
                    "domain": "applitools.github.io",
                    "httpOnly": False,
                    "name": "index",
                    "path": "/demo/TestPages/CookiesTestPage",
                    "secure": False,
                    "value": "1",
                },
                {
                    "domain": "applitools.github.io",
                    "httpOnly": False,
                    "name": "frame2",
                    "path": "/demo/TestPages/CookiesTestPage/subdir",
                    "secure": False,
                    "value": "1",
                },
            ],
        ),
        # outside resources have no cookies
        spy.call("http://applitools.github.io/demo/images/image_1.jpg", []),
        spy.call("https://demo.applitools.com/img/logo-big.png", []),
    ]


@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/CookiesTestPage/"
)
def test_cookies_are_not_passed_when_disabled(chrome_driver, fake_connector_class, spy):
    vg_runner = VisualGridRunner(1)
    eyes = Eyes(vg_runner)
    eyes.configure.set_dont_use_cookies(True)
    eyes.server_connector = fake_connector_class()
    download_resource_spy = spy(eyes.server_connector, "download_resource")
    eyes.open(
        chrome_driver,
        app_name="Visual Grid Render Test",
        test_name="TestRenderResourceNotFound",
    )

    eyes.check(Target.window().disable_browser_fetching())
    eyes.close(False)
    vg_runner.get_all_test_results(False)

    download_resource_spy.call_args_list.sort(key=lambda a: (a.args[0], len(a.args[1])))
    assert download_resource_spy.call_args_list == [
        spy.call(
            "http://applitools.github.io/demo/TestPages/CookiesTestPage/"
            "otherdir/cookie.png",
            [],
        ),
        spy.call(
            "http://applitools.github.io/demo/TestPages/CookiesTestPage/"
            "subdir/cookie.png",
            [],
        ),
        spy.call("http://applitools.github.io/demo/images/image_1.jpg", []),
        spy.call("https://demo.applitools.com/img/logo-big.png", []),
    ]
