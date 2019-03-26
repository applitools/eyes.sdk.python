import pytest
from PIL import Image

__all__ = ("image",)


@pytest.fixture
def image():
    img = Image.new("RGB", (800, 600), "black")
    pixels = img.load()  # create the pixel map

    for i in range(img.size[0]):  # for every col:
        for j in range(img.size[1]):  # For every row
            pixels[i, j] = (i, j, 100)  # set the colour accordingly
    return img
