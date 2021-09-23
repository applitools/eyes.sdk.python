import pytest

from applitools.selenium.command_executor import CommandExecutor, ManagerType
from applitools.selenium.connection import USDKConnection
from applitools.selenium.webdriver_marshal import marshal_webdriver_ref


def test_usdk_commands_make_manager():
    commands = CommandExecutor(USDKConnection.create())
    commands.make_sdk()

    mgr = commands.core_make_manager(ManagerType.CLASSIC)

    assert "applitools-ref-id" in mgr


def test_usdk_commands_set_get_viewport_size(local_chrome_driver):
    driver = marshal_webdriver_ref(local_chrome_driver)
    commands = CommandExecutor(USDKConnection.create())
    commands.make_sdk()

    commands.core_set_viewport_size(driver, {"width": 800, "height": 600})
    returned_size = commands.core_get_viewport_size(driver)

    assert returned_size == {"width": 800, "height": 600}


def test_usdk_commands_open_close_eyes(local_chrome_driver):
    driver = marshal_webdriver_ref(local_chrome_driver)
    commands = CommandExecutor(USDKConnection.create())
    commands.make_sdk()
    mgr = commands.core_make_manager(ManagerType.CLASSIC)
    eyes = commands.manager_open_eyes(
        mgr,
        driver,
        {
            "appName": "app name",
            "testName": "test name",
        },
    )

    assert "applitools-ref-id" in mgr

    eyes_close_result = commands.eyes_close_eyes(eyes)
    test_result = eyes_close_result[0]

    assert len(eyes_close_result) == 1
    assert test_result["appName"] == "app name"
    assert test_result["name"] == "test name"

    manager_close_result = commands.manager_close_all_eyes(mgr)

    assert manager_close_result == eyes_close_result


@pytest.mark.skip("Aborted test is missing from results")
def test_usdk_commands_open_abort_eyes(local_chrome_driver):
    driver = marshal_webdriver_ref(local_chrome_driver)
    commands = CommandExecutor(USDKConnection.create())
    commands.make_sdk()
    mgr = commands.core_make_manager(ManagerType.CLASSIC)
    eyes = commands.manager_open_eyes(
        mgr,
        driver,
        {
            "appName": "app name",
            "testName": "test name",
        },
    )

    assert "applitools-ref-id" in mgr

    eyes_abort_result = commands.eyes_abort_eyes(eyes)
    test_result = eyes_abort_result[0]

    assert len(eyes_abort_result) == 1
    assert test_result["appName"] == "app name"
    assert test_result["name"] == "test name"

    manager_close_result = commands.manager_close_all_eyes(mgr)

    assert manager_close_result == eyes_abort_result


def test_usdk_commands_open_check_close_eyes(local_chrome_driver):
    local_chrome_driver.get(
        "https://applitools.github.io/demo/TestPages/SimpleTestPage"
    )
    config = {"appName": "app name", "testName": "test name"}
    driver = marshal_webdriver_ref(local_chrome_driver)
    commands = CommandExecutor(USDKConnection.create())
    commands.make_sdk()
    mgr = commands.core_make_manager(ManagerType.CLASSIC)
    eyes = commands.manager_open_eyes(mgr, driver, config)

    assert "applitools-ref-id" in mgr

    check_result = commands.eyes_check(eyes)

    assert check_result == {"asExpected": True}

    eyes_close_result = commands.eyes_close_eyes(eyes)
    test_result = eyes_close_result[0]

    assert len(eyes_close_result) == 1
    assert test_result["appName"] == "app name"
    assert test_result["name"] == "test name"

    manager_close_result = commands.manager_close_all_eyes(mgr)

    assert manager_close_result == eyes_close_result
