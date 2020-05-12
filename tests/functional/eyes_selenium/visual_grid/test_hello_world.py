import pytest

from selenium.webdriver.common.by import By
from applitools.selenium import (
    Eyes,
    VisualGridRunner,
    ClassicRunner,
    BrowserType,
    Configuration,
    Target,
)


def pytest_generate_tests(metafunc):
    metafunc.parametrize("eyes_runner", [ClassicRunner(), VisualGridRunner(1)])


@pytest.fixture()
def name_suffix(eyes_runner):
    if isinstance(eyes_runner, ClassicRunner):
        return ""
    else:
        return "_VG"


@pytest.mark.platform("Linux")
@pytest.mark.test_page_url("https://applitools.com/helloworld")
def test_hello_world(eyes_runner, driver, name_suffix):
    eyes = Eyes(eyes_runner)
    sconf = (
        Configuration()
        .add_browser(800, 600, BrowserType.CHROME)
        .add_browser(700, 500, BrowserType.FIREFOX)
        .add_browser(1200, 800, BrowserType.IE_10)
        .add_browser(1200, 800, BrowserType.IE_11)
        .add_browser(1600, 1200, BrowserType.EDGE_CHROMIUM)
        .set_app_name("Hello World Demo")
        .set_test_name("Hello World Demo" + name_suffix)
    )
    eyes.set_configuration(sconf)
    eyes.open(driver)

    eyes.check(
        "",
        Target.window()
        .with_name("Step 1 - Viewport")
        .ignore([By.CSS_SELECTOR, ".primary"]),
    )
    eyes.check(
        "",
        Target.window()
        .fully()
        .with_name("Step 1 - Full Page")
        .floating([By.CSS_SELECTOR, ".primary"], 10, 20, 30, 40)
        .floating([By.TAG_NAME, "button"], 1, 2, 3, 4),
    )
    driver.find_element_by_tag_name("button").click()
    eyes.check("", Target.window().with_name("Step 2 - Viewport"))
    eyes.check("", Target.window().fully().with_name("Step 2 - Full Page"))
    eyes.close(True)
