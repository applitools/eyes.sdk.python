import typing

from applitools.common import logger
from applitools.common.utils import image_utils
from applitools.core.capture import ImageProvider
from applitools.selenium.useragent import BrowserNames, UserAgent

if typing.TYPE_CHECKING:
    from PIL.Image import Image
    from applitools.selenium.selenium_eyes import SeleniumEyes
    from applitools.selenium.webdriver import EyesWebDriver


def get_image_provider(ua, eyes):
    # type: (UserAgent, SeleniumEyes) -> ImageProvider
    if ua:
        if ua.browser == BrowserNames.Firefox:
            if ua.browser_major_version >= 48:
                return FirefoxScreenshotImageProvider(eyes)
        elif ua.browser == BrowserNames.Safari:
            return SafariScreenshotImageProvider(eyes)
    return TakesScreenshotImageProvider(eyes)


class SafariScreenshotImageProvider(ImageProvider):
    def get_image(self):
        # TODO: Update implementation
        return TakesScreenshotImageProvider(self._eyes).get_image()


class TakesScreenshotImageProvider(ImageProvider):
    def get_image(self):
        # type: () -> Image
        logger.info("Getting screenshot as base64...")
        screenshot64 = self._eyes.driver.get_screenshot_as_base64()
        logger.info("Done getting base64! Creating BufferedImage...")
        return image_utils.image_from_base64(screenshot64)


class FirefoxScreenshotImageProvider(ImageProvider):
    def get_image(self):
        driver = self._eyes.driver  # type: EyesWebDriver
        fc = driver.frame_chain.clone()
        logger.info("frameChain size: {}".format(fc.size))
        logger.info("Switching temporarily to default content.")
        driver.switch_to.default_content()

        logger.info("Getting screenshot as base64.")
        screenshot64 = driver.get_screenshot_as_base64()
        logger.info("Done getting base64! Creating BufferedImage...")

        image = image_utils.image_from_base64(screenshot64)
        logger.info("Done. Switching back to original frame.")
        driver.switch_to.frames(fc)
        return image
