import pytest

from applitools.common import Configuration, ImageMatchSettings
from applitools.selenium import ClassicRunner, Eyes, VisualGridRunner


@pytest.fixture
def custom_eyes_server():
    return None


@pytest.fixture
def configuration():
    return Configuration()


@pytest.fixture(scope="function")
def image_match_settings():
    return ImageMatchSettings()


@pytest.fixture(scope="function")
def eyes(request):
    if request.param == "selenium":
        return Eyes(ClassicRunner())
    elif request.param == "visual_grid":
        return Eyes(VisualGridRunner())
    else:
        raise ValueError("invalid internal test config")
