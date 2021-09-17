import pytest
from selenium import webdriver


@pytest.fixture
def local_chrome_driver():
    with webdriver.Chrome() as driver:
        yield driver
