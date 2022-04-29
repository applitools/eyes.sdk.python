from enum import Enum
from os import environ

import pytest
from appium.webdriver import Remote
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.ui import WebDriverWait

from applitools.common import (
    AndroidDeviceName,
    BatchInfo,
    IosDeviceName,
    ScreenOrientation,
)
from applitools.selenium import Eyes, Target

batch = BatchInfo("Python Viewport Measurement")

SAUCE_MAPPING = {
    "Galaxy S10": ("Samsung Galaxy S10 WQHD GoogleAPI Emulator", "11.0"),
    "Galaxy S20": ("Samsung Galaxy S20 WQHD GoogleAPI Emulator", "11.0"),
    "Galaxy S8": ("Samsung Galaxy S8 GoogleAPI Emulator", "8.1"),
    "Galaxy S8 Plus": ("Samsung Galaxy S8 Plus GoogleAPI Emulator", "8.1"),
    "Galaxy S9": ("Samsung Galaxy S9 WQHD GoogleAPI Emulator", "9.0"),
    "Galaxy S9 Plus": ("Samsung Galaxy S9 Plus WQHD GoogleAPI Emulator", "8.1"),
    "Pixel 3 XL": ("Google Pixel 3 XL GoogleAPI Emulator", "12.0"),
    "Pixel 4": ("Google Pixel 4 GoogleAPI Emulator", "12.0"),
    "Pixel 4 XL": ("Google Pixel 4 XL GoogleAPI Emulator", "12.0"),
    "iPad (7th generation)": ("iPad (7th generation) Simulator", "15.4"),
    "iPad (9th generation)": ("iPad (9th generation) Simulator", "15.4"),
    "iPad Air (2nd generation)": ("iPad Air 2 Simulator", "15.4"),
    "iPad Pro (12.9-inch) (3rd generation)": (
        "iPad Pro (12.9 inch) (3rd generation) Simulator",
        "15.4",
    ),
    "iPhone 11": ("iPhone 11 Simulator", "15.4"),
    "iPhone 11 Pro": ("iPhone 11 Pro Simulator", "15.4"),
    "iPhone 11 Pro Max": ("iPhone 11 Pro Max Simulator", "15.4"),
    "iPhone 12": ("iPhone 12 Simulator", "15.4"),
    "iPhone 12 Pro": ("iPhone 12 Pro Simulator", "15.4"),
    "iPhone 12 Pro Max": ("iPhone 12 Pro Max Simulator", "15.4"),
    "iPhone 12 mini": ("iPhone 12 mini Simulator", "14.5"),
    "iPhone 13": ("iPhone 13 Simulator", "15.4"),
    "iPhone 13 Pro": ("iPhone 13 Pro Simulator", "15.4"),
    "iPhone 13 Pro Max": ("iPhone 13 Pro Max Simulator", "15.4"),
    "iPhone 7": ("iPhone 7 Plus Simulator", "15.4"),
    "iPhone 8": ("iPhone 8 Simulator", "15.4"),
    "iPhone 8 Plus": ("iPhone 8 Plus Simulator", "15.4"),
    "iPhone SE (1st generation)": ("iPhone SE (1st generation) Simulator", "15.4"),
    "iPhone X": ("iPhone X Simulator", "15.4"),
    "iPhone XR": ("iPhone XR Simulator", "15.4"),
    "iPhone Xs": ("iPhone XS Simulator", "15.4"),
}

BS_MAPPING = {
    "Galaxy Note 10": ("Samsung Galaxy Note 10", "9.0"),
    "Galaxy Note 10 Plus": ("Samsung Galaxy Note 10 Plus", "9.0"),
    "Galaxy Note 8": ("Samsung Galaxy Note 8", "7.1"),
    "Galaxy Note 9": ("Samsung Galaxy Note 9", "8.1"),
    "Galaxy S10": ("Samsung Galaxy S10", "9.0"),
    "Galaxy S10 Plus": ("Samsung Galaxy S10 Plus", "9.0"),
    "Galaxy S20": ("Samsung Galaxy S20 Ultra", "10.0"),
    "Galaxy S20 Plus": ("Samsung Galaxy S20 Plus", "10.0"),
    "Galaxy S21": ("Samsung Galaxy S21", "11.0"),
    "Galaxy S21 Plus": ("Samsung Galaxy S21 Plus", "11.0"),
    "Galaxy S21 Ultra": ("Samsung Galaxy S21 Ultra", "11.0"),
    "Galaxy S8": ("Samsung Galaxy S8", "7.0"),
    "Galaxy S8 Plus": ("Samsung Galaxy S8 Plus", "7.0"),
    "Galaxy S9": ("Samsung Galaxy S9", "8.0"),
    "Galaxy S9 Plus": ("Samsung Galaxy S9 Plus", "8.0"),
    "Pixel 3 XL": ("Google Pixel 3 XL", "9.0"),
    "Pixel 4": ("Google Pixel 4", "10.0"),
    "Pixel 4 XL": ("Google Pixel 4 XL", "10.0"),
    "iPhone 11": ("iPhone 11", "13"),
    "iPhone 11 Pro": ("iPhone 11 Pro", "13"),
    "iPhone 11 Pro Max": ("iPhone 11 Pro Max", "13"),
    "iPhone 12": ("iPhone 12", "14"),
    "iPhone 12 Pro": ("iPhone 12 Pro", "14"),
    "iPhone 12 Pro Max": ("iPhone 12 Pro Max", "14"),
    "iPhone 12 mini": ("iPhone 12 Mini", "14"),
    "iPhone 13": ("iPhone 13", "15"),
    "iPhone 13 Pro": ("iPhone 13 Pro", "15"),
    "iPhone 13 Pro Max": ("iPhone 13 Pro Max", "15"),
    "iPhone 7": ("iPhone 7", "10"),
    "iPhone 8": ("iPhone 8", "11"),
    "iPhone 8 Plus": ("iPhone 8 Plus", "11"),
    "iPhone X": ("iPhone X", "11"),
    "iPhone XR": ("iPhone XR", "12"),
    "iPhone Xs": ("iPhone XS", "12"),
}


class Provider(Enum):
    SAUCE = "sauce"
    BS = "bs"

    @property
    def url(self):
        return PROVIDER_URL[self]


class StatusBar(Enum):
    SHOWN = "status_shown"
    HIDDEN = "status_hidden"


class NavBar(Enum):
    SHOWN = "navbar_shown"
    HIDDEN = "navbar_hidden"


PROVIDER_URL = {
    # Provider.LOCAL: "http://localhost:4723/wd/hub",
    Provider.SAUCE: "https://{}:{}@ondemand.saucelabs.com:443/wd/hub".format(
        environ["SAUCE_USERNAME"], environ["SAUCE_ACCESS_KEY"]
    ),
    Provider.BS: "https://{}:{}@hub-cloud.browserstack.com/wd/hub".format(
        environ["BROWSERSTACK_USERNAME"], environ["BROWSERSTACK_ACCESS_KEY"]
    ),
}

ANDROID_APP_BUTTONS = {
    (StatusBar.HIDDEN, NavBar.HIDDEN): "btnActivityFullScreen",
    (StatusBar.SHOWN, NavBar.HIDDEN): "btnActivityNoNavBar",
    (StatusBar.HIDDEN, NavBar.SHOWN): "btnActivityNoStatusBar",
    (StatusBar.SHOWN, NavBar.SHOWN): "btnActivityStatusBar",
}
IOS_APP_LABELS = {
    StatusBar.SHOWN: "With status bar",
    StatusBar.HIDDEN: "Without status bar",
}


def create_caps(provider, device_name, orientation):
    if provider is Provider.SAUCE:
        caps_device_name, caps_version = SAUCE_MAPPING[device_name.value]
        apk_url = "https://applitools.jfrog.io/artifactory/Examples/viewportTestApp.apk"
        ipa_url = "https://applitools.jfrog.io/artifactory/iOS/Applications/ViewportDemoiOS/app/ViewportDemoiOS.zip"
    else:
        caps_device_name, caps_version = BS_MAPPING[device_name.value]
        apk_url = "bs://fc266d6e049417d40bbcad5c2b6ab4f90952b04e"

    if type(device_name) is AndroidDeviceName:
        caps = {
            "platformName": "Android",
            "appium:app": apk_url,
            "appium:deviceName": caps_device_name,
            "appium:platformVersion": caps_version,
            "appium:clearSystemFiles": True,
            "appium:automationName": "UiAutomator2",
            "appium:deviceOrientation": orientation.value.lower(),
        }
    else:
        caps = {
            "platformName": "iOS",
            "appium:app": ipa_url,
            "appium:deviceName": caps_device_name,
            "appium:platformVersion": caps_version,
            "appium:deviceOrientation": orientation.value.lower(),
        }
    return caps


def wait_for_element(driver, strategy, locator):
    wait = WebDriverWait(driver, 20)
    return wait.until(presence_of_element_located((strategy, locator)))


SAUCE_ANDROID = [
    (d, Provider.SAUCE) for d in AndroidDeviceName if d.value in SAUCE_MAPPING
]
BS_ANDROID = [(d, Provider.BS) for d in AndroidDeviceName if d.value in BS_MAPPING]


@pytest.mark.parametrize("statusbar", StatusBar)
@pytest.mark.parametrize("navbar", NavBar)
@pytest.mark.parametrize("orientation", ScreenOrientation)
@pytest.mark.parametrize("device, provider", SAUCE_ANDROID + BS_ANDROID)
def test_viewport_size_android(
    device, orientation, statusbar, navbar, provider, request
):
    caps = create_caps(provider, device, orientation)
    with Remote(provider.url, caps) as driver:
        button = ANDROID_APP_BUTTONS[(statusbar, navbar)]
        wait_for_element(driver, MobileBy.ID, button).click()
        eyes = Eyes()
        eyes.configure.batch = batch
        eyes.open(driver, "NavbarApp", request.node.name)
        eyes.check(Target.window().fully(False))
        result = eyes.close(False)
        viewport = result.host_display_size
        with open("results.csv", "a") as f:
            print(
                provider,
                device,
                orientation,
                statusbar,
                navbar,
                viewport.width,
                viewport.height,
                sep=";",
                file=f,
            )


SAUCE_IOS = [(d, Provider.SAUCE) for d in IosDeviceName if d.value in SAUCE_MAPPING]
BS_IOS = [(d, Provider.BS) for d in IosDeviceName if d.value in BS_MAPPING]


@pytest.mark.parametrize("statusbar", StatusBar)
@pytest.mark.parametrize("orientation", ScreenOrientation)
@pytest.mark.parametrize("device, provider", SAUCE_IOS)
def test_viewport_size_ios(device, orientation, statusbar, provider, request):
    caps = create_caps(provider, device, orientation)
    with Remote(provider.url, caps) as driver:
        button = IOS_APP_LABELS[statusbar]
        wait_for_element(
            driver, MobileBy.IOS_PREDICATE, 'label == "{}"'.format(button)
        ).click()
        eyes = Eyes()
        eyes.configure.batch = batch
        eyes.open(driver, "NavbarApp", request.node.name)
        eyes.check(Target.window().fully(False))
        result = eyes.close(False)
        viewport = result.host_display_size
        with open("results.csv", "a") as f:
            print(
                provider,
                device,
                orientation,
                statusbar,
                None,
                viewport.width,
                viewport.height,
                sep=";",
                file=f,
            )
