from __future__ import division

import typing
from math import floor

import attr

from applitools.common import Point

if typing.TYPE_CHECKING:
    from typing import List, Optional

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
    for pixel in range(image.width * image.height):
        if _is_pattern(image, pixel, pattern):
            return Point(
                pixel % image.width - pattern.offset,
                floor(pixel // image.width) - pattern.offset,
            )


def _is_pattern(image, index, pattern):
    # type: (Image, int, Pattern) -> bool
    round_number = pattern.size - pattern.size // 2
    for chunk_index, chunk_color in enumerate(pattern.mask):
        pixel_offset = index + image.width * pattern.size * chunk_index
        for round in range(round_number):
            side_length = pattern.size - round * 2
            steps_number = side_length * 4 - 4
            threshold = min((round_number - round) * 10 + 10, 100)
            for step in range(steps_number):
                pixel_index = pixel_offset + round + round * image.width
                if step < side_length:
                    pixel_index += step
                elif step < side_length * 2 - 1:
                    pixel_index += (
                        side_length - 1 + ((step % side_length + 1)) * image.width
                    )
                elif step < side_length * 3 - 2:
                    pixel_index += (side_length - 1) * image.width + (
                        side_length - (step % side_length) - 1
                    )
                else:
                    pixel_index += (step % side_length) * image.width
                pixel_color = _pixel_color_at(image, pixel_index, threshold)
                if pixel_color != chunk_color:
                    return False
    return True


def _pixel_color_at(image, pixel_index, threshold):
    # type: (Image, int, int) -> int
    xy = pixel_index % image.width, pixel_index // image.width
    components = image.getpixel(xy)
    # White
    if all(c >= 255 - threshold for c in components):
        return 1
    elif all(c <= threshold for c in components):
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
