from applitools.selenium.connection import USDKConnection


def test_make_manager():
    ec = USDKConnection.create()
    ec.notification(
        "Core.makeSDK", {"name": "a", "version": "1", "protocol": "webdriver"}
    )
    res = ec.command("Core.makeManager", {"type": "classic"}, True, 1)
    assert "applitools-ref-id" in res["payload"]["result"]
