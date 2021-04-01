from __future__ import division

import typing
from math import ceil

import attr

from applitools.common import Point

if typing.TYPE_CHECKING:
    from typing import List, Optional, Tuple

    from PIL.Image import Image

    from applitools.common.utils.custom_types import AnyWebDriver


@attr.s
class Pattern(object):
    offset = attr.ib()  # type: int
    size = attr.ib()  # type: int
    mask = attr.ib()  # type: List[int]


def add_page_marker(driver, pixel_ratio):
    # type: (AnyWebDriver, float) -> Pattern
    driver.execute_script(_ADD_PAGE_MARKER_JS)
    return Pattern(int(1 * pixel_ratio), int(3 * pixel_ratio), [0, 1, 0])


def remove_page_marker(driver):
    # type: (AnyWebDriver) -> None
    driver.execute_script(_CLEANUP_PAGE_MARKER_JS)


def find_pattern(image, pattern):
    # type: (Image, Pattern) -> Optional[Point]
    image = image.convert("RGB")
    for y in range(image.height // 2):  # Look for pattern in top left quadrant only
        for x in range(image.width // 2):
            if _is_pattern(image, x, y, pattern):
                return Point(x - pattern.offset, y - pattern.offset)


def _is_pattern(image, x, y, pattern):
    # type: (Image, int, int, Pattern) -> bool
    chunk_midsize = ceil(pattern.size / 2)
    # Try to check if centers of all chunks have matching color
    # makes significant performance improvement on dark images
    for chunk_index, chunk_color in enumerate(pattern.mask):
        chunk_center = x + chunk_midsize, y + chunk_midsize + chunk_index * pattern.size
        if _pixel_color_at(image, chunk_center, 10) != chunk_color:
            return False
    for chunk_index, chunk_color in enumerate(pattern.mask):
        threshold = 40
        # Check if all pixels of the chunk have matching color
        # Check is done from borders to center, reducing threshold closer to center
        for round in range(chunk_midsize):
            round_x = x + round
            round_y = y + round + chunk_index * pattern.size
            side_length = pattern.size - round * 2
            threshold = max(10, threshold - 10)
            for i in range(side_length):
                top = round_x + i, round_y
                bottom = round_x + i, round_y + side_length - 1
                left = round_x, round_y + i
                right = round_x + side_length - 1, round_y + i
                for pixel in top, bottom, left, right:
                    if _pixel_color_at(image, pixel, threshold) != chunk_color:
                        return False
    return True


def _pixel_color_at(image, xy, threshold):
    # type: (Image, Tuple[int, int], int) -> int
    r, g, b = image.getpixel(xy)
    white = 255 - threshold
    if r >= white and g >= white and b >= white:
        return 1
    elif r <= threshold and g <= threshold and b <= threshold:
        return 0
    else:
        return -1


_SET_ELEMENT_STYLE_PROPERTIES_JS = """
function __setElementStyleProperties([element, properties] = []) {
  const keys = Object.keys(properties).sort()
  const original = keys.reduce((original, prop) => {
    original[prop] = {
      value: element.style.getPropertyValue(prop),
      important: Boolean(element.style.getPropertyPriority(prop)),
    }
    return original
  }, {})

  keys.forEach(prop => {
    element.style.setProperty(
      prop,
      typeof properties[prop] === 'string' || !properties[prop]
        ? properties[prop]
        : properties[prop].value,
      properties[prop] && properties[prop].important ? 'important' : '',
    )
  })
  return original
}
"""

_ADD_PAGE_MARKER_JS = "{} {} return __addPageMarker()".format(
    _SET_ELEMENT_STYLE_PROPERTIES_JS,
    """
function __addPageMarker() {
  const marker = document.createElement('div')
  const contrast = document.createElement('div')
  marker.appendChild(contrast)
  document.body.appendChild(marker)
  marker.setAttribute('data-applitools-marker', '')

  marker.style.setProperty('position', 'fixed', 'important')
  marker.style.setProperty('top', '0', 'important')
  marker.style.setProperty('left', '0', 'important')
  marker.style.setProperty('width', '3px', 'important')
  marker.style.setProperty('height', '9px', 'important')
  marker.style.setProperty('box-sizing', 'content-box', 'important')
  marker.style.setProperty('border', '1px solid rgb(127,127,127)', 'important')
  marker.style.setProperty('background', 'rgb(0,0,0)', 'important')
  marker.style.setProperty('z-index', '999999999', 'important')

  contrast.style.setProperty('width', '3px', 'important')
  contrast.style.setProperty('height', '3px', 'important')
  contrast.style.setProperty('margin', '3px 0', 'important')
  contrast.style.setProperty('background', 'rgb(255,255,255)', 'important')

  const transform = {value: 'none', important: true}
  const html = __setElementStyleProperties([
    document.documentElement,
    {transform, '-webkit-transform': transform},
  ])
  const body = __setElementStyleProperties([
    document.body,
    {transform, '-webkit-transform': transform},
  ])

  document.documentElement.setAttribute('data-applitools-original-transforms', JSON.stringify(html))
  document.body.setAttribute('data-applitools-original-transforms', JSON.stringify(body))
}
""",
)

_CLEANUP_PAGE_MARKER_JS = "{} {} return __cleanupPageMarker()".format(
    _SET_ELEMENT_STYLE_PROPERTIES_JS,
    """
function __cleanupPageMarker() {
  const marker = document.querySelector('[data-applitools-marker]')
  if (marker) document.body.removeChild(marker)
  const html = document.documentElement.getAttribute('data-applitools-original-transforms')
  const body = document.body.getAttribute('data-applitools-original-transforms')
  if (html) __setElementStyleProperties([document.documentElement, JSON.parse(html)])
  if (body) __setElementStyleProperties([document.body, JSON.parse(body)])
}
""",
)
