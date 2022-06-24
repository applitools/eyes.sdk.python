from applitools.common import (
    ChromeEmulationInfo,
    DesktopBrowserInfo,
    DeviceName,
    IosDeviceInfo,
    IosDeviceName,
    IosVersion,
    ScreenOrientation,
)
from applitools.selenium.universal_sdk_types import (
    demarshal_browser_info,
    demarshal_error,
)


def test_demarshal_browser_info():
    assert None == demarshal_browser_info(None)
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
            "iosDeviceInfo": {
                "deviceName": "iPhone 12",
                "screenOrientation": "portrait",
            }
        }
    )
    assert IosDeviceInfo(
        IosDeviceName.iPhone_12, ScreenOrientation.PORTRAIT, IosVersion.ONE_VERSION_BACK
    ) == demarshal_browser_info(
        {
            "iosDeviceInfo": {
                "deviceName": "iPhone 12",
                "screenOrientation": "portrait",
                "iosVersion": "latest-1",
            }
        }
    )
    assert ChromeEmulationInfo(DeviceName.Galaxy_S10) == demarshal_browser_info(
        {
            "chromeEmulationInfo": {
                "deviceName": "Galaxy S10",
                "screenOrientation": "portrait",
            }
        }
    )


def test_demarshal_usdk_error():
    exc = demarshal_error(
        {
            "message": "Message.",
            "stack": "Error: Message.\n  stack trace line 1\n  stack trace line 2",
        }
    )
    assert str(exc) == "Message.\n  stack trace line 1\n  stack trace line 2"
