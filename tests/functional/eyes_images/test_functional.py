# from applitools.core import Region, UnscaledFixedCutProvider
from os import path

import pytest
from PIL import Image, ImageDraw

from applitools.images import Region, Target, UnscaledFixedCutProvider, Eyes

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
