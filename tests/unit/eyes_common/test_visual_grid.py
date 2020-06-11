from applitools.common import VGResource
from applitools.common.ultrafastgrid import (
    IosDeviceInfo,
    IosDeviceName,
    IosScreenOrientation,
    DesktopBrowserInfo,
    BrowserType,
    RectangleSize,
)


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


def test_ios_device_info():
    idi = IosDeviceInfo(IosDeviceName.iPhone_11_Pro)
    assert idi.device_name == IosDeviceName.iPhone_11_Pro
    assert idi.screen_orientation is None

    idi = IosDeviceInfo(
        IosDeviceName.iPhone_11_Pro, IosScreenOrientation.LANDSCAPE_RIGHT
    )
    assert idi.device_name == IosDeviceName.iPhone_11_Pro
    assert idi.screen_orientation == IosScreenOrientation.LANDSCAPE_RIGHT

    idi = IosDeviceInfo("iPhone 11 Pro", "landscapeRight")
    assert idi.device_name == IosDeviceName.iPhone_11_Pro
    assert idi.screen_orientation == IosScreenOrientation.LANDSCAPE_RIGHT


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
