import time
from collections import defaultdict

import pytest

from applitools.common import ChromeEmulationInfo
from applitools.selenium import (
    BrowserType,
    Configuration,
    DeviceName,
    Eyes,
    IosDeviceInfo,
    IosDeviceName,
    IosVersion,
    MatchLevel,
    RectangleSize,
    ScreenOrientation,
    StitchMode,
    Target,
    VisualGridRunner,
    logger,
)
from tests.utils import get_session_results


def test_mobile_only(driver, batch_info):
    runner = VisualGridRunner(30)
    eyes = Eyes(runner)

    sconf = Configuration()
    sconf.test_name = "Mobile Render Test"
    sconf.app_name = "Visual Grid Render Test"
    sconf.batch = batch_info

    sconf.add_device_emulation(DeviceName.Galaxy_S5)

    eyes.set_configuration(sconf)
    eyes.open(driver)
    driver.get(
        "https://applitools.github.io/demo/TestPages/DynamicResolution/mobile.html"
    )
    eyes.check("Test Mobile Only", Target.window().fully())
    eyes.close()
    all_results = runner.get_all_test_results()


@pytest.mark.skip
def test_viewports_test(driver, batch_info):
    runner = VisualGridRunner(30)
    eyes = Eyes(runner)

    sconf = Configuration()
    sconf.batch = batch_info
    sconf.test_name = "Viewport Size Test"
    sconf.app_name = "Visual Grid Viewports Test"
    sconf.hide_scrollbars = True
    sconf.stitch_mode = StitchMode.CSS
    sconf.force_full_page_screenshot = True
    sconf.match_level = MatchLevel.STRICT

    sconf.add_browser(800, 600, BrowserType.CHROME)
    sconf.add_browser(700, 500, BrowserType.CHROME)
    sconf.add_browser(1200, 800, BrowserType.CHROME)
    sconf.add_browser(1600, 1200, BrowserType.CHROME)
    sconf.add_browser(800, 600, BrowserType.FIREFOX)
    sconf.add_browser(700, 500, BrowserType.FIREFOX)
    sconf.add_browser(1200, 800, BrowserType.FIREFOX)
    sconf.add_browser(1600, 1200, BrowserType.FIREFOX)
    sconf.add_browser(800, 600, BrowserType.EDGE)
    sconf.add_browser(700, 500, BrowserType.EDGE)
    sconf.add_browser(1200, 800, BrowserType.EDGE)
    # sconf.add_browser(1600, 1200, BrowserType.EDGE)
    sconf.add_browser(800, 600, BrowserType.IE_11)
    sconf.add_browser(700, 500, BrowserType.IE_11)
    sconf.add_browser(1200, 800, BrowserType.IE_11)
    # sconf.add_browser(1600, 1200, BrowserType.IE_11)
    sconf.add_browser(800, 600, BrowserType.IE_10)
    sconf.add_browser(700, 500, BrowserType.IE_10)
    sconf.add_browser(1200, 800, BrowserType.IE_10)
    # sconf.add_browser(1600, 1200, BrowserType.IE_10)
    eyes.set_configuration(sconf)

    eyes.open(driver)
    driver.get("https://www.applitools.com")
    eyes.check("Test Viewport", Target.window().fully())
    eyes.close_async()

    all_results = runner.get_all_test_results(False)
    assert len(sconf.browsers_info) > len(BrowserType)
    assert len(all_results) == len(sconf.browsers_info)

    results = defaultdict(set)
    for trc in all_results:
        assert trc
        session_results = None
        try:
            session_results = get_session_results(eyes.api_key, trc.test_results)
        except Exception as e:
            logger.exception(e)

        if session_results is None:
            logger.debug("Error: session_results is null for item {}".format(trc))
            continue

        env = session_results["env"]
        browser = env["hostingAppInfo"]
        if browser is None:
            logger.debug("Error: HostingAppInfo (browser) is null. {}".format(trc))
            continue

        sizes_list = results[browser]
        display_size = RectangleSize.from_(env["displaySize"])
        if display_size in sizes_list:
            assert (
                False
            ), "Browser {} viewport size {} already exists in results.".format(
                browser, display_size
            )
        sizes_list.add(display_size)
    assert len(results) == 5


@pytest.mark.parametrize(
    "url,test_name",
    [
        (
            "https://applitools.github.io/demo/TestPages/DomTest/shadow_dom.html",
            "Shadow DOM Test",
        ),
        (
            "https://applitools.github.io/demo/TestPages/VisualGridTestPage/canvastest.html",
            "Canvas Test",
        ),
    ],
)
def test_special_rendering(url, test_name, batch_info, driver):
    runner = VisualGridRunner(30)
    eyes = Eyes(runner)
    sconf = Configuration(
        test_name=test_name, app_name="Visual Grid Render Test", batch=batch_info
    )
    sconf.add_device_emulation(DeviceName.Galaxy_S5)
    sconf.add_browser(1200, 800, BrowserType.CHROME)
    sconf.add_browser(1200, 800, BrowserType.FIREFOX)

    eyes.set_configuration(sconf)
    eyes.open(driver)
    driver.get(url)
    time.sleep(0.5)
    eyes.check(test_name, Target.window().fully())
    eyes.close_async()
    all_results = runner.get_all_test_results()


@pytest.mark.skip("Page is missing")
def test_svg_parsing(driver, eyes, batch_info, vg_runner):
    driver.get("https://danielschwartz85.github.io/static-test-page2/index.html")
    eyes = Eyes(vg_runner)
    eyes.set_configuration(
        Configuration(
            test_name="TestSvgParsing",
            app_name="Visual Grid Render Test",
            batch=batch_info,
        ).add_browser(1200, 800, BrowserType.CHROME)
    )
    eyes.open(driver)
    eyes.check_window()
    eyes.close_async()
    all_results = vg_runner.get_all_test_results()


def test_css_relative_url_on_another_domain(driver, batch_info, vg_runner):
    driver.get(
        "https://applitools.github.io/demo/TestPages/VisualGridTestPageWithRelativeBGImage/index.html"
    )
    eyes = Eyes(vg_runner)
    eyes.set_configuration(
        Configuration(
            test_name="TestCssRelativeUrlOnAnotherDomain",
            app_name="Visual Grid Render Test",
            batch=batch_info,
        )
        .add_browser(1200, 800, BrowserType.CHROME)
        .add_browser(700, 600, BrowserType.FIREFOX)
        .add_browser(1200, 600, BrowserType.FIREFOX)
        .add_browser(1200, 600, BrowserType.EDGE)
        .add_browser(1200, 600, BrowserType.IE_11)
        .add_browser(1200, 600, BrowserType.IE_10)
        .add_device_emulation(DeviceName.iPhone_X, ScreenOrientation.PORTRAIT)
        .add_device_emulation(DeviceName.Nexus_10, ScreenOrientation.LANDSCAPE)
        .add_device_emulation(DeviceName.iPad)
    )
    eyes.open(driver)
    eyes.check_window()
    eyes.close_async()
    all_results = vg_runner.get_all_test_results(False)
    assert len(all_results) == 9


def test_mobile_web_happy_flow(driver, batch_info, vg_runner):
    driver.get("https://applitools.github.io/demo")
    eyes = Eyes(vg_runner)
    eyes.set_configuration(
        Configuration(
            app_name="Eyes SDK",
            test_name="UFG Mobile Web Happy Flow",
            batch=batch_info,
        ).add_browser(
            IosDeviceInfo(IosDeviceName.iPhone_12, ScreenOrientation.LANDSCAPE)
        )
    )
    eyes.open(driver, viewport_size=RectangleSize(800, 600))
    eyes.check_window()
    eyes.close()


def test_rendering_ios_simulator(driver, batch_info, vg_runner):
    driver.get("http://applitools.github.io/demo")
    eyes = Eyes(vg_runner)
    eyes.set_configuration(
        Configuration(
            app_name="Eyes SDK",
            test_name="UFG Mobile Web Happy Flow",
            batch=batch_info,
        )
        .add_browser(
            IosDeviceInfo(IosDeviceName.iPhone_XR, ScreenOrientation.LANDSCAPE)
        )
        .add_browser(
            IosDeviceInfo(IosDeviceName.iPhone_XR, ios_version=IosVersion.LATEST)
        )
        .add_browser(
            IosDeviceInfo(
                IosDeviceName.iPhone_XR, ios_version=IosVersion.ONE_VERSION_BACK
            )
        )
        .set_save_diffs(False)
        .set_save_new_tests(False)
    )
    eyes.open(driver, viewport_size=RectangleSize(800, 600))
    eyes.check_window()
    eyes.close_async()
    assert len(vg_runner.get_all_test_results()) == 3


def test_explicit_layout_breakpoints(driver, batch_info, vg_runner):
    driver.get("https://applitools.github.io/demo/TestPages/JsLayout")
    eyes = Eyes(vg_runner)
    eyes.set_configuration(
        Configuration(
            app_name="Eyes SDK",
            test_name="UFG Layout Breakpoints explicit test",
            batch=batch_info,
        )
        .add_browser(500, 400, BrowserType.CHROME)
        .add_browser(800, 400, BrowserType.CHROME)
        .add_browser(800, 600, BrowserType.CHROME)
        .add_browser(1024, 768, BrowserType.CHROME)
        .add_browser(1200, 800, BrowserType.CHROME)
        .set_layout_breakpoints(500, 1000)
    )
    eyes.open(driver, viewport_size=RectangleSize(800, 600))
    eyes.check_window()
    eyes.close()


def test_inferred_layout_breakpoints(driver, batch_info, vg_runner):
    driver.get("https://applitools.github.io/demo/TestPages/JsLayout")
    eyes = Eyes(vg_runner)
    eyes.set_configuration(
        Configuration(
            app_name="Eyes SDK",
            test_name="UFG Layout Breakpoints auto test",
            batch=batch_info,
        )
        .add_browser(500, 400, BrowserType.CHROME)
        .add_browser(800, 400, BrowserType.CHROME)
        .add_browser(800, 600, BrowserType.CHROME)
        .add_browser(1024, 768, BrowserType.CHROME)
        .add_browser(1200, 800, BrowserType.CHROME)
        .set_layout_breakpoints(True)
    )
    eyes.open(driver, viewport_size=RectangleSize(800, 600))
    eyes.check_window()
    eyes.close()


def test_inferred_layout_breakpoints_with_devices(driver, batch_info, vg_runner):
    driver.get("https://applitools.github.io/demo/TestPages/JsLayout")
    eyes = Eyes(vg_runner)
    eyes.set_configuration(
        Configuration(
            app_name="Eyes SDK",
            test_name="UFG Layout Breakpoints inferred devices",
            batch=batch_info,
        )
        .add_browser(ChromeEmulationInfo("iPad", "portrait"))
        .add_browser(
            IosDeviceInfo(IosDeviceName.iPhone_12, ScreenOrientation.LANDSCAPE)
        )
        .add_browser(800, 600, BrowserType.CHROME)
        .add_browser(1024, 768, BrowserType.CHROME)
        .set_layout_breakpoints(True)
    )
    eyes.open(driver, viewport_size=RectangleSize(800, 600))
    eyes.check_window()
    eyes.close()


def test_explicit_layout_breakpoints(driver, batch_info, vg_runner):
    driver.get("https://applitools.github.io/demo/TestPages/JsLayout")
    eyes = Eyes(vg_runner)
    eyes.set_configuration(
        Configuration(
            app_name="Eyes SDK",
            test_name="UFG Layout Breakpoints explicit chrome",
            batch=batch_info,
        )
        .add_browser(500, 400, BrowserType.CHROME)
        .add_browser(800, 400, BrowserType.CHROME)
        .add_browser(800, 600, BrowserType.CHROME)
        .add_browser(1024, 768, BrowserType.CHROME)
        .add_browser(1200, 800, BrowserType.CHROME)
        .set_layout_breakpoints(500, 1000)
    )
    eyes.open(driver, viewport_size=RectangleSize(800, 600))
    eyes.check_window()
    eyes.close()


def test_inferred_layout_breakpoints(driver, batch_info, vg_runner):
    driver.get("https://applitools.github.io/demo/TestPages/JsLayout")
    eyes = Eyes(vg_runner)
    eyes.set_configuration(
        Configuration(
            app_name="Eyes SDK",
            test_name="UFG Layout Breakpoints inferred chrome",
            batch=batch_info,
        )
        .add_browser(500, 400, BrowserType.CHROME)
        .add_browser(800, 400, BrowserType.CHROME)
        .add_browser(800, 600, BrowserType.CHROME)
        .add_browser(1024, 768, BrowserType.CHROME)
        .add_browser(1200, 800, BrowserType.CHROME)
        .set_layout_breakpoints(True)
    )
    eyes.open(driver, viewport_size=RectangleSize(800, 600))
    eyes.check_window()
    eyes.close()


def test_inferred_layout_breakpoints_with_big_devices(driver, batch_info, vg_runner):
    driver.get("https://applitools.github.io/demo/TestPages/JsLayout")
    eyes = Eyes(vg_runner)
    eyes.set_configuration(
        Configuration(
            app_name="Eyes SDK",
            test_name="UFG Layout Breakpoints inferred big screen devices",
            batch=batch_info,
        )
        .add_browser(ChromeEmulationInfo("iPad", "portrait"))
        .add_browser(
            IosDeviceInfo(IosDeviceName.iPad_Pro_3, ScreenOrientation.PORTRAIT)
        )
        .add_browser(1024, 768, BrowserType.CHROME)
        .set_layout_breakpoints(True)
    )
    eyes.open(driver, viewport_size=RectangleSize(800, 600))
    eyes.check_window()
    eyes.close()


def test_inferred_layout_breakpoints_with_small_devices(driver, batch_info, vg_runner):
    driver.get("https://applitools.github.io/demo/TestPages/JsLayout")
    eyes = Eyes(vg_runner)
    eyes.set_configuration(
        Configuration(
            app_name="Eyes SDK",
            test_name="UFG Layout Breakpoints inferred small screen device",
            batch=batch_info,
        )
        .add_browser(
            IosDeviceInfo(IosDeviceName.iPhone_12, ScreenOrientation.LANDSCAPE)
        )
        .add_browser(IosDeviceInfo(IosDeviceName.iPhone_12, ScreenOrientation.PORTRAIT))
        .add_browser(1024, 768, BrowserType.CHROME)
        .set_layout_breakpoints(True)
    )
    eyes.open(driver, viewport_size=RectangleSize(800, 600))
    eyes.check_window()
    eyes.close()
