from mock import Mock

from applitools.common.accessibility import AccessibilityRegionType
from applitools.common.geometry import AccessibilityRegion, Region
from applitools.core import CheckSettings


def test_set_get_use_dom():
    cs = CheckSettings().use_dom(True)
    assert cs.values.use_dom


def test_set_get_send_dom():
    cs = CheckSettings().send_dom(True)
    assert cs.values.send_dom


def test_set_get_enable_patterns():
    cs = CheckSettings().enable_patterns(True)
    assert cs.values.enable_patterns


def test_set_get_ignore_displacements():
    cs = CheckSettings().ignore_displacements(True)
    assert cs.values.ignore_displacements
    cs = cs.layout().ignore_displacements(False)
    assert not cs.values.ignore_displacements


def test_set_get_accessibility_regions():
    cs = CheckSettings().accessibility(
        AccessibilityRegion(1, 2, 3, 4, AccessibilityRegionType.LargeText)
    )
    assert cs.values.accessibility_regions[0].get_regions(Mock(), Mock()) == [
        AccessibilityRegion(1, 2, 3, 4, AccessibilityRegionType.LargeText)
    ]
    cs = CheckSettings().accessibility(
        Region(1, 2, 3, 4), AccessibilityRegionType.LargeText
    )
    assert cs.values.accessibility_regions[0].get_regions(Mock(), Mock()) == [
        AccessibilityRegion(1, 2, 3, 4, AccessibilityRegionType.LargeText)
    ]
