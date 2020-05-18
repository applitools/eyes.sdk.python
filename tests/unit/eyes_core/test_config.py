import pytest

from applitools.common import Configuration, MatchLevel
from applitools.common.accessibility import (
    AccessibilitySettings,
    AccessibilityLevel,
    AccessibilityGuidelinesVersion,
)


@pytest.fixture
def config():
    return Configuration()


def test_set_get_values_present_in_image_match_settings(config):
    config.match_level = MatchLevel.LAYOUT
    assert config.match_level == MatchLevel.LAYOUT
    assert config.default_match_settings.match_level == MatchLevel.LAYOUT

    config.set_ignore_caret(True)
    assert config.ignore_caret
    assert config.default_match_settings.ignore_caret

    config.use_dom = True
    assert config.use_dom
    assert config.default_match_settings.use_dom

    config.enable_patterns = True
    assert config.enable_patterns
    assert config.default_match_settings.enable_patterns

    config.ignore_displacements = True
    assert config.ignore_displacements
    assert config.default_match_settings.ignore_displacements

    a_setting = AccessibilitySettings(
        AccessibilityLevel.AA, AccessibilityGuidelinesVersion.WCAG_2_1
    )
    assert config.accessibility_validation is None
    config.accessibility_validation = a_setting
    assert config.accessibility_validation == a_setting
    assert config.default_match_settings.accessibility_settings == a_setting
