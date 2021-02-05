import os
from os import path

import pytest
from PIL import Image, ImageDraw

from applitools.images import (
    AccessibilityGuidelinesVersion,
    AccessibilityLevel,
    AccessibilityRegion,
    AccessibilityRegionType,
    AccessibilitySettings,
    Eyes,
    Region,
    Target,
    UnscaledFixedCutProvider,
)
from tests.functional.conftest import check_image_match_settings

here = path.abspath(path.dirname(__file__))


def test_check_image(eyes):
    # type: (Eyes) -> None
    eyes.open("images", "TestCheckImage", dimension=dict(width=100, height=400))
    eyes.check_image(path.join(here, "resources/minions-800x500.jpg"))
    eyes.close()


def test_check_image_path_fluent(eyes):
    # type: (Eyes) -> None
    eyes.open("images", "TestCheckImage_Fluent")
    eyes.check(
        "TestCheckImage_Fluent",
        Target.image(path.join(here, "resources/minions-800x500.jpg")),
    )
    eyes.close()


def test_check_raw_image_fluent(eyes):
    # type: (Eyes) -> None
    eyes.open("images", "TestCheckImage_Fluent")
    origin_image = Image.new("RGBA", (600, 600))
    eyes.check("TestCheckImage_Fluent", Target.image(origin_image))
    eyes.close()


def test_check_region(eyes):
    # type: (Eyes) -> None
    eyes.open("images", "TestCheckRegion")
    eyes.check_region(
        path.join(here, "resources/minions-800x500.jpg"),
        Region(left=200, top=100, width=400, height=400),
    )
    eyes.close()


def test_check_region_fluent(eyes):
    # type: (Eyes) -> None
    eyes.open("images", "TestCheckRegion_Fluent")
    eyes.check(
        Target.region(
            path.join(here, "resources/minions-800x500.jpg"),
            Region(left=200, top=100, width=400, height=400),
        )
    )
    eyes.close()


def test_check_raw_image_delete_result(eyes):
    # type: (Eyes) -> None
    eyes.open("images", "TestCheckImage_DeleteResult")
    origin_image = Image.new("RGBA", (600, 600))
    eyes.check("TestCheckImage_Fluent", Target.image(origin_image))
    result = eyes.close(False)
    result.delete()


def test_check_raw_image_fluent_must_fail(eyes):
    # type: (Eyes) -> None
    eyes.open("images", "TestCheckImage_Fluent")
    origin_image = Image.new("RGBA", (600, 600))
    draw = ImageDraw.Draw(origin_image)
    draw.rectangle(((0, 00), (500, 100)), fill="white")
    eyes.check("TestCheckImage_Fluent", Target.image(origin_image))
    with pytest.raises(Exception):
        eyes.close()


def test_check_image_with_ignore_region_fluent(eyes):
    # type: (Eyes) -> None
    eyes.open("images", "TestCheckImageWithIgnoreRegion_Fluent")
    eyes.check(
        "TestCheckImage_WithIgnoreRegion_Fluent",
        Target.image(path.join(here, "resources/minions-800x500.jpg")).ignore(
            Region(10, 20, 30, 40)
        ),
    )
    eyes.close()


def test_check_image_fluent_cut_provider(eyes):
    # type: (Eyes) -> None
    eyes.open("images", "TestCheckImage_Fluent_CutProvider")
    eyes.cut_provider = UnscaledFixedCutProvider(200, 100, 100, 50)
    eyes.check(
        "TestCheckImage_Fluent",
        Target.image(path.join(here, "resources/minions-800x500.jpg")),
    )
    eyes.close()


def test_check_image_fluent_accessibility(eyes):
    (
        eyes.configure.set_accessibility_validation(
            AccessibilitySettings(
                AccessibilityLevel.AA, AccessibilityGuidelinesVersion.WCAG_2_1
            )
        )
    )
    eyes.open("images", "TestCheckImage_Fluent_Accessibility")
    eyes.check(
        "TestCheckImage_Fluent",
        Target.image(path.join(here, "resources/minions-800x500.jpg")).accessibility(
            Region(10, 25, 200, 100), AccessibilityRegionType.GraphicalObject
        ),
    )
    test_result = eyes.close(False)
    check_image_match_settings(
        eyes,
        test_result,
        [
            {
                "actual_name": "accessibility",
                "expected": [
                    AccessibilityRegion(
                        10, 25, 200, 100, AccessibilityRegionType.GraphicalObject
                    )
                ],
            },
            {
                "actual_name": "accessibilitySettings",
                "expected": AccessibilitySettings(
                    AccessibilityLevel.AA, AccessibilityGuidelinesVersion.WCAG_2_1
                ),
            },
        ],
    )
