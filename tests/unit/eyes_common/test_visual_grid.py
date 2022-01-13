import json
import os
from collections import namedtuple

from applitools.common import IosVersion
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


class DummyTest(namedtuple("DummyTest", ("name", "browser_info"))):
    def __new__(cls, name, width):
        return super(DummyTest, cls).__new__(cls, name, DesktopBrowserInfo(width, 0))


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

    idi = IosDeviceInfo("iPhone 11 Pro", "landscape", "latest-1")
    assert idi.device_name == IosDeviceName.iPhone_11_Pro
    assert idi.screen_orientation == ScreenOrientation.LANDSCAPE
    assert idi.ios_version == IosVersion.ONE_VERSION_BACK


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
