from typing import TYPE_CHECKING

import attr

from .utils.json_utils import JsonInclude

if TYPE_CHECKING:
    from typing import Optional, Text

    from .geometry import Point, RectangleSize

__all__ = ("AppOutput",)


@attr.s
class AppOutput(object):
    title = attr.ib(default=None, metadata={JsonInclude.NON_NONE: True})  # type: Text
    screenshot_bytes = attr.ib(default=None, repr=False)  # type: Optional[bytes]
    screenshot_url = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[Text]
    dom_url = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[Text]
    viewport = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[RectangleSize]
    location = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type: Optional[Point]
