from typing import Text

import attr

from applitools.common import Configuration

from .positioning import StitchMode


@attr.s
class SeleniumConfiguration(Configuration):
    DEFAULT_WAIT_BEFORE_SCREENSHOTS = 100

    force_full_page_screenshot = attr.ib(default=False)  # type: bool
    wait_before_screenshots = attr.ib(
        default=DEFAULT_WAIT_BEFORE_SCREENSHOTS
    )  # type: int
    stitch_mode = attr.ib(default=StitchMode.Scroll)  # type: Text
    hide_scrollbars = attr.ib(default=False)  # type: bool
    hide_caret = attr.ib(default=False)  # type: bool
