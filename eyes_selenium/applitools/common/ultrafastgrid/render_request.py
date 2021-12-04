import typing

import attr

from applitools.common.utils.json_utils import JsonInclude

if typing.TYPE_CHECKING:
    from typing import Optional, Text


__all__ = ("RenderingInfo",)


@attr.s(frozen=True)
class RenderingInfo(object):
    service_url = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Text]
    access_token = attr.ib(
        default=None, repr=False, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Text]
    results_url = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Text]
    stitching_service_url = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[Text]
    max_image_height = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[int]
    max_image_area = attr.ib(
        default=None, metadata={JsonInclude.THIS: True}
    )  # type: Optional[int]
