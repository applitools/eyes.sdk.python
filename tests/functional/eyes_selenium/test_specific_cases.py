import pytest
from selenium.webdriver.common.by import By

from applitools.core import Region
from applitools.eyes_selenium import StitchMode, Target, IgnoreRegionBySelector, FloatingRegion, FloatingBounds


@pytest.mark.platform('Linux')
def test_quickstart_example(eyes, driver):
    required_viewport = {'width': 450, 'height': 300}
    eyes.set_viewport_size(driver, required_viewport)
    eyes.open(driver=driver, app_name='Hello World!', test_name='My first Selenium Python test!',
              viewport_size={'width': 800, 'height': 600})
    driver.get('https://applitools.com/helloworld')

    eyes.check_window('Hello!')

    driver.find_element_by_css_selector('button').click()
    eyes.check_window('Click!')

    eyes.check_region(Region(20, 20, 50, 50), "step")

    eyes.close()


@pytest.mark.platform('Linux')
@pytest.mark.eyes(force_full_page_screenshot=True, stitch_mode=StitchMode.CSS)
def test_sample_script(eyes, driver):
    driver = eyes.open(driver, "Python app", "applitools", {'width': 800, 'height': 600})
    driver.get('http://applitools.github.io/demo/TestPages/FramesTestPage/')
    eyes.check_window("Home", target=(Target()
                                      .ignore(IgnoreRegionBySelector(By.CLASS_NAME, 'hero-container'))
                                      .floating(FloatingRegion(Region(10, 20, 30, 40), FloatingBounds(10, 0, 20, 10))))
                      )

    hero = driver.find_element_by_class_name("hero-container")
    eyes.check_region_by_element(hero, "Page Hero", target=(Target()
                                                            .ignore(Region(20, 20, 50, 50), Region(40, 40, 10, 20))))
    eyes.close()


@pytest.mark.platform('Linux')
@pytest.mark.eyes(force_full_page_screenshot=True)
def test_check_window_with_ignore_region_fluent(eyes, driver):
    eyes.open(driver, "Eyes Selenium SDK - Fluent API", "TestCheckWindowWithIgnoreRegion_Fluent",
              {'width': 800, 'height': 600})
    driver.get('http://applitools.github.io/demo/TestPages/FramesTestPage/')
    driver.find_element_by_tag_name('input').send_keys('My Input')
    eyes.check_window("Fluent - Window with Ignore region", target=Target().ignore(
        Region(left=50, top=50, width=100, height=100)))
    eyes.close()
