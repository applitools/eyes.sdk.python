import typing

from applitools.common import Configuration, EyesError, RectangleSize, Region, logger
from applitools.core import NULL_REGION_PROVIDER, EyesBase, RegionProvider
from applitools.images.fluent import ImagesCheckSettings, Target

from .__version__ import __version__
from .capture import EyesImagesScreenshot

if typing.TYPE_CHECKING:
    from typing import Text, Union, Optional, Dict
    from PIL import Image
    from applitools.common.utils.custom_types import ViewPort


class Eyes(EyesBase):
    DELEGATE_TO_CONFIG = Configuration.all_fields()

    _raw_title = None  # type: Optional[Text]
    _screenshot = None  # type: Optional[EyesImagesScreenshot]
    _inferred = None  # type: Optional[Text]

    def __getattr__(self, name):
        if name in self.DELEGATE_TO_CONFIG:
            return getattr(self.configuration, name)
        raise AttributeError("{} has not attr {}".format(self.__class__.__name__, name))

    def __setattr__(self, name, value):
        if name in self.DELEGATE_TO_CONFIG:
            setattr(self.configuration, name, value)
        else:
            super(Eyes, self).__setattr__(name, value)

    @property
    def full_agent_id(self):
        # type: () -> Text
        if self.agent_id is None:
            return self.base_agent_id
        return "%s [%s]" % (self.agent_id, self.base_agent_id)

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

    @staticmethod
    def get_viewport_size_static():
        pass

    @staticmethod
    def set_viewport_size_static(value):
        pass

    def _get_viewport_size(self):
        # type: () -> RectangleSize
        return self.configuration.viewport_size

    def _set_viewport_size(self, size):
        # type: (ViewPort) -> None
        self.configuration.viewport_size = size  # type: ignore

    def _ensure_viewport_size(self):
        pass

    def _get_screenshot(self, **kwargs):
        # type: (**Dict) -> EyesImagesScreenshot
        return self._screenshot

    def _try_capture_dom(self):
        # type: () -> None
        return None

    def open(self, app_name, test_name, dimension=None):
        # type: (Text, Text, Optional[ViewPort]) -> None
        self.open_base(app_name, test_name, dimension)

    def check(self, name, check_settings):
        # type: (Text, ImagesCheckSettings) -> bool
        if self.configuration.is_disabled:
            return False
        if name:
            check_settings = check_settings.with_name(name)
        else:
            name = check_settings.values.name

        image = check_settings.values.image
        if self.configuration.viewport_size is None:
            self.configuration.viewport_size = RectangleSize.from_(image)

        return self._check_image(NULL_REGION_PROVIDER, name, False, check_settings)

    def check_image(self, image, tag=None, ignore_mismatch=False):
        # type: (Union[Image.Image, Text], Optional[Text], bool) -> Optional[bool]
        if self.configuration.is_disabled:
            return None
        logger.info(
            "check_image(Image {}, tag {}, ignore_mismatch {}".format(
                image, tag, ignore_mismatch
            )
        )
        return self._check_image(
            NULL_REGION_PROVIDER, tag, ignore_mismatch, Target.image(image)
        )

    def check_region(self, image, region, tag=None, ignore_mismatch=False):
        # type: (Image.Image, Region, Optional[Text], bool) -> Optional[bool]
        if self.configuration.is_disabled:
            return None
        logger.info(
            "check_region(Image {}, region {}, tag {}, ignore_mismatch {}".format(
                image, region, tag, ignore_mismatch
            )
        )
        return self._check_image(
            NULL_REGION_PROVIDER, tag, ignore_mismatch, Target.region(image, region)
        )

    def _check_image(self, region_provider, name, ignore_mismatch, check_settings):
        # type: (RegionProvider, Text, bool, ImagesCheckSettings) -> bool
        # Set the title to be linked to the screenshot.
        self._raw_title = name if name else ""

        if not self.is_opened:
            self.abort_if_not_closed()
            raise EyesError("you must call open() before checking")

        image = check_settings.values.image  # type: Image.Image
        # TODO: Add cut provider

        self._screenshot = EyesImagesScreenshot(image)
        if not self.configuration.viewport_size:
            self._set_viewport_size(
                RectangleSize(width=image.width, height=image.height)
            )

        check_settings = check_settings.timeout(0)
        match_result = self._check_window_base(
            region_provider, self._raw_title, ignore_mismatch, check_settings
        )
        self._screenshot = None
        self._raw_title = None
        return match_result.as_expected
