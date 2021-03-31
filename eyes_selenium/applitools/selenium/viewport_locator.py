import typing

if typing.TYPE_CHECKING:
    from applitools.common.utils.custom_types import AnyWebDriver


def add_page_marker(driver, pixel_ratio):
    # type: (AnyWebDriver, float) -> dict
    driver.execute_script(_ADD_PAGE_MARKER_JS)
    return {
        "offset": 1 * pixel_ratio,
        "size": 3 * pixel_ratio,
        "mask": [0, 1, 0],
    }


def remove_page_marker(driver):
    # type: (AnyWebDriver) -> None
    driver.execute_script(_CLEANUP_PAGE_MARKER_JS)


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
