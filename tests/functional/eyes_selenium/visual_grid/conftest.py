import pytest

from applitools.selenium import VisualGridRunner


@pytest.fixture(scope="function")
def vg_runner():
    vg = VisualGridRunner(10)
    return vg
