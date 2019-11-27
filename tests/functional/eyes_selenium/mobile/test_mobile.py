import pytest

from applitools.selenium import ScreenOrientation, Target

IOS_DEVICES = [
    ["iPad Pro (9.7 inch) Simulator", "12.0", ScreenOrientation.LANDSCAPE, False],
    ["iPhone XR Simulator", "12.0", ScreenOrientation.PORTRAIT, False],
    ["iPad Air 2 Simulator", "12.0", ScreenOrientation.LANDSCAPE, False],
    ["iPad Air 2 Simulator", "11.3", ScreenOrientation.LANDSCAPE, False],
    ["iPad Air 2 Simulator", "11.0", ScreenOrientation.LANDSCAPE, False],
    ["iPad Air 2 Simulator", "10.3", ScreenOrientation.LANDSCAPE, False],
    ["iPad Air 2 Simulator", "12.0", ScreenOrientation.PORTRAIT, False],
    ["iPad Air 2 Simulator", "11.3", ScreenOrientation.PORTRAIT, False],
    ["iPad Air 2 Simulator", "11.0", ScreenOrientation.PORTRAIT, False],
    ["iPad Air 2 Simulator", "10.3", ScreenOrientation.PORTRAIT, False],
    ["iPad Air Simulator", "12.0", ScreenOrientation.LANDSCAPE, False],
    ["iPad Air Simulator", "11.0", ScreenOrientation.PORTRAIT, True],
    ["iPad Simulator", "11.0", ScreenOrientation.LANDSCAPE, True],
    ["iPad Simulator", "11.0", ScreenOrientation.PORTRAIT, False],
    ["iPad (5th generation) Simulator", "11.0", ScreenOrientation.PORTRAIT, False],
    ["iPad Pro (9.7 inch) Simulator", "11.0", ScreenOrientation.LANDSCAPE, False],
    ["iPad Pro (9.7 inch) Simulator", "11.0", ScreenOrientation.LANDSCAPE, True],
    [
        "iPad Pro (12.9 inch) (2nd generation) Simulator",
        "11.0",
        ScreenOrientation.LANDSCAPE,
        False,
    ],
    [
        "iPad Pro (12.9 inch) (2nd generation) Simulator",
        "11.0",
        ScreenOrientation.PORTRAIT,
        True,
    ],
    [
        "iPad Pro (12.9 inch) (2nd generation) Simulator",
        "12.0",
        ScreenOrientation.PORTRAIT,
        True,
    ],
    ["iPad Pro (10.5 inch) Simulator", "11.0", ScreenOrientation.PORTRAIT, False],
    ["iPad Pro (10.5 inch) Simulator", "11.0", ScreenOrientation.LANDSCAPE, True],
    ["iPhone XS Max Simulator", "12.2", ScreenOrientation.LANDSCAPE, False],
    ["iPhone XS Max Simulator", "12.2", ScreenOrientation.LANDSCAPE, True],
    ["iPhone XS Max Simulator", "12.2", ScreenOrientation.PORTRAIT, False],
    ["iPhone XS Max Simulator", "12.2", ScreenOrientation.PORTRAIT, True],
    ["iPhone XS Simulator", "12.2", ScreenOrientation.PORTRAIT, False],
    ["iPhone XS Simulator", "12.2", ScreenOrientation.LANDSCAPE, False],
    ["iPhone XS Simulator", "12.2", ScreenOrientation.PORTRAIT, True],
    ["iPhone XS Simulator", "12.2", ScreenOrientation.LANDSCAPE, True],
    ["iPhone XR Simulator", "12.2", ScreenOrientation.PORTRAIT, False],
    ["iPhone XR Simulator", "12.2", ScreenOrientation.LANDSCAPE, False],
    ["iPhone XR Simulator", "12.2", ScreenOrientation.LANDSCAPE, True],
    ["iPhone X Simulator", "11.2", ScreenOrientation.PORTRAIT, False],
    ["iPhone X Simulator", "11.2", ScreenOrientation.PORTRAIT, True],
    ["iPhone 7 Simulator", "10.3", ScreenOrientation.PORTRAIT, True],
    ["iPhone 6 Plus Simulator", "11.0", ScreenOrientation.PORTRAIT, False],
    ["iPhone 6 Plus Simulator", "11.0", ScreenOrientation.LANDSCAPE, True],
    ["iPhone 5s Simulator", "10.3", ScreenOrientation.LANDSCAPE, False],
    ["iPhone 5s Simulator", "10.3", ScreenOrientation.LANDSCAPE, True],
]

ANDROID_DEVICES = [
    ["Android Emulator", "8.0", ScreenOrientation.PORTRAIT, False],
    ["Android Emulator", "8.0", ScreenOrientation.LANDSCAPE, True],
]


def create_browser_config(device, platform_name, browser_name):
    device_name, platform_version, dev_orientation, fully = device
    browser_config = {
        "deviceName": device_name,
        "deviceOrientation": dev_orientation.name.upper(),
        "platformVersion": platform_version,
        "platformName": platform_name,
        "browserName": browser_name,
        "fully": fully,
    }
    return browser_config


@pytest.mark.platform("Android")
@pytest.mark.parametrize(
    "mobile_eyes",
    [create_browser_config(device, "Android", "Chrome") for device in ANDROID_DEVICES],
    indirect=True,
    ids=lambda o: "{}-{}-{}".format(
        o["deviceName"], o["platformVersion"], o["deviceOrientation"]
    ),
)
def test_android__sauce_labs(mobile_eyes):
    eyes, fully = mobile_eyes
    eyes.check("", Target.window().fully(fully))


@pytest.mark.platform("iOS")
@pytest.mark.parametrize(
    "mobile_eyes",
    [create_browser_config(device, "iOS", "Safari") for device in IOS_DEVICES],
    indirect=True,
    ids=lambda o: "{}-{}-{}".format(
        o["deviceName"], o["platformVersion"], o["deviceOrientation"]
    ),
)
def test_IOS_safari_crop__sauce_labs(mobile_eyes):
    eyes, fully = mobile_eyes
    eyes.check("", Target.window().fully(fully))
