from applitools.common.errors import USDKFailure


def test_usdk_failure_str():
    exc = USDKFailure("message", "stack")

    assert str(exc) == "message\nstack"


def test_usdk_failure_repr():
    exc = USDKFailure("message", "stack")

    assert repr(exc) == "USDKFailure('message', 'stack')"
