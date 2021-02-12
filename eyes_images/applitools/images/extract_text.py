from typing import TYPE_CHECKING, List, Text, Union

from PIL import Image

from applitools.common import AppOutput, Point
from applitools.common.utils import image_utils
from applitools.core import TextRegionSettings as TextRegionSettingsBase
from applitools.core.extract_text import (
    BaseOCRRegion,
    ExpectedTextRegion,
    ExtractTextProvider,
    TextSettingsData,
)

if TYPE_CHECKING:
    from .eyes import Eyes


class OCRRegion(BaseOCRRegion):
    def __init__(self, target):
        # type: (Union[Image.Image, Text]) -> None
        super(OCRRegion, self).__init__(target)


class TextRegionSettings(TextRegionSettingsBase):
    def __init__(self, *patterns):
        # type: (*Union[Text, List[Text]]) -> None
        super(TextRegionSettings, self).__init__(*patterns)
        self._image = None

    def image(self, image):
        # type: (Union[Image.Image, Text]) -> TextRegionSettings
        cloned = self.clone()
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
            image = image_utils.image_from_path(ocr_region.target)
            screenshot_url = self._server_connector.try_upload_image(
                image_utils.get_bytes(image)
            )
            data = TextSettingsData(
                app_output=AppOutput(
                    screenshot_url=screenshot_url,
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
            result = self._server_connector.extract_text(data)
            results.extend(result)
        return results

    def get_text_regions(self, config):
        # type: (TextRegionSettings) -> List[Text]
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
        return self._server_connector.extract_text_regions(data)
