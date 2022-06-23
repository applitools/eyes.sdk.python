import pytest
from mock import Mock

from applitools.common import MatchLevel
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


def test_give_incorrect_parameters_to_match_regions():
    with pytest.raises(TypeError) as exc_info:
        cs = CheckSettings().accessibility(1)
        assert exc_info.type == TypeError
    with pytest.raises(TypeError) as exc_info:
        cs = CheckSettings().layout(1)
        assert exc_info.type == TypeError
    with pytest.raises(TypeError) as exc_info:
        cs = CheckSettings().content(1)
        assert exc_info.type == TypeError
    with pytest.raises(TypeError) as exc_info:
        cs = CheckSettings().strict(1)
        assert exc_info.type == TypeError
    with pytest.raises(TypeError) as exc_info:
        cs = CheckSettings().floating(1)
        assert exc_info.type == TypeError


def test_set_match_regions_level():
    cs = CheckSettings().layout(Region.EMPTY())
    assert cs.values.match_level is None
    cs = cs.layout()
    assert cs.values.match_level == MatchLevel.LAYOUT

    cs = CheckSettings().content(Region.EMPTY())
    assert cs.values.match_level is None
    cs = cs.content()
    assert cs.values.match_level == MatchLevel.CONTENT

    cs = CheckSettings().strict(Region.EMPTY())
    assert cs.values.match_level is None
    cs = cs.strict()
    assert cs.values.match_level == MatchLevel.STRICT

    cs = CheckSettings().exact()
    assert cs.values.match_level == MatchLevel.EXACT
