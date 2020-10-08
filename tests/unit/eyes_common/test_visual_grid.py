import json
from random import randint

from applitools.common import VGResource, IosVersion
from applitools.common.ultrafastgrid import (
    BrowserType,
    ChromeEmulationInfo,
    DesktopBrowserInfo,
    DeviceName,
    IosDeviceInfo,
    IosDeviceName,
    RectangleSize,
    ScreenOrientation,
)
from applitools.common.utils import json_utils


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
    chars = (b"a", b"b", b"c", b"2")
    resource = VGResource(
        "https://test.url",
        "content-type/test",
        b"".join(chars[randint(0, 3)] for _ in range(VGResource.MAX_RESOURCE_SIZE + 5)),
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
