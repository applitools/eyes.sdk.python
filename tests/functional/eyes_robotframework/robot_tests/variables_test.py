import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal


def get_variables(
    runner_type,  # type: Literal["web", "web_ufg", "mobile_native"]
    backend_library,  # type:  Literal["appium", "selenium"]
    platform,  # type: Literal["ios", "android", "desktop"]
):
    # type: (...) -> dict
    batch_name = "RobotFramework"

    if platform == "android":
        batch_name += " | Android"
        desired_caps = {
            "platformName": "Android",
            "platformVersion": "8.1",
            "deviceName": "Samsung Galaxy S9 HD GoogleAPI Emulator",
            "deviceOrientation": "portrait",
        }
    elif platform == "ios":
        batch_name += " | IOS"
        desired_caps = {
            "platformName": "iOS",
            "platformVersion": "14.3",
            "deviceName": "iPhone XR Simulator",
            "deviceOrientation": "portrait",
        }
    else:
        desired_caps = {}  # What?

    if backend_library == "appium":
        backend_library_name = "AppiumLibrary"
        desired_caps.update(
            {
                "appiumVersion": "1.20.1",
            }
        )

        if runner_type == "mobile_native":
            batch_name += " | App"
            if platform == "android":
                desired_caps.update(
                    {
                        "automationName": "UiAutomator2",
                        "app": "http://saucelabs.com/example_files/ContactManager.apk",
                        "clearSystemFiles": True,
                        "noReset": True,
                    }
                )
            elif platform == "ios":
                desired_caps.update(
                    {
                        "app": "http://174.138.1.48/doc/Demo_Application.zip",
                        "clearSystemFiles": True,
                        "noReset": True,
                        "automationName": "XCUITest",
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
