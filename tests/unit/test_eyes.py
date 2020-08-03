import pytest

from applitools.core import ServerConnector


def pytest_generate_tests(metafunc):
    if "eyes" in metafunc.fixturenames:
        metafunc.parametrize(
            "eyes", ["selenium", "visual_grid", "images"], indirect=True
        )


def test_is_disabled_True(eyes):
    eyes.is_disabled = True
    eyes.check("Test", None)


def test_is_disabled_False(eyes):
    with pytest.raises(Exception):
        eyes.is_disabled = False
        eyes.check(None, None)


def test_set_get_server_connector(eyes):
    class CustomServerCon(ServerConnector):
        pass

    conn = CustomServerCon()
    eyes.server_connector = conn
    assert eyes.server_connector is conn


def test_set_incorrect_server_connector(eyes):
    class CustomServerCon:
        pass

    with pytest.raises(ValueError):
        eyes.server_connector = CustomServerCon()
