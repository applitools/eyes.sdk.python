from applitools.eyes_core import Region, UnscaledFixedCutProvider

from applitools.eyes_images import Target


def test_check_image(eyes):
    eyes.check_image('resources/minions-800x500.jpg')


def test_check_image_fluent(eyes):
    eyes.check("TestCheckImage_Fluent", Target.image("resources/minions-800x500.jpg"))


def test_check_image_with_ignore_region_fluent(eyes):
    eyes.check("TestCheckImage_WithIgnoreRegion_Fluent", Target.image("resources/minions-800x500.jpg")
               .ignore(Region(10, 20, 30, 40)))


def test_check_image_fluent_cut_provider(eyes):
    eyes.image_cut = UnscaledFixedCutProvider(200, 100, 100, 50)
    eyes.check("TestCheckImage_Fluent", Target.image("resources/minions-800x500.jpg"))
