import pytest


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
