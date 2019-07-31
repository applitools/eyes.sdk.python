from typing import Text, Optional

import attr

from .utils.json_utils import JsonInclude

__all__ = ("AppOutput",)


@attr.s
class AppOutput(object):
    title = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    screenshot64 = attr.ib(
        repr=False, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[Text]
    screenshot_url = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[Text]
    dom_url = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[Text]
