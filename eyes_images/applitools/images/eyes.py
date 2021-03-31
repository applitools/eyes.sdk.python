import typing

from applitools.common import Configuration, EyesError, RectangleSize, Region, logger
from applitools.common.utils.compat import basestring
from applitools.common.utils.general_utils import all_fields, proxy_to
from applitools.core import (
    NULL_REGION_PROVIDER,
    EyesBase,
    NullCutProvider,
    RegionProvider,
)
from applitools.core.extract_text import PATTERN_TEXT_REGIONS
from applitools.images.fluent import ImagesCheckSettings, Target

from .__version__ import __version__
from .capture import EyesImagesScreenshot
from .extract_text import ImagesExtractTextProvider, OCRRegion, TextRegionSettings

if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional, Text, Union

    from PIL import Image

    from applitools.common.utils.custom_types import ViewPort


@proxy_to("configure", all_fields(Configuration))
class Eyes(EyesBase):
    _raw_title = None  # type: Optional[Text]
    _screenshot = None  # type: Optional[EyesImagesScreenshot]
    _inferred = None  # type: Optional[Text]
    _extract_text_provider = None  # type: Optional[ImagesExtractTextProvider]

    def _init_additional_providers(self):
        self._extract_text_provider = ImagesExtractTextProvider(self)

    @property
    def full_agent_id(self):
        # type: () -> Text
        if self.configure.agent_id is None:
            return self.base_agent_id
        return "%s [%s]" % (self.configure.agent_id, self.base_agent_id)

    @property
    def base_agent_id(self):
        # type: () -> Text
        return "eyes.images.python/{version}".format(version=__version__)

    @property
    def _title(self):
        return self._raw_title

    @property
    def _inferred_environment(self):
        # type: () -> Text
        if self._inferred:
            return self._inferred
        return ""

    def _get_viewport_size(self):
        # type: () -> RectangleSize
        return self.configure.viewport_size

    def _set_viewport_size(self, size):
        # type: (ViewPort) -> None
        self.configure.viewport_size = size  # type: ignore

    def _ensure_viewport_size(self):
        pass

    def _get_screenshot(self, **kwargs):
        # type: (**Dict) -> EyesImagesScreenshot
        return self._screenshot

    def _try_capture_dom(self):
        # type: () -> None
        return None

    def __verify_that_session_has_been_opened(self, image):
        if not self._is_opened:
            self.abort()
            raise EyesError("you must call eyes.open() before")
        if not self.configure.viewport_size:
            # in case open was called without viewport size and no check was called
            self._set_viewport_size({"width": image.width, "height": image.height})
            self._ensure_running_session()

    def extract_text(self, *regions):
        # type: (*OCRRegion) -> List[Text]
        self.__verify_that_session_has_been_opened(regions[0].image)
        return super(Eyes, self).extract_text(*regions)

    def extract_text_regions(self, config):
        # type: (TextRegionSettings) -> PATTERN_TEXT_REGIONS
        self.__verify_that_session_has_been_opened(config._image)
        return super(Eyes, self).extract_text_regions(config)

    def open(self, app_name, test_name, dimension=None):
        # type: (Text, Text, Optional[ViewPort]) -> None
        self._init_additional_providers()
        self.open_base(app_name, test_name, dimension)

    @typing.overload
    def check(self, name, check_settings):
        # type: (Text, ImagesCheckSettings) -> bool
        pass

    @typing.overload
    def check(self, check_settings):
        # type: (ImagesCheckSettings) -> None
        pass

    def check(self, check_settings, name=None):
        if self.configure.is_disabled:
            return False
        if isinstance(name, ImagesCheckSettings) or isinstance(
            check_settings, basestring
        ):
            check_settings, name = name, check_settings
        if name:
            check_settings = check_settings.with_name(name)

        image = check_settings.values.image
        if self.configure.viewport_size is None:
            self.configure.viewport_size = RectangleSize.from_(image)

        return self._check_image(
            check_settings.values.name,
            False,
            check_settings,
        )

    def check_image(self, image, tag=None, ignore_mismatch=False):
        # type: (Union[Image.Image, Text], Optional[Text], bool) -> Optional[bool]
        if self.configure.is_disabled:
            return None
        logger.info(
            "check_image(Image {}, tag {}, ignore_mismatch {}".format(
                image, tag, ignore_mismatch
            )
        )
        return self._check_image(tag, ignore_mismatch, Target.image(image))

    def check_region(self, image, region, tag=None, ignore_mismatch=False):
        # type: (Image.Image, Region, Optional[Text], bool) -> Optional[bool]
        if self.configure.is_disabled:
            return None
        logger.info(
            "check_region(Image {}, region {}, tag {}, ignore_mismatch {}".format(
                image, region, tag, ignore_mismatch
            )
        )
        return self._check_image(tag, ignore_mismatch, Target.region(image, region))

    def _check_image(self, name, ignore_mismatch, check_settings):
        # type: (Text, bool, ImagesCheckSettings) -> bool
        # Set the title to be linked to the screenshot.
        self._raw_title = name if name else ""
        if name:
            check_settings = check_settings.with_name(name)

        image = check_settings.values.image  # type: Image.Image
        self.__verify_that_session_has_been_opened(image)

        if check_settings.values.target_region:
            region_provider = RegionProvider(check_settings.values.target_region)
        else:
            region_provider = NULL_REGION_PROVIDER

        if not isinstance(self.cut_provider, NullCutProvider):
            logger.debug("cutting...")
            image = self.cut_provider.cut(image)
            self.debug_screenshots_provider.save(image, "cut")

        self._screenshot = EyesImagesScreenshot(image)
        check_settings = check_settings.timeout(0)
        match_result = self._check_window_base(
            region_provider, ignore_mismatch, check_settings, None
        )
        self._screenshot = None
        self._raw_title = None
        return match_result.as_expected
