from applitools.common import (
    ChromeEmulationInfo,
    DesktopBrowserInfo,
    DeviceName,
    IosDeviceInfo,
    IosDeviceName,
    IosVersion,
    ScreenOrientation,
)
from applitools.selenium.universal_sdk_types import demarshal_browser_info


def test_demarshal_browser_info():
    assert DesktopBrowserInfo(800, 600, "chrome") == demarshal_browser_info(
        {"width": 800, "height": 600, "name": "chrome"}
    )
    assert DesktopBrowserInfo(
        800, 600, "chrome-one-version-back"
    ) == demarshal_browser_info(
        {"width": 800, "height": 600, "name": "chrome-one-version-back"}
    )
    assert IosDeviceInfo(IosDeviceName.iPhone_12) == demarshal_browser_info(
        {
            "ios_device_info": {
                "device_name": "iPhone 12",
                "screen_orientation": "portrait",
            }
        }
    )
    assert IosDeviceInfo(
        IosDeviceName.iPhone_12, ScreenOrientation.PORTRAIT, IosVersion.ONE_VERSION_BACK
    ) == demarshal_browser_info(
        {
            "ios_device_info": {
                "device_name": "iPhone 12",
                "screen_orientation": "portrait",
                "ios_version": "latest-1",
            }
        }
    )
    assert ChromeEmulationInfo(DeviceName.Galaxy_S10) == demarshal_browser_info(
        {
            "chrome_emulation_info": {
                "device_name": "Galaxy S10",
                "screen_orientation": "portrait",
            }
        }
    )
