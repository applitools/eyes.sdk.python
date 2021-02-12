from typing import TYPE_CHECKING, List, Optional, Text, Union

from applitools.common import AppOutput, Point, Region
from applitools.common.utils import argument_guard, image_utils
from applitools.core import ServerConnector
from applitools.core.debug import DebugScreenshotsProvider
from applitools.core.text_regions import (
    PATTERN_TEXT_REGIONS,
    BaseOCRRegion,
    ExpectedTextRegion,
    TextRegionProvider,
    TextRegionSettings,
    TextSettingsData,
)
from applitools.selenium import eyes_selenium_utils
from applitools.selenium.fluent import SeleniumCheckSettings, Target
from applitools.selenium.selenium_eyes import SeleniumEyes

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import (
        AnyWebDriver,
        AnyWebElement,
        CssSelector,
    )


class OCRRegion(BaseOCRRegion):
    def __init__(self, target, hint="", language="eng", min_match=None):
        # type:(Union[Region,CssSelector,AnyWebElement],Text,Text,Optional[float])->None
        super(OCRRegion, self).__init__(target, hint, language, min_match)


class SeleniumTextRegionProvider(TextRegionProvider):
    def __init__(self, driver, eyes):
        # type: (AnyWebDriver, SeleniumEyes) -> None
        self._driver = driver
        self._eyes = eyes
        self._server_connector = eyes.server_connector  # type: ServerConnector
        self._debug_screenshot_provider = (
            eyes.debug_screenshots_provider
        )  # type: DebugScreenshotsProvider

    def _process_app_output(self, ocr_region):
        check_settings = SeleniumCheckSettings().fully()
        check_settings.values.ocr_region = ocr_region

        check_settings = check_settings.region(ocr_region.target)

        def process_app_output(check_settings, region):
            if not check_settings.values.target_region:
                element = eyes_selenium_utils.get_element_from_check_settings(
                    self._driver, check_settings
                )
                ocr_region.hint = eyes_selenium_utils.get_inner_text(
                    self._driver, element
                )
            app_output = self._eyes._app_output_provider.get_app_output(
                region, self._eyes._last_screenshot, check_settings
            )
            ocr_region.app_output_with_screenshot = app_output
            ocr_region.app_output = app_output.app_output
            ocr_region.regions.append(
                ExpectedTextRegion(
                    0,
                    0,
                    width=app_output.screenshot.image.width,
                    height=app_output.screenshot.image.height,
                    expected=ocr_region.hint,
                )
            )

        ocr_region.add_process_app_output(process_app_output)
        self._eyes.check(check_settings)

    def _get_viewport_screenshot_url(self):
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
        # type: (*OCRRegion) -> List[Text]
        result = []
        for ocr_region in regions:
            self._process_app_output(ocr_region)
            screenshot_url = self._server_connector.try_upload_image(
                image_utils.get_bytes(
                    ocr_region.app_output_with_screenshot.screenshot.image
                )
            )
            ocr_region.app_output_with_screenshot.app_output.screenshot_url = (
                screenshot_url
            )
            result.extend(self._server_connector.extract_text(ocr_region))
        return result

    def get_text_regions(self, config):
        # type: (TextRegionSettings) -> PATTERN_TEXT_REGIONS
        argument_guard.not_none(config.values.patterns)
        screenshot_url = self._get_viewport_screenshot_url()
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
