from __future__ import unicode_literals

from os import getcwd

import pytest

from applitools.selenium.command_executor import CommandExecutor, ManagerType
from applitools.selenium.connection import USDKConnection
from applitools.selenium.universal_sdk_types import marshal_webdriver_ref


def test_usdk_commands_make_manager():
    commands = CommandExecutor(USDKConnection.create())
    commands.make_sdk("sdk_name", "sdk_version", getcwd())

    mgr = commands.core_make_manager(ManagerType.CLASSIC)

    assert "applitools-ref-id" in mgr


def test_usdk_commands_open_eyes(local_chrome_driver):
    local_chrome_driver.get("https://demo.applitools.com")
    commands = CommandExecutor(USDKConnection.create())

    commands.make_sdk("sdk_name", "sdk_version", getcwd())

    mgr = commands.core_make_manager(ManagerType.CLASSIC)

    eyes = commands.manager_open_eyes(
        mgr,
        {
            "sessionId": local_chrome_driver.session_id,
            "serverUrl": local_chrome_driver.command_executor._url,  # noqa
            "capabilities": local_chrome_driver.capabilities,
        },
        {"appName": "a", "testName": "b"},
    )

    assert "applitools-ref-id" in eyes


def test_usdk_commands_set_get_viewport_size(local_chrome_driver):
    driver = marshal_webdriver_ref(local_chrome_driver)
    commands = CommandExecutor(USDKConnection.create())
    commands.make_sdk("sdk_name", "sdk_version", getcwd())

    commands.core_set_viewport_size(driver, {"width": 800, "height": 600})
    returned_size = commands.core_get_viewport_size(driver)

    assert returned_size == {"width": 800, "height": 600}


def test_usdk_commands_open_close_eyes(local_chrome_driver):
    driver = marshal_webdriver_ref(local_chrome_driver)
    commands = CommandExecutor(USDKConnection.create())
    commands.make_sdk("sdk_name", "sdk_version", getcwd())
    mgr = commands.core_make_manager(ManagerType.CLASSIC)
    eyes = commands.manager_open_eyes(
        mgr,
        driver,
        {
            "appName": "USDK Test",
            "testName": "USDK Commands open close",
        },
    )

    assert "applitools-ref-id" in mgr

    eyes_close_result = commands.eyes_close_eyes(eyes, True)
    test_result = eyes_close_result[0]

    assert len(eyes_close_result) == 1
    assert test_result["appName"] == "USDK Test"
    assert test_result["name"] == "USDK Commands open close"

    manager_close_result = commands.manager_close_all_eyes(mgr, 100)

    assert manager_close_result == eyes_close_result


@pytest.mark.skip("Aborted test is missing from all results")
def test_usdk_commands_open_abort_eyes(local_chrome_driver):
    driver = marshal_webdriver_ref(local_chrome_driver)
    commands = CommandExecutor(USDKConnection.create())
    commands.make_sdk("sdk_name", "sdk_version", getcwd())
    mgr = commands.core_make_manager(ManagerType.CLASSIC)
    eyes = commands.manager_open_eyes(
        mgr,
        driver,
        {
            "appName": "USDK Test",
            "testName": "USDK Commands open abort",
        },
    )

    assert "applitools-ref-id" in mgr

    eyes_abort_result = commands.eyes_abort_eyes(eyes, True)
    test_result = eyes_abort_result[0]

    assert len(eyes_abort_result) == 1
    assert test_result["appName"] == "USDK Test"
    assert test_result["name"] == "USDK Commands open abort"

    manager_close_result = commands.manager_close_all_eyes(mgr, 100)

    assert manager_close_result == eyes_abort_result


def test_usdk_commands_open_check_close_eyes(local_chrome_driver):
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/SimpleTestPage"
    )
    config = {"appName": "USDK Test", "testName": "USDK Commands open check close"}
    driver = marshal_webdriver_ref(local_chrome_driver)
    commands = CommandExecutor(USDKConnection.create())
    commands.make_sdk("sdk_name", "sdk_version", getcwd())
    mgr = commands.core_make_manager(ManagerType.CLASSIC)
    eyes = commands.manager_open_eyes(mgr, driver, config)

    check_result = commands.eyes_check(eyes)

    eyes_close_result = commands.eyes_close_eyes(eyes, True)
    test_result = eyes_close_result[0]

    assert "applitools-ref-id" in mgr
    assert check_result == {"asExpected": True}
    assert len(eyes_close_result) == 1
    assert test_result["appName"] == "USDK Test"
    assert test_result["name"] == "USDK Commands open check close"

    manager_close_result = commands.manager_close_all_eyes(mgr, 100)

    assert manager_close_result == eyes_close_result
