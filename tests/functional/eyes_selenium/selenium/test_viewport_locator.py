import pytest
from PIL import Image

from applitools.common import Point
from applitools.selenium import Target
from applitools.selenium.viewport_locator import (
    Pattern,
    add_page_marker,
    find_pattern,
    remove_page_marker,
)
from tests.utils import get_resource_path


def test_add_remove_marker(driver, eyes):
    driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage/")
    eyes.open(
        driver,
        "Viewport locator tests",
        "Add and remove marker",
        {"width": 500, "height": 300},
    )
    marker = add_page_marker(driver, 2)
    eyes.check("Marker added", Target.window())
    remove_page_marker(driver)
    eyes.check("Marker removed", Target.window())
    eyes.close()
    assert marker == Pattern(2, 6, [0, 1, 0])


@pytest.mark.parametrize(
    "image_name, marker_location, pixel_ratio",
    [
        ("iPad_Air_portrait.png", Point(0, 140), 2),
        ("iPhone_5S_landscape.png", Point(0, 100), 2),
        ("iPhone_X_perfecto_portrait.png", Point(0, 297), 3),
        ("iPhone_XR_perfecto_landscape.png", Point(88, 100), 2),
        ("iPhone_XS_landscape.png", Point(132, 150), 3),
        ("iPhone_XS_Max_perfecto_landscape.png", Point(132, 150), 3),
        ("iPhone_XS_portrait_nomarker.png", None, 3),
        ("iPhone_XS_portrait.png", Point(0, 282), 3),
    ],
)
def test_find_pattern(image_name, marker_location, pixel_ratio):
    marker = Pattern(pixel_ratio, 3 * pixel_ratio, [0, 1, 0])
    image = Image.open(get_resource_path("unit/ios_screenshots/" + image_name))

    location = find_pattern(image, marker)

    assert location == marker_location
