from applitools.selenium import Target
from applitools.selenium.viewport_locator import (
    Pattern,
    add_page_marker,
    remove_page_marker,
)


def test_add_remove_marker(driver, eyes):
    driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage/")
    device_pixel_ratio = driver.execute_script("return window.devicePixelRatio;")
    eyes.open(
        driver,
        "Viewport locator tests",
        "Add and remove marker",
        {"width": 500, "height": 300},
    )
    marker = add_page_marker(driver)
    eyes.check("Marker added", Target.window())
    remove_page_marker(driver)
    eyes.check("Marker removed", Target.window())
    eyes.close()
    assert marker == Pattern(device_pixel_ratio, device_pixel_ratio * 3, [0, 1, 0])
