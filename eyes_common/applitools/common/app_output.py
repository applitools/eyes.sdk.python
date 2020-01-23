from typing import Optional, Text

import attr

from .utils.json_utils import JsonInclude

__all__ = ("AppOutput",)


@attr.s
class AppOutput(object):
    title = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    screenshot_bytes = attr.ib(repr=False)  # type: Optional[bytes]
    screenshot_url = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[Text]
    dom_url = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[Text]
