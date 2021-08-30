import json
import os
from collections import namedtuple

from applitools.common import IosVersion, VGResource
from applitools.common.ultrafastgrid import (
    BrowserType,
    ChromeEmulationInfo,
    DesktopBrowserInfo,
    DeviceName,
    IosDeviceInfo,
    IosDeviceName,
    ScreenOrientation,
)
from applitools.common.utils import json_utils
from applitools.selenium.visual_grid.visual_grid_eyes import _group_tests_by_width


class DummyTest(namedtuple("DummyTest", ("name", "browser_info"))):
    def __new__(cls, name, width):
        return super(DummyTest, cls).__new__(cls, name, DesktopBrowserInfo(width, 0))


def test_vgresource_with_function_that_raises_exception_should_not_break():
    def _raise():
        raise Exception

    VGResource.from_blob(
        {
            "url": "https://someurl.com",
            "type": "application/empty-response",
            "content": b"",
        },
        _raise,
    )


def test_vg_resource_big_content_should_be_cutted_in_vg_resource():
    resource = VGResource(
        "https://test.url",
        "content-type/test",
        os.urandom(VGResource.MAX_RESOURCE_SIZE + 5),
    )
    assert len(resource.content) == VGResource.MAX_RESOURCE_SIZE


def test_chrome_emulation_info():
    cei = ChromeEmulationInfo(DeviceName.iPhone_X)
    assert cei.device_name == DeviceName.iPhone_X
    assert cei.screen_orientation == ScreenOrientation.PORTRAIT
    assert cei.baseline_env_name is None

    cei = ChromeEmulationInfo(
        DeviceName.iPhone_X, ScreenOrientation.LANDSCAPE, "Baseline env"
    )
    assert cei.device_name == DeviceName.iPhone_X
    assert cei.screen_orientation == ScreenOrientation.LANDSCAPE
    assert cei.baseline_env_name == "Baseline env"

    cei = ChromeEmulationInfo("iPhone X", "landscape")
    assert cei.device_name == DeviceName.iPhone_X
    assert cei.screen_orientation == ScreenOrientation.LANDSCAPE


def test_ios_device_info():
    idi = IosDeviceInfo(IosDeviceName.iPhone_11_Pro)
    assert idi.device_name == IosDeviceName.iPhone_11_Pro
    assert idi.screen_orientation == ScreenOrientation.PORTRAIT
    assert idi.ios_version is None
    assert idi.baseline_env_name is None
    assert {"name": "iPhone 11 Pro", "screenOrientation": "portrait"} == json.loads(
        json_utils.to_json(idi)
    )

    idi = IosDeviceInfo(
        IosDeviceName.iPhone_11_Pro,
        ScreenOrientation.LANDSCAPE,
        IosVersion.LATEST,
        "Baseline env",
    )
    assert idi.device_name == IosDeviceName.iPhone_11_Pro
    assert idi.screen_orientation == ScreenOrientation.LANDSCAPE
    assert idi.ios_version == IosVersion.LATEST
    assert idi.baseline_env_name == "Baseline env"
    assert {
        "name": "iPhone 11 Pro",
        "screenOrientation": "landscape",
        "iosVersion": "latest",
    } == json.loads(json_utils.to_json(idi))

    idi = IosDeviceInfo("iPhone 11 Pro", "landscape", "latest-1")
    assert idi.device_name == IosDeviceName.iPhone_11_Pro
    assert idi.screen_orientation == ScreenOrientation.LANDSCAPE
    assert idi.ios_version == IosVersion.ONE_VERSION_BACK
    assert {
        "name": "iPhone 11 Pro",
        "screenOrientation": "landscape",
        "iosVersion": "latest-1",
    } == json.loads(json_utils.to_json(idi))


def test_desktop_browser_info():
    dri = DesktopBrowserInfo(500, 600)
    assert dri.width == 500
    assert dri.height == 600
    assert dri.browser_type == BrowserType.CHROME
    assert dri.baseline_env_name is None

    dri = DesktopBrowserInfo(500, 600, BrowserType.SAFARI)
    assert dri.width == 500
    assert dri.height == 600
    assert dri.browser_type == BrowserType.SAFARI
    assert dri.baseline_env_name is None

    dri = DesktopBrowserInfo(500, 700, BrowserType.SAFARI, "base env")
    assert dri.width == 500
    assert dri.height == 700
    assert dri.browser_type == BrowserType.SAFARI
    assert dri.baseline_env_name == "base env"


def test_group_tests_by_width_disabled_layout():
    grouped = _group_tests_by_width([DummyTest("a", 100), DummyTest("b", 50)], False)

    assert grouped == {None: [DummyTest("b", 50), DummyTest("a", 100)]}


def test_group_tests_by_width_single_breakpoint_and_above():
    grouped = _group_tests_by_width([DummyTest("a", 100), DummyTest("b", 50)], [50])

    assert grouped == {50: [DummyTest("b", 50), DummyTest("a", 100)]}


def test_group_tests_by_width_single_breakpoint_and_one_below():
    grouped = _group_tests_by_width([DummyTest("a", 50), DummyTest("b", 49)], [50])

    assert grouped == {50: [DummyTest("a", 50)], 49: [DummyTest("b", 49)]}


def test_group_tests_by_width_single_breakpoint_and_well_below():
    grouped = _group_tests_by_width([DummyTest("a", 50), DummyTest("b", 20)], [50])

    assert grouped == {50: [DummyTest("a", 50)], 49: [DummyTest("b", 20)]}


def test_group_tests_by_width_far_below_single_breakpoint():
    grouped = _group_tests_by_width([DummyTest("a", 20)], [50])

    assert grouped == {49: [DummyTest("a", 20)]}


def test_group_tests_by_width_breakpoints_true():
    grouped = _group_tests_by_width(
        [DummyTest("a", 20), DummyTest("b", 20), DummyTest("c", 30)], True
    )

    assert grouped == {
        20: [DummyTest("a", 20), DummyTest("b", 20)],
        30: [DummyTest("c", 30)],
    }


def test_group_tests_by_width_multiple_duplicate_redundant_breakpoints1():
    grouped = _group_tests_by_width(
        [DummyTest("a", 5), DummyTest("b", 9), DummyTest("c", 10), DummyTest("d", 11)],
        [10, 20, 20, 30, 40],
    )

    assert grouped == {
        9: [DummyTest("a", 5), DummyTest("b", 9)],
        10: [DummyTest("c", 10), DummyTest("d", 11)],
    }


def test_group_tests_by_width_multiple_unsorted_redundant_breakpoints1():
    grouped = _group_tests_by_width(
        [DummyTest("a", 5), DummyTest("b", 20), DummyTest("c", 25), DummyTest("d", 50)],
        [20, 10, 30, 40],
    )

    assert grouped == {
        9: [DummyTest("a", 5)],
        20: [DummyTest("b", 20), DummyTest("c", 25)],
        40: [DummyTest("d", 50)],
    }
