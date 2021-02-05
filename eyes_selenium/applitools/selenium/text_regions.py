from typing import TYPE_CHECKING, Text

from applitools.common import AppOutput, Point, Region
from applitools.common.utils import argument_guard, image_utils
from applitools.core import ServerConnector
from applitools.core.debug import DebugScreenshotsProvider
from applitools.core.text_regions import (
    PATTERN_TEXT_REGIONS,
    OCRRegion,
    TextRegionSettings,
    TextRegionsProvider,
    TextSettingsData,
)
from applitools.selenium.selenium_eyes import SeleniumEyes

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import AnyWebDriver


class SeleniumTextRegionsProvider(TextRegionsProvider):
    def __init__(self, driver, eyes):
        # type: (AnyWebDriver, SeleniumEyes) -> None
        self._driver = driver
        self._eyes = eyes
        self._server_connector = eyes.server_connector  # type: ServerConnector
        self._debug_screenshot_provider = (
            eyes.debug_screenshots_provider
        )  # type: DebugScreenshotsProvider

    def _get_screenshot_url(self):
        scale_provider = self._eyes.update_scaling_params()
        viewport_screenshot = self._eyes.get_scaled_cropped_viewport_image(
            scale_provider
        )
        image = image_utils.get_bytes(viewport_screenshot)
        return self._server_connector.try_upload_image(image)

    def _get_dom_url(self):
        dom_json = self._eyes._try_capture_dom()
        return self._eyes._try_post_dom_capture(dom_json)

    def get_text(self, *regions):
        # type: (*OCRRegion) -> Text
        raise NotImplementedError
        # screenshot_url = self._get_screenshot_url()
        # dom_url = self._get_dom_url()
        # region = regions[0]
        # if region.hint is None and not isinstance(region.target, Region):
        #     pass

    def get_text_regions(self, config):
        # type: (TextRegionSettings) -> PATTERN_TEXT_REGIONS
        argument_guard.not_none(config.values.patterns)
        screenshot_url = self._get_screenshot_url()
        dom_url = self._get_dom_url()
        settings = TextSettingsData(
            app_output=AppOutput(
                dom_url=dom_url,
                screenshot_url=screenshot_url,
                location=Point.ZERO(),
            ),
            patterns=config.values.patterns,
            ignore_case=config.values.ignore_case,
            first_only=config.values.first_only,
            language=config.values.language,
        )
        return self._server_connector.extract_text_regions(settings)
