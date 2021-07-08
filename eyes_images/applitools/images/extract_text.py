from typing import TYPE_CHECKING, List, Optional, Text, Union

from PIL import Image

from applitools.common import AppOutput, Region
from applitools.common.utils import image_utils
from applitools.core import TextRegionSettings as TextRegionSettingsBase
from applitools.core.extract_text import (
    PATTERN_TEXT_REGIONS,
    BaseOCRRegion,
    ExpectedTextRegion,
    ExtractTextProvider,
    TextSettingsData,
)

if TYPE_CHECKING:
    from .eyes import Eyes


class OCRRegion(BaseOCRRegion):
    def __init__(self, image, region_in_image=None):
        # type: (Union[Image.Image, Text], Optional[Region]) -> None
        super(OCRRegion, self).__init__(image)
        self._image = image_utils.image_from_path(image)
        if region_in_image is None:
            region_in_image = Region.from_(self._image)
        self._region = region_in_image

    @property
    def image(self):
        # type: () -> Image.Image
        return self._image

    @property
    def expected_text_region(self):
        return ExpectedTextRegion(
            self._region.left,
            self._region.top,
            self._region.width,
            self._region.height,
            self._hint,
        )


class TextRegionSettings(TextRegionSettingsBase):
    def __init__(self, *patterns):
        # type: (*Union[Text, List[Text]]) -> None
        super(TextRegionSettings, self).__init__(*patterns)
        self._image = None

    def image(self, image):
        # type: (Union[Image.Image, Text]) -> TextRegionSettings
        cloned = self._clone()
        cloned._image = image_utils.image_from_path(image)
        return cloned


class ImagesExtractTextProvider(ExtractTextProvider):
    def __init__(self, eyes):
        # type: (Eyes) -> None
        self._eyes = eyes
        self._server_connector = eyes.server_connector

    def get_text(self, *regions):
        # type: (*OCRRegion) -> List[Text]
        results = []
        for ocr_region in regions:
            image = ocr_region.image
            screenshot_url = self._server_connector.try_upload_image(
                image_utils.get_bytes(image)
            )
            data = TextSettingsData(
                app_output=AppOutput(
                    screenshot_url=screenshot_url,
                ),
                language=ocr_region._language,
                min_match=ocr_region._min_match,
                regions=[ocr_region.expected_text_region],
            )
            result = self._server_connector.get_text_in_running_session_image(data)
            results.extend(result)
        return results

    def get_text_regions(self, config):
        # type: (TextRegionSettings) -> PATTERN_TEXT_REGIONS
        image = image_utils.get_bytes(config._image)
        screenshot_url = self._server_connector.try_upload_image(image)
        data = TextSettingsData(
            app_output=AppOutput(
                screenshot_url=screenshot_url,
            ),
            patterns=config._patterns,
            language=config._language,
            first_only=config.is_first_only,
            ignore_case=config._ignore_case,
        )
        return self._server_connector.get_text_regions_in_running_session_image(data)
