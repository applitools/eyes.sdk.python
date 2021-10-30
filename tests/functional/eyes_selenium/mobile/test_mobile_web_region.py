import pytest
from selenium import webdriver as selenium_webdriver
from selenium.webdriver.common.by import By

from applitools.selenium import StitchMode, Target


@pytest.fixture
def webdriver_module():
    return selenium_webdriver


def _region_test_flow(eyes):
    eyes.configure.stitch_mode = StitchMode.Scroll
    eyes.check(
        "region-scroll",
        Target.region([By.TAG_NAME, "footer"]),
    )
    eyes.configure.stitch_mode = StitchMode.CSS
    eyes.check(
        "region-css",
        Target.region([By.TAG_NAME, "footer"]).timeout(0),
    )


def _region_fully_test_flow(eyes):
    eyes.configure.stitch_mode = StitchMode.Scroll
    eyes.check(
        "region-scroll",
        Target.region([By.TAG_NAME, "footer"]),
    )
    eyes.configure.stitch_mode = StitchMode.CSS
    eyes.check(
        "region-css",
        Target.region([By.TAG_NAME, "footer"]).fully().timeout(0),
    )


@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/RegionOutOfViewport/"
)
def test_region_capture_ios(eyes, sauce_iphone8_ios14_driver):
    eyes.configure.is_simulator = True
    eyes.open(sauce_iphone8_ios14_driver, "Mobile Web Tests", "TestRegionCapture_iOS")
    _region_test_flow(eyes)
    eyes.close()


@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/RegionOutOfViewport/"
)
def test_region_fully_capture_ios(eyes, sauce_iphone8_ios14_driver):
    eyes.configure.is_simulator = True
    eyes.open(
        sauce_iphone8_ios14_driver, "Mobile Web Tests", "TestRegionFullyCapture_iOS"
    )
    _region_fully_test_flow(eyes)
    eyes.close()


@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/RegionOutOfViewport/"
)
def test_region_capture_android(eyes, sauce_galaxy_s9_android9_driver):
    eyes.configure.is_simulator = True
    eyes.open(
        sauce_galaxy_s9_android9_driver, "Mobile Web Tests", "TestRegionCapture_Android"
    )
    _region_test_flow(eyes)
    eyes.close()


@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/RegionOutOfViewport/"
)
def test_region_fully_capture_android(eyes, sauce_galaxy_s9_android9_driver):
    eyes.configure.is_simulator = True
    eyes.open(
        sauce_galaxy_s9_android9_driver,
        "Mobile Web Tests",
        "TestRegionFullyCapture_Android",
    )
    _region_fully_test_flow(eyes)
    eyes.close()
