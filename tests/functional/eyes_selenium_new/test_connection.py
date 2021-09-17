from applitools.selenium.connection import USDKConnection


def test_make_manager():
    ec = USDKConnection.create()
    ec.notification(
        "Session.init", {"name": "aa", "version": "1", "protocol": "webdriver"}
    )
    ec.command("Core.makeManager", {"type": "classic"})
