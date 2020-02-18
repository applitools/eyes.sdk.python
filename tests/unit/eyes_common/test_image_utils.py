from applitools.common import Point
from applitools.common.utils import image_utils


def test_paste_image_no_error_if_point_has_float_values(image):
    point = Point(0, 0)
    point.x = 3.4
    point.x = 5.6
    image_utils.paste_image(image, image, point)
