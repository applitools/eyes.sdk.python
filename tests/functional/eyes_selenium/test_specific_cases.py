import time

import pytest

from applitools.selenium import Target


def test_directly_set_viewport_size(eyes, local_chrome_driver):
    required_viewport = {"width": 800, "height": 600}
    eyes.set_viewport_size(local_chrome_driver, required_viewport)
    assert required_viewport == eyes.get_viewport_size(local_chrome_driver)


@pytest.mark.test_page_url("data:text/html,<p>Test</p>")
def test_abort_eyes(eyes, local_chrome_driver):
    eyes.open(
        local_chrome_driver, "Test Abort", "Test Abort", {"width": 1200, "height": 800}
    )
    time.sleep(15)
    eyes.abort()


def test_capture_element_on_pre_scrolled_down_page(eyes, local_chrome_driver):
    local_chrome_driver.get(
        "http://applitools.github.io/demo/TestPages/FramesTestPage/longframe.html"
    )
    eyes.open(
        driver=local_chrome_driver,
        app_name="Applitools Eyes SDK",
        test_name="Test capture element on pre scrolled down page",
        viewport_size={"width": 800, "height": 600},
    )
    local_chrome_driver.execute_script("window.scrollTo(0, 300)")
    eyes.check("Row 10", Target.region("body > table > tr:nth-child(10)"))
    eyes.check("Row 20", Target.region("body > table > tr:nth-child(20)"))
    eyes.close()


@pytest.mark.eyes_config(branch_name="master_python")
@pytest.mark.skip("USDK Difference, element not found")
def test_charts_with_scroll_root(eyes, local_chrome_driver):
    local_chrome_driver.get(
        "https://gistcdn.githack.com/skhalymon/048004f61ddcbf2d527daa6d6bc3b82f/raw/06cbf10fe444783445a5812691ae7f37b0db7559/MobileViewCorrect.html"
    )
    eyes.open(
        driver=local_chrome_driver,
        app_name="Applitools Eyes SDK",
        test_name="TestChartsWithScrollRoot",
        viewport_size={"width": 1200, "height": 700},
    )
    eyes.configure.add_property("Fluent", False)
    driver = eyes.driver
    frame1 = driver.find_element_by_id("mainFrame")
    driver.switch_to.frame(frame1)

    frame2 = driver.find_element_by_id("angularContainerIframe")
    driver.switch_to.frame(frame2)

    checked_element = driver.find_element_by_tag_name("mv-temperature-sensor-graph")
    checked_element2 = driver.find_element_by_tag_name("mv-humidity-sensor-graph")
    scroll_root = driver.find_element_by_tag_name("mat-sidenav-content")

    eyes.check(Target.window().region(checked_element).scroll_root_element(scroll_root))
    eyes.check(
        Target.window().region(checked_element2).scroll_root_element(scroll_root)
    )
    eyes.close()


@pytest.mark.eyes_config(branch_name="master_python")
@pytest.mark.skip("USDK Difference, region 0")
def test_charts_with_scroll_root_fluent(eyes, local_chrome_driver):
    local_chrome_driver.get(
        "https://gistcdn.githack.com/skhalymon/048004f61ddcbf2d527daa6d6bc3b82f/raw/06cbf10fe444783445a5812691ae7f37b0db7559/MobileViewCorrect.html"
    )
    eyes.open(
        driver=local_chrome_driver,
        app_name="Applitools Eyes SDK",
        test_name="TestChartsWithScrollRoot",
        viewport_size={"width": 1200, "height": 700},
    )
    eyes.check(
        Target.frame("mainFrame")
        .frame("angularContainerIframe")
        .region("mv-temperature-sensor-graph")
        .scroll_root_element("mat-sidenav-content")
    )

    eyes.check(
        Target.frame("mainFrame")
        .frame("angularContainerIframe")
        .region("mv-humidity-sensor-graph")
        .scroll_root_element("mat-sidenav-content")
    )

    eyes.close()
