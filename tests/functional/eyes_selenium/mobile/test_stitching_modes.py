from applitools.selenium import StitchMode, Target


def test_eyes_mobile_scroll_stitching(sauce_iphone8_ios14_driver, eyes):
    sauce_iphone8_ios14_driver.get("https://demo.applitools.com/")
    eyes.stitch_mode = StitchMode.Scroll
    eyes.open(sauce_iphone8_ios14_driver, "Tests", "ios14 scroll stitching")

    eyes.check("step", Target.window().fully())

    eyes.close()


def test_eyes_mobile_css_stitching(sauce_iphone8_ios14_driver, eyes):
    sauce_iphone8_ios14_driver.get("https://demo.applitools.com/")
    eyes.stitch_mode = StitchMode.CSS
    eyes.open(sauce_iphone8_ios14_driver, "Tests", "ios14 css stitching")

    eyes.check("step", Target.window().fully())

    eyes.close()
