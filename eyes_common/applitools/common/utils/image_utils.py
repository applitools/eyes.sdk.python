"""
Utilities for image manipulation.
"""
from __future__ import absolute_import

import base64
import io
import math
import typing as tp

from PIL import Image

from applitools.common import logger
from applitools.common.errors import EyesError

if tp.TYPE_CHECKING:
    from applitools.common.geometry import Region

__all__ = (
    "image_from_file",
    "image_from_bytes",
    "image_from_base64",
    "scale_image",
    "get_base64",
    "get_bytes",
    "get_image_part",
)


def image_from_file(f):
    """
    Reads the PNG data from the given file stream and returns a new Image instance.
    """
    return Image.open(f)


def image_from_bytes(png_bytes):
    # type: (bytes) -> Image.Image
    """
    Reads the PNG data from the given png bytes and returns a new Image instance.

    :param png_bytes: Png bytes.
    :return: Image instance.
    """
    return Image.open(io.BytesIO(png_bytes))


def image_from_base64(base64_str):
    # type: (str) -> Image.Image
    """
    Reads the PNG data from the given png bytes and returns a new Image instance.

    :param png_bytes: Png bytes.
    :return: Image instance.
    """
    return Image.open(io.BytesIO(base64.b64decode(base64_str)))


def scale_image(image, scale_ratio):
    # type: (Image.Image, float) -> Image.Image
    if scale_ratio == 1:
        return image

    image_ratio = float(image.height) / float(image.width)
    scale_width = int(math.ceil(image.width * scale_ratio))
    scale_height = int(math.ceil(scale_width * image_ratio))
    image = image.convert("RGBA")
    scaled_image = image.resize((scale_width, scale_height), resample=Image.BICUBIC)
    return scaled_image


def get_base64(image):
    # type: (Image.Image) -> str
    """
    Gets the base64 representation of the PNG bytes.

    :return: The base64 representation of the PNG bytes.
    """
    image_bytes_stream = io.BytesIO()
    image.save(image_bytes_stream, format="PNG")
    image64 = base64.b64encode(image_bytes_stream.getvalue()).decode("utf-8")
    image_bytes_stream.close()
    return image64


def get_bytes(image):
    # type: (Image.Image) -> bytes
    """
    Gets the image bytes.

    :return: The image bytes.
    """
    image_bytes_stream = io.BytesIO()
    image.save(image_bytes_stream, format="PNG")
    image_bytes = image_bytes_stream.getvalue()
    image_bytes_stream.close()
    return image_bytes


def get_image_part(image, region):
    # type: (Image.Image, Region) -> Image.Image
    """
    Get a copy of the part of the image given by region.

    :return: The part of the image.
    """
    if region.is_empty:
        raise EyesError("region is empty!")
    return image.crop(box=(region.left, region.top, region.right, region.bottom))


def save_image(image, filename):
    try:
        logger.info("Saving file: {}".format(filename))
        image.save(filename)
    except Exception:
        logger.warning("Failed to save image")


def crop_image(image, region_to_crop):
    image_region = Region.from_(image)
    image_region.intersect(region_to_crop)
    if image_region.is_size_empty:
        logger.warning(
            "requested cropped area results in zero-size image! "
            "Cropped not performed. Returning original image."
        )
        return image

    if image_region != region_to_crop:
        logger.warning("requested cropped area overflows image boundaries.")

    cropped_image = image.cut(
        box=(
            image_region.left,
            image_region.top,
            image_region.right,
            image_region.bottom,
        )
    )
    return cropped_image
