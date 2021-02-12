from typing import TYPE_CHECKING, Callable, List, Optional, Text, Union

from applitools.common import AppOutput, Point, Region
from applitools.common.utils import argument_guard, image_utils
from applitools.core import AppOutputWithScreenshot, ServerConnector
from applitools.core.debug import DebugScreenshotsProvider
from applitools.core.extract_text import (
    PATTERN_TEXT_REGIONS,
    BaseOCRRegion,
    ExpectedTextRegion,
    ExtractTextProvider,
    TextRegionSettings,
    TextSettingsData,
)
from applitools.selenium import eyes_selenium_utils
from applitools.selenium.fluent import SeleniumCheckSettings
from applitools.selenium.selenium_eyes import SeleniumEyes

if TYPE_CHECKING:
    from applitools.common.utils.custom_types import (
        AnyWebDriver,
        AnyWebElement,
        CssSelector,
    )
    from applitools.selenium import EyesWebDriver, EyesWebElement


def _element_from_check_settings(driver, check_settings):
    # type: (EyesWebDriver, SeleniumCheckSettings) -> EyesWebElement
    from .webelement import EyesWebElement

    if check_settings.values.target_element:
        element = check_settings.values.target_element
    elif check_settings.values.target_selector:
        by, value = check_settings.values.target_selector
        element = driver.find_element(by, value)
    else:
        raise ValueError
    return EyesWebElement(element, driver)


class OCRRegion(BaseOCRRegion):
    def __init__(self, target):
        # type:(Union[Region,CssSelector,AnyWebElement])->None
        super(OCRRegion, self).__init__(target)
        self.process_app_output = None  # type: Optional[Callable]
        self.app_output_with_screenshot = (
            None
        )  # type: Optional[AppOutputWithScreenshot]

    def add_process_app_output(self, callback):
        # type: (Callable) -> None
        if not callable(callback):
            raise ValueError
        self.process_app_output = callback


class SeleniumExtractTextProvider(ExtractTextProvider):
    def __init__(self, driver, eyes):
        # type: (AnyWebDriver, SeleniumEyes) -> None
        self._driver = driver
        self._eyes = eyes
        self._server_connector = eyes.server_connector  # type: ServerConnector
        self._debug_screenshot_provider = (
            eyes.debug_screenshots_provider
        )  # type: DebugScreenshotsProvider

    def _process_app_output(self, ocr_region):
        settings = SeleniumCheckSettings().fully()
        settings.values.ocr_region = ocr_region

        settings = settings.region(ocr_region.target)

        def app_output_callback(check_settings, region):
            if not check_settings.values.target_region:
                element = _element_from_check_settings(self._driver, check_settings)
                ocr_region.hint = eyes_selenium_utils.get_inner_text(
                    self._driver, element
                )
            app_output = self._eyes._app_output_provider.get_app_output(
                region, self._eyes._last_screenshot, check_settings
            )
            ocr_region.app_output_with_screenshot = app_output

        ocr_region.add_process_app_output(app_output_callback)
        self._eyes.check(settings)

    def get_text(self, *regions):
        # type: (*OCRRegion) -> List[Text]
        result = []
        for ocr_region in regions:
            self._process_app_output(ocr_region)
            image = ocr_region.app_output_with_screenshot.screenshot.image
            screenshot_url = self._server_connector.try_upload_image(
                image_utils.get_bytes(image)
            )
            data = TextSettingsData(
                app_output=AppOutput(
                    screenshot_url=screenshot_url,
                    location=Point.ZERO(),
                    dom_url=ocr_region.app_output_with_screenshot.app_output.dom_url,
                ),
                language=ocr_region._language,
                min_match=ocr_region._min_match,
                regions=[
                    ExpectedTextRegion(
                        0,
                        0,
                        width=image.width,
                        height=image.height,
                        expected=ocr_region._hint,
                    )
                ],
            )
            result.extend(
                self._server_connector.get_text_in_running_session_image(data)
            )
        return result

    def get_text_regions(self, config):
        # type: (TextRegionSettings) -> PATTERN_TEXT_REGIONS
        def get_app_output():
            scale_provider = self._eyes.update_scaling_params()
            viewport_screenshot = self._eyes.get_scaled_cropped_viewport_image(
                scale_provider
            )
            image = image_utils.get_bytes(viewport_screenshot)
            screenshot_url = self._server_connector.try_upload_image(image)

            dom_json = self._eyes._try_capture_dom()
            dom_url = self._eyes._try_post_dom_capture(dom_json)
            return AppOutput(
                dom_url=dom_url, screenshot_url=screenshot_url, location=Point.ZERO()
            )

        argument_guard.not_none(config._patterns)
        data = TextSettingsData(
            app_output=get_app_output(),
            patterns=config._patterns,
            ignore_case=config._ignore_case,
            first_only=config._first_only,
            language=config._language,
        )
        return self._server_connector.get_text_regions_in_running_session_image(data)
