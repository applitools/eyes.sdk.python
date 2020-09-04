from typing import TYPE_CHECKING

from applitools.common import logger
from applitools.common.utils import argument_guard, image_utils
from applitools.core.locators import (
    LOCATORS_TYPE,
    VisualLocatorsData,
    VisualLocatorSettings,
    VisualLocatorsProvider,
)

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import AnyWebDriver
    from applitools.core import ServerConnector
    from applitools.core.debug import DebugScreenshotsProvider
    from applitools.selenium.selenium_eyes import SeleniumEyes


class SeleniumVisualLocatorsProvider(VisualLocatorsProvider):
    def __init__(self, driver, eyes):
        # type: (AnyWebDriver, SeleniumEyes) -> None
        self._driver = driver
        self._eyes = eyes
        self._server_connector = eyes._server_connector  # type: ServerConnector
        self._debug_screenshot_provider = (
            eyes.debug_screenshots_provider
        )  # type: DebugScreenshotsProvider

    def _get_viewport_screenshot(self):
        scale_provider = self._eyes.update_scaling_params()
        return self._eyes.get_scaled_cropped_viewport_image(scale_provider)

    def get_locators(self, visual_locator_settings):
        # type: (VisualLocatorSettings) -> LOCATORS_TYPE
        argument_guard.not_none(visual_locator_settings)

        logger.info(
            "Get locators with given names: {}".format(visual_locator_settings.names)
        )
        logger.info("Requested viewport screenshot for visual locators..")
        viewport_screenshot = self._get_viewport_screenshot()
        self._debug_screenshot_provider.save(
            viewport_screenshot,
            "Visual locators: {}".format(visual_locator_settings.names),
        )
        image = image_utils.get_bytes(viewport_screenshot)
        logger.info("Post visual locators screenshot...")
        viewport_screenshot_url = self._server_connector.try_upload_image(image)

        logger.info("Screenshot URL: {}".format(viewport_screenshot_url))
        data = VisualLocatorsData(
            app_name=self._eyes.configure.app_name,
            image_url=viewport_screenshot_url,
            first_only=visual_locator_settings.values.is_first_only,
            locator_names=visual_locator_settings.values.names,
        )
        logger.info("Post visual locators: {}".format(data))
        return self._server_connector.post_locators(data)
