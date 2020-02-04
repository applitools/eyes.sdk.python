import json

import pytest

from applitools.common import MatchLevel, ExactMatchSettings, ImageMatchSettings
from applitools.common.utils import json_utils
from applitools.core import MatchWindowTask
from applitools.core.test_eyes import TestEyes
from applitools.selenium import Target


@pytest.fixture
def eyes():
    return TestEyes()


def pytest_generate_tests(metafunc):
    if "use_dom" in metafunc.fixturenames:
        metafunc.parametrize("use_dom", [True, False])
    if "ignore_displacements" in metafunc.fixturenames:
        metafunc.parametrize("ignore_displacements", [True, False])
    if "enable_patterns" in metafunc.fixturenames:
        metafunc.parametrize("enable_patterns", [True, False])
    if "match_level" in metafunc.fixturenames:
        metafunc.parametrize(
            "match_level",
            [MatchLevel.CONTENT, MatchLevel.EXACT, MatchLevel.LAYOUT, MatchLevel.NONE],
        )


def test_fluent_info_api_serialization(
    use_dom, enable_patterns, ignore_displacements, match_level, eyes, screenshot
):
    settings = (
        Target.window()
        .fully()
        .use_dom(use_dom)
        .enable_patterns(enable_patterns)
        .ignore_displacements(ignore_displacements)
        .match_level(match_level)
    )
    image_match_settings = MatchWindowTask.create_image_match_settings(settings, eyes)
    assert image_match_settings.match_level == match_level
    assert image_match_settings.use_dom == use_dom
    assert image_match_settings.enable_patterns == enable_patterns
    assert image_match_settings.ignore_displacements == ignore_displacements
    assert image_match_settings.ignore_regions == []
    assert image_match_settings.strict_regions == []
    # assert image_match_settings.accessibility == []
    assert image_match_settings.layout_regions == []
    assert image_match_settings.content_regions == []
    assert image_match_settings.floating_match_settings == []

    serialized_img = json.loads(json_utils.to_json(image_match_settings))
    assert serialized_img["matchLevel"] == match_level.value
    assert serialized_img["useDom"] == use_dom
    assert serialized_img["enablePatterns"] == enable_patterns
    assert serialized_img["ignoreDisplacements"] == ignore_displacements
    assert serialized_img["Ignore"] == []
    assert serialized_img["Layout"] == []
    assert serialized_img["Strict"] == []
    assert serialized_img["Content"] == []
    assert serialized_img["Floating"] == []
    # assert serialized_img["accessibility"] == []


def test_image_match_settings_serialization(
    use_dom, enable_patterns, ignore_displacements, match_level, eyes, screenshot
):
    settings = (
        Target.window()
        .fully()
        .use_dom(use_dom)
        .enable_patterns(enable_patterns)
        .ignore_displacements(ignore_displacements)
        .match_level(match_level)
    )
    exact_match_settings = ExactMatchSettings()
    exact_match_settings.match_threshold = 0.5
    eyes.configure.default_match_settings = ImageMatchSettings(
        match_level=MatchLevel.EXACT, exact=exact_match_settings, use_dom=use_dom
    )
    image_match_settings = MatchWindowTask.create_image_match_settings(settings, eyes)
    assert image_match_settings.match_level == match_level
    assert image_match_settings.use_dom == use_dom
    assert image_match_settings.enable_patterns == enable_patterns
    assert image_match_settings.ignore_displacements == ignore_displacements
    assert (
        image_match_settings.exact.match_threshold
        == exact_match_settings.match_threshold
    )

    serialized_img = json.loads(json_utils.to_json(image_match_settings))
    assert serialized_img["matchLevel"] == match_level.value
    assert serialized_img["useDom"] == use_dom
    assert serialized_img["enablePatterns"] == enable_patterns
    assert serialized_img["ignoreDisplacements"] == ignore_displacements
    assert (
        serialized_img["exact"]["minDiffIntensity"]
        == exact_match_settings.min_diff_intensity
    )
    assert (
        serialized_img["exact"]["minDiffWidth"] == exact_match_settings.min_diff_width
    )
    assert (
        serialized_img["exact"]["minDiffHeight"] == exact_match_settings.min_diff_height
    )
    assert (
        serialized_img["exact"]["matchThreshold"]
        == exact_match_settings.match_threshold
    )
    assert serialized_img["Ignore"] is None
    assert serialized_img["Layout"] is None
    assert serialized_img["Strict"] is None
    assert serialized_img["Content"] is None
    assert serialized_img["Floating"] is None
    # assert serialized_img["accessibility"] == []


def test_configuration_serialization(eyes, screenshot):
    settings = Target.window().fully()
    config = eyes.get_configuration()
    config.use_dom = True
    config.enable_patterns = True
    config.ignore_displacements = True
    eyes.set_configuration(config)

    image_match_settings = MatchWindowTask.create_image_match_settings(
        settings, eyes, screenshot
    )
    assert image_match_settings.use_dom
    assert image_match_settings.enable_patterns
    assert image_match_settings.ignore_displacements

    serialized_img = json.loads(json_utils.to_json(image_match_settings))
    assert serialized_img["useDom"]
    assert serialized_img["enablePatterns"]
    assert serialized_img["ignoreDisplacements"]
