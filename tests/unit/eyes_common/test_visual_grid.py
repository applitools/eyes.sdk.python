from applitools.common import VGResource
from applitools.common.ultrafastgrid import (
    IosDeviceInfo,
    IosDeviceName,
    ScreenOrientation,
    DesktopBrowserInfo,
    BrowserType,
    RectangleSize,
    ChromeEmulationInfo,
    DeviceName,
    ScreenOrientation,
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
    assert idi.baseline_env_name is None

    idi = IosDeviceInfo(
        IosDeviceName.iPhone_11_Pro, ScreenOrientation.LANDSCAPE, "Baseline env",
    )
    assert idi.device_name == IosDeviceName.iPhone_11_Pro
    assert idi.screen_orientation == ScreenOrientation.LANDSCAPE
    assert idi.baseline_env_name == "Baseline env"

    idi = IosDeviceInfo("iPhone 11 Pro", "landscape")
    assert idi.device_name == IosDeviceName.iPhone_11_Pro
    assert idi.screen_orientation == ScreenOrientation.LANDSCAPE


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
