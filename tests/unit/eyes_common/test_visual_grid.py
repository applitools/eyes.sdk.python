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
    dri = DesktopBrowserInfo(500, 500, BrowserType.SAFARI)
    assert dri.viewport_size == RectangleSize(500, 500)
    assert dri.browser_type == BrowserType.SAFARI

    dri = DesktopBrowserInfo(500, 500, BrowserType.SAFARI, "base env")
    assert dri.baseline_env_name == "base env"

    dri = DesktopBrowserInfo(RectangleSize(500, 500), BrowserType.SAFARI, "base env")
    assert dri.viewport_size == RectangleSize(500, 500)
    assert dri.browser_type == BrowserType.SAFARI
    assert dri.baseline_env_name == "base env"

    dri = DesktopBrowserInfo(dict(width=500, height=500), "safari-0", "base env")
    assert dri.viewport_size == RectangleSize(500, 500)
    assert dri.browser_type == BrowserType.SAFARI
    assert dri.baseline_env_name == "base env"
