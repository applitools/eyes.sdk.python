import typing

import attr

from applitools.common import Region, logger
from applitools.common.utils import image_utils
from applitools.core.capture import ImageProvider
from applitools.selenium.positioning import ScrollPositionProvider
from applitools.selenium.useragent import BrowserNames, UserAgent
from applitools.selenium.viewport_locator import device_viewport_location

if typing.TYPE_CHECKING:
    from PIL.Image import Image

    from applitools.selenium.frames import FrameChain
    from applitools.selenium.selenium_eyes import SeleniumEyes
    from applitools.selenium.webdriver import EyesWebDriver


def get_image_provider(ua, eyes):
    # type: (UserAgent, SeleniumEyes) -> ImageProvider
    if ua:
        if ua.browser == BrowserNames.Firefox:
            if ua.browser_major_version >= 48:
                return FirefoxScreenshotImageProvider(eyes)
        elif ua.browser == BrowserNames.Safari:
            return SafariScreenshotImageProvider(eyes, ua)
        elif ua.browser == BrowserNames.MobileSafari:
            return MobileSafariScreenshotImageProvider(eyes, ua)
    return TakesScreenshotImageProvider(eyes)


@attr.s(hash=False)
class DeviceData(object):
    width = attr.ib()
    height = attr.ib()
    vp_width = attr.ib()
    vp_height = attr.ib()

    def __hash__(self):
        return int(
            self.width * 100000
            + self.height * 1000
            + self.vp_width * 100
            + self.vp_height
        )


@attr.s
class MobileSafariScreenshotImageProvider(ImageProvider):
    _eyes = attr.ib()  # type: SeleniumEyes
    _useragent = attr.ib()  # type: UserAgent

    def get_image(self):
        image = TakesScreenshotImageProvider(self._eyes).get_image()

        if self._eyes.is_cut_provider_explicitly_set:
            return image

        logger.info(
            "physical device pixel size", width=image.width, height=image.height
        )

        viewport_location = device_viewport_location(self._eyes.driver)
        original_viewport_size = self._eyes._get_viewport_size()
        viewport_size = original_viewport_size.scale(self._eyes.device_pixel_ratio)
        crop_region = Region(
            viewport_location.x,
            viewport_location.y,
            viewport_size.width,
            viewport_size.height,
        )
        logger.info("calculated viewport region", viewport_region=crop_region)
        image = image_utils.crop_image(image, crop_region)

        return image


@attr.s
class SafariScreenshotImageProvider(ImageProvider):
    _eyes = attr.ib()  # type: SeleniumEyes
    _useragent = attr.ib()  # type: UserAgent

    def get_image(self):
        image = TakesScreenshotImageProvider(self._eyes).get_image()

        if self._eyes.is_cut_provider_explicitly_set:
            return image

        scale_ratio = self._eyes.device_pixel_ratio
        original_viewport_size = self._eyes._get_viewport_size()
        viewport_size = original_viewport_size.scale(scale_ratio)

        logger.info("logical viewport size: {}".format(original_viewport_size))

        force_full_page_screenshot = self._eyes.configure.force_full_page_screenshot
        if force_full_page_screenshot is not None:
            if not force_full_page_screenshot:
                current_frame_chain = self._eyes.driver.frame_chain  # type: FrameChain

                if len(current_frame_chain) == 0:
                    position_provider = ScrollPositionProvider(
                        self._eyes.driver,
                        self._eyes.driver.find_element_by_tag_name("html"),
                    )
                    loc = position_provider.get_current_position()
                else:
                    loc = current_frame_chain.default_content_scroll_position

                loc = loc.scale(scale_ratio)
                image = image_utils.crop_image(image, Region.from_(loc, viewport_size))
        return image


class TakesScreenshotImageProvider(ImageProvider):
    def get_image(self):
        # type: () -> Image
        logger.debug("Getting screenshot as base64...")
        screenshot64 = self._eyes.driver.get_screenshot_as_base64()
        logger.debug("Done getting base64! Creating BufferedImage...")
        image = image_utils.image_from_base64(screenshot64)
        self._eyes.debug_screenshots_provider.save(image, "initial")
        return image


class FirefoxScreenshotImageProvider(ImageProvider):
    def get_image(self):
        driver = self._eyes.driver  # type: EyesWebDriver
        fc = driver.frame_chain.clone()
        logger.debug("frameChain size: {}".format(fc.size))
        logger.debug("Switching temporarily to default content.")
        driver.switch_to.default_content()

        logger.debug("Getting screenshot as base64.")
        screenshot64 = driver.get_screenshot_as_base64()
        logger.debug("Done getting base64! Creating BufferedImage...")

        image = image_utils.image_from_base64(screenshot64)
        logger.debug("Done. Switching back to original frame.")
        driver.switch_to.frames(fc)
        return image
