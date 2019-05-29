import typing

import attr

from applitools.common import logger, Region
from applitools.common.utils import image_utils
from applitools.core.capture import ImageProvider
from applitools.selenium.positioning import ScrollPositionProvider
from applitools.selenium.useragent import BrowserNames, UserAgent, OSNames

if typing.TYPE_CHECKING:
    from PIL.Image import Image
    from applitools.selenium.selenium_eyes import SeleniumEyes
    from applitools.selenium.webdriver import EyesWebDriver
    from applitools.selenium.frames import FrameChain


def get_image_provider(ua, eyes):
    # type: (UserAgent, SeleniumEyes) -> ImageProvider
    if ua:
        if ua.browser == BrowserNames.Firefox:
            if ua.browser_major_version >= 48:
                return FirefoxScreenshotImageProvider(eyes)
        elif ua.browser == BrowserNames.Safari:
            return SafariScreenshotImageProvider(eyes, ua)
    return TakesScreenshotImageProvider(eyes)


@attr.s(hash=False)
class DeviceData(object):
    width = attr.ib()
    height = attr.ib()
    vp_width = attr.ib()
    vp_height = attr.ib()
    major_version = attr.ib()

    def __hash__(self):
        return (
            self.width * 100000
            + self.height * 1000
            + self.vp_width * 100
            + self.vp_height * 10
            + self.major_version
        )


@attr.s
class SafariScreenshotImageProvider(ImageProvider):
    _devices_regions = None

    _eyes = attr.ib()  # type: SeleniumEyes
    _useragent = attr.ib()  # type: UserAgent

    def get_image(self):
        image = TakesScreenshotImageProvider(self._eyes).get_image()
        self._eyes.debug_screenshot_provider.save(image, "SAFARI")

        if self._eyes.is_cut_provider_explicitly_set:
            return image

        scale_ratio = self._eyes.device_pixel_ratio
        original_viewport_size = self._eyes._get_viewport_size()
        viewport_size = original_viewport_size.scale(scale_ratio)

        logger.info("logical viewport size: {}".format(original_viewport_size))

        if self._useragent.os == OSNames.IOS:
            if self._devices_regions is None:
                self.init_device_regions_table()

            logger.info(
                "physical device pixel size: {} x {}".format(image.width, image.height)
            )

            device_delta = DeviceData(
                image.width,
                image.height,
                original_viewport_size.width,
                original_viewport_size.height,
                self._useragent.browser_major_version,
            )
            if device_delta in self._devices_regions:
                logger.debug("device model found in hash table")
                crop = self._devices_regions.get(device_delta)
                image = image_utils.crop_image(image, crop)
            else:
                logger.debug("device not found in list. returning original image.")
        elif not self._eyes.configuration.force_full_page_screenshot:
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
            image = image_utils.crop_image(
                image, Region.from_location_size(loc, viewport_size)
            )
        return image

    def init_device_regions_table(self):
        self._devices_regions = {
            DeviceData(1125, 2436, 375, 635, 11): Region(0, 283, 1125, 1903),
            DeviceData(2436, 1125, 724, 325, 11): Region(132, 151, 2436, 930),
            DeviceData(1242, 2208, 414, 622, 11): Region(0, 211, 1242, 1863),
            DeviceData(2208, 1242, 736, 364, 11): Region(0, 151, 2208, 1090),
            DeviceData(1242, 2208, 414, 628, 10): Region(0, 193, 1242, 1882),
            DeviceData(2208, 1242, 736, 337, 10): Region(0, 231, 2208, 1010),
            DeviceData(750, 1334, 375, 553, 11): Region(0, 141, 750, 1104),
            DeviceData(1334, 750, 667, 325, 11): Region(0, 101, 1334, 648),
            DeviceData(750, 1334, 375, 559, 10): Region(0, 129, 750, 1116),
            DeviceData(1334, 750, 667, 331, 10): Region(0, 89, 1334, 660),
            DeviceData(640, 1136, 320, 460, 10): Region(0, 129, 640, 918),
            DeviceData(1136, 640, 568, 232, 10): Region(0, 89, 1136, 462),
            DeviceData(1536, 2048, 768, 954, 11): Region(0, 141, 1536, 1907),
            DeviceData(2048, 1536, 1024, 698, 11): Region(0, 141, 2048, 1395),
            DeviceData(1536, 2048, 768, 922, 11): Region(0, 206, 1536, 1842),
            DeviceData(2048, 1536, 1024, 666, 11): Region(0, 206, 2048, 1330),
            DeviceData(1536, 2048, 768, 960, 10): Region(0, 129, 1536, 1919),
            DeviceData(2048, 1536, 1024, 704, 10): Region(0, 129, 2048, 1407),
            DeviceData(1536, 2048, 768, 928, 10): Region(0, 194, 1536, 1854),
            DeviceData(2048, 1536, 1024, 672, 10): Region(0, 194, 2048, 1342),
            DeviceData(2048, 2732, 1024, 1296, 11): Region(0, 141, 2048, 2591),
            DeviceData(2732, 2048, 1366, 954, 11): Region(0, 141, 2732, 1907),
            DeviceData(1668, 2224, 834, 1042, 11): Region(0, 141, 1668, 2083),
            DeviceData(2224, 1668, 1112, 764, 11): Region(0, 141, 2224, 1527),
        }


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
