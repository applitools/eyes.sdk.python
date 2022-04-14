import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal


def get_variables(
    runner_type,  # type: Literal["web", "web_ufg", "mobile_native", "native_mobile_grid"]
    backend_library,  # type:  Literal["appium", "selenium"]
    platform,  # type: Literal["ios", "android", "desktop"]
):
    # type: (...) -> dict
    batch_name = "RobotFramework"

    if platform == "android":
        batch_name += " | Android"
        desired_caps = {
            "platformName": "Android",
            "platformVersion": "10.0",
            "deviceName": "Google Pixel 3a XL GoogleAPI Emulator",
            "deviceOrientation": "portrait",
            "name": "Pixel 3a xl (Python)",
            "appiumVersion": "1.20.2",
        }
    elif platform == "ios":
        batch_name += " | IOS"
        desired_caps = {
            "platformName": "iOS",
            "platformVersion": "15.2",
            "deviceName": "iPhone 12 Pro Simulator",
            "deviceOrientation": "portrait",
        }
    else:
        desired_caps = {}  # What?

    if backend_library == "appium":
        backend_library_name = "AppiumLibrary"

        if runner_type in ["mobile_native", "native_mobile_grid"]:
            batch_name += " | App"
            if platform == "android":
                desired_caps.update(
                    {
                        "automationName": "UiAutomator2",
                        "app": "https://applitools.jfrog.io/artifactory/Examples/ufg-native-example.apk",
                        "clearSystemFiles": True,
                        "noReset": True,
                    }
                )
            elif platform == "ios":
                desired_caps.update(
                    {
                        "app": "https://applitools.jfrog.io/artifactory/Examples/DuckDuckGo-instrumented.app.zip",
                        "clearSystemFiles": True,
                        "noReset": True,
                        "automationName": "XCUITest",
                    }
                )
                if runner_type == "native_mobile_grid":
                    desired_caps.update(
                        {
                            "processArguments": {
                                "args": [],
                                "env": {
                                    "DYLD_INSERT_LIBRARIES": "@executable_path/Frameworks/UFG_lib.xcframework/ios-arm64_x86_64-simulator/UFG_lib.framework/UFG_lib"
                                },
                            }
                        }
                    )

        else:
            batch_name += " | Web"
            if platform == "desktop":
                batch_name += " | Desktop"
    elif backend_library == "selenium":
        batch_name += " | Web"
        backend_library_name = "SeleniumLibrary"

    else:
        raise ValueError("Invalid backend library", backend_library)

    if runner_type == "web":
        if platform == "android":
            desired_caps.update(
                {
                    "browserName": "Chrome",
                }
            )
        elif platform == "ios":
            desired_caps.update({"browserName": "Safari"})
    elif runner_type == "web_ufg":
        batch_name += " | UFG"
    elif runner_type == "native_mobile_grid":
        batch_name += " | UFG Native"

    if platform in ["android", "ios"]:
        remote_url = (
            "https://{username}:{password}@ondemand.saucelabs.com:443/wd/hub".format(
                username=os.environ["SAUCE_USERNAME"],
                password=os.environ["SAUCE_ACCESS_KEY"],
            )
        )
    else:
        remote_url = False

    return {
        "BATCH_NAME": batch_name,
        "RUNNER": runner_type,
        "BACKEND_LIBRARY_NAME": backend_library_name,
        "DESIRED_CAPS": desired_caps,
        "REMOTE_URL": remote_url,
    }
