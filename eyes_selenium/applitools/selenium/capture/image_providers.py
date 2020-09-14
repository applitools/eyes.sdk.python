import collections
import typing

import attr

from applitools.common import RectangleSize, Region, logger
from applitools.common.utils import image_utils
from applitools.core.capture import ImageProvider
from applitools.selenium.positioning import ScrollPositionProvider
from applitools.selenium.useragent import BrowserNames, OSNames, UserAgent

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
    _devices_regions = None

    _eyes = attr.ib()  # type: SeleniumEyes
    _useragent = attr.ib()  # type: UserAgent

    def get_image(self):
        image = TakesScreenshotImageProvider(self._eyes).get_image()

        if self._eyes.is_cut_provider_explicitly_set:
            return image

        # original_viewport_size = self._eyes._get_viewport_size()
        # FIXME: huck to get correct viewport size on mobile
        original_viewport_size = RectangleSize.from_(
            self._eyes.scroll_root_element.size_and_borders.size
        )
        logger.info("logical viewport size: {}".format(original_viewport_size))

        if self._devices_regions is None:
            self.init_device_regions_table()

        logger.info(
            "physical device pixel size: {} x {}".format(image.width, image.height)
        )

        device_data = DeviceData(
            image.width,
            image.height,
            original_viewport_size.width,
            original_viewport_size.height,
        )
        if device_data in self._devices_regions:
            logger.debug("device model found in hash table")
            crop_by_version = self._devices_regions.get(device_data)
            if crop_by_version.major_version <= self._useragent.browser_major_version:
                image = image_utils.crop_image(image, crop_by_version.region)
            else:
                logger.debug(
                    "device version not found in list. returning original image."
                )
        else:
            logger.debug("device not found in list. returning original image.")
        return image

    def init_device_regions_table(self):
        r_v = collections.namedtuple("RegionAndVersion", "major_version region")
        self._devices_regions = {
            DeviceData(828, 1792, 414, 719): r_v(12, Region(0, 189, 828, 1436)),
            DeviceData(1792, 828, 808, 364): r_v(12, Region(88, 101, 1616, 685)),
            DeviceData(1242, 2688, 414, 719): r_v(12, Region(0, 283, 1242, 2155)),
            DeviceData(2688, 1242, 808, 364): r_v(12, Region(132, 151, 2424, 1028)),
            DeviceData(1125, 2436, 375, 635): r_v(11, Region(0, 283, 1125, 1903)),
            DeviceData(2436, 1125, 724, 325): r_v(11, Region(132, 151, 2436, 930)),
            DeviceData(1242, 2208, 414, 622): r_v(11, Region(0, 211, 1242, 1863)),
            DeviceData(2208, 1242, 736, 364): r_v(11, Region(0, 151, 2208, 1090)),
            DeviceData(1242, 2208, 414, 628): r_v(10, Region(0, 193, 1242, 1882)),
            DeviceData(2208, 1242, 736, 337): r_v(10, Region(0, 231, 2208, 1010)),
            DeviceData(750, 1334, 375, 553): r_v(11, Region(0, 141, 750, 1104)),
            DeviceData(1334, 750, 667, 325): r_v(11, Region(0, 101, 1334, 648)),
            DeviceData(750, 1334, 375, 559): r_v(10, Region(0, 129, 750, 1116)),
            DeviceData(1334, 750, 667, 331): r_v(10, Region(0, 89, 1334, 660)),
            DeviceData(640, 1136, 320, 460): r_v(10, Region(0, 129, 640, 918)),
            DeviceData(1136, 640, 568, 232): r_v(10, Region(0, 89, 1136, 462)),
            DeviceData(1536, 2048, 768, 954): r_v(11, Region(0, 141, 1536, 1907)),
            DeviceData(2048, 1536, 1024, 698): r_v(11, Region(0, 141, 2048, 1395)),
            DeviceData(1536, 2048, 768, 922): r_v(11, Region(0, 206, 1536, 1842)),
            DeviceData(2048, 1536, 1024, 666): r_v(11, Region(0, 206, 2048, 1330)),
            DeviceData(1536, 2048, 768, 960): r_v(10, Region(0, 129, 1536, 1919)),
            DeviceData(2048, 1536, 1024, 704): r_v(10, Region(0, 129, 2048, 1407)),
            DeviceData(1536, 2048, 768, 928): r_v(10, Region(0, 194, 1536, 1854)),
            DeviceData(2048, 1536, 1024, 672): r_v(10, Region(0, 194, 2048, 1342)),
            DeviceData(2048, 2732, 1024, 1296): r_v(11, Region(0, 141, 2048, 2591)),
            DeviceData(2732, 2048, 1366, 954): r_v(11, Region(0, 141, 2732, 1907)),
            DeviceData(1668, 2224, 834, 1042): r_v(11, Region(0, 141, 1668, 2083)),
            DeviceData(2224, 1668, 1112, 764): r_v(11, Region(0, 141, 2224, 1527)),
        }


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
