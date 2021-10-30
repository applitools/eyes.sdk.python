import pytest
from mock import patch

from applitools.core import Feature
from applitools.selenium import Region, Target


@pytest.mark.native_app("http://saucelabs.com/example_files/ContactManager.apk")
def test_android_native_sauce_labs(eyes, sauce_galaxy_s9_android9_driver):
    eyes.open(
        sauce_galaxy_s9_android9_driver,
        "AndroidNativeApp",
        "AndroidNativeApp checkWindow",
    )
    eyes.check(
        "Contact list",
        Target.window().ignore(Region(left=0, top=0, width=1440, height=100)),
    )
    eyes.close()


@pytest.mark.native_app("http://saucelabs.com/example_files/ContactManager.apk")
def test_android_native_region__sauce_labs(eyes, sauce_galaxy_s9_android9_driver):
    eyes.open(
        sauce_galaxy_s9_android9_driver,
        "AndroidNativeApp",
        "AndroidNativeApp checkRegionFloating",
    )
    settings = Target.region(Region(0, 100, 1400, 2000)).floating(
        Region(10, 10, 20, 20), 3, 3, 20, 30
    )
    eyes.check("Contact list", settings)
    eyes.close()


@pytest.mark.native_app(
    "https://applitools.jfrog.io/artifactory/"
    "Examples/eyes-ios-hello-world/1.2/eyes-ios-hello-world.zip"
)
def test_iOS_native__sauce_labs(eyes, sauce_iphone8_ios14_driver):
    eyes.open(sauce_iphone8_ios14_driver, "iOSNativeApp", "iOSNativeApp checkWindow")
    eyes.check(
        "Contact list",
        Target.window().ignore(Region(left=0, top=0, width=300, height=100)),
    )
    eyes.close()


@pytest.mark.native_app(
    "https://applitools.jfrog.io/artifactory/"
    "Examples/eyes-ios-hello-world/1.2/eyes-ios-hello-world.zip"
)
def test_iOS_native_region__sauce_labs(eyes, sauce_iphone8_ios14_driver):
    eyes.configure.set_features(Feature.SCALE_MOBILE_APP)
    eyes.open(
        sauce_iphone8_ios14_driver, "iOSNativeApp", "iOSNativeApp checkRegionFloating"
    )
    settings = Target.region(Region(0, 100, 375, 712)).floating(
        Region(10, 10, 20, 20), 3, 3, 20, 30
    )
    eyes.check("Contact list", settings)
    eyes.close()


@pytest.mark.native_app("http://saucelabs.com/example_files/ContactManager.apk")
def test_android_native_sauce_labs_tracking_id_sent(
    eyes, sauce_galaxy_s9_android9_driver
):
    eyes.open(
        sauce_galaxy_s9_android9_driver,
        "AndroidNativeApp",
        "AndroidNativeApp trackingIdSent",
    )
    with patch("applitools.core.server_connector.ServerConnector.match_window") as smw:
        eyes.check("Contact list", Target.window())
        match_window_data = smw.call_args[0][1]  # type: MatchWindowData
    eyes.close(False)
    assert match_window_data.options.source == "com.example.android.contactmanager"


@pytest.mark.native_app(
    "https://applitools.jfrog.io/artifactory/"
    "Examples/eyes-ios-hello-world/1.2/eyes-ios-hello-world.zip"
)
def test_iOS_native_region_sauce_labs_tracking_id_sent(
    eyes, sauce_iphone8_ios14_driver
):
    eyes.open(sauce_iphone8_ios14_driver, "iOSNativeApp", "iOSNativeApp trackingIdSent")
    with patch("applitools.core.server_connector.ServerConnector.match_window") as smw:
        eyes.check("Contact list", Target.window())
        match_window_data = smw.call_args[0][1]  # type: MatchWindowData
    eyes.close(False)
    assert match_window_data.options.source == "eyes-ios-hello-world.zip"
