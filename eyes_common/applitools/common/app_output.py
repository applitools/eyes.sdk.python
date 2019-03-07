import typing
from datetime import datetime
from typing import List, Text

import attr

from .match import ImageMatchSettings

if typing.TYPE_CHECKING:
    Image = typing.ByteString
    from .match import FloatingMatchSettings
    from .capture import EyesScreenshot
    from .geometry import Region
    from .utils.custom_types import UserInputs

    T = typing.TypeVar("T", bound="CheckSettings")

__all__ = (
    "AppOutput",
    "AppOutputWithScreenshot",
    "AppOutputProvider",
    "ExpectedAppOutput",
    "ActualAppOutput",
)


@attr.s
class Annotations(object):
    floating = attr.ib(default=None)  # type: List[FloatingMatchSettings]
    ignore = attr.ib(default=None)  # type: List[Region]
    strict = attr.ib(default=None)  # type: List[Region]
    content = attr.ib(default=None)  # type: List[Region]
    layout = attr.ib(default=None)  # type: List[Region]


@attr.s
class AppOutput(object):
    title = attr.ib()
    screenshot64 = attr.ib(repr=False)
    screenshot_url = attr.ib(default=None)
    dom_url = attr.ib(default=None)


@attr.s
class AppOutputWithScreenshot(object):
    app_output = attr.ib(type=AppOutput)  # type: AppOutput
    screenshot = attr.ib()  # type: EyesScreenshot


@attr.s
class AppOutputProvider(object):
    method = attr.ib()

    def get_app_output(self, region, last_screenshot, check_settings):
        # type: (Region, EyesScreenshot, T) -> AppOutputWithScreenshot
        return self.method(region, last_screenshot, check_settings)


@attr.s
class ExpectedAppOutput(object):
    tag = attr.ib()  # type: Text
    image = attr.ib()  # type: Image
    thumbprint = attr.ib()  # type: Image
    annotations = attr.ib(type=Annotations)  # type: Annotations
    # occurred_at = attr.ib(factory=lambda t: datetime.fromisoformat(t))  # type: datetime
    occurred_at = attr.ib()  # type: Text


@attr.s
class ActualAppOutput(object):
    image = attr.ib()  # type: Image
    thumbprint = attr.ib()  # type: Image
    image_match_settings = attr.ib(type=ImageMatchSettings)  # type: ImageMatchSettings
    ignore_expected_output_settings = attr.ib()  # type: bool
    is_matching = attr.ib()  # type: bool
    are_images_matching = attr.ib()  # type: bool
    occurred_at = attr.ib()  # type: datetime
    user_inputs = attr.ib()  # type: UserInputs
    window_title = attr.ib()  # type: Text
    tag = attr.ib()  # type: Text
    is_primary = attr.ib()  # type: bool
