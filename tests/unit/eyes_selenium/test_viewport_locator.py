import pytest
from PIL import Image

from applitools.common import Point
from applitools.selenium.viewport_locator import Pattern, find_pattern
from tests.utils import get_resource_path


@pytest.mark.parametrize(
    "image_name, marker_location, pixel_ratio",
    [
        ("iPhone_XR_landscape.png", Point(88, 100), 2),
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
