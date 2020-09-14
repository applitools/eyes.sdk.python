import typing

import attr

from .match import ImageMatchSettings
from .server import SessionType
from .utils.compat import basestring
from .utils.json_utils import JsonInclude

if typing.TYPE_CHECKING:
    from typing import Optional, Text, Union

    from applitools.common import (
        BatchInfo,
        DeviceName,
        IosDeviceName,
        RectangleSize,
        RenderingInfo,
    )

__all__ = ("RunningSession", "AppEnvironment", "SessionStartInfo")


@attr.s
class RunningSession(object):
    """
    Encapsulates data for the session currently running in the agent.
    """

    id = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    session_id = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    batch_id = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    baseline_id = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    url = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    rendering_info = attr.ib(default=None)  # type: Optional[RenderingInfo]
    is_new_session = attr.ib(
        default=False, metadata={JsonInclude.NAME: "isNew"}
    )  # type: bool


def _to_device_info(v):
    # type: (Optional[Union[DeviceName, IosDeviceName, Text]]) -> Text
    # import here because in global scope causing circular import reference
    from .ultrafastgrid.config import DeviceName, IosDeviceName  # noqa

    if isinstance(v, basestring):
        return v
    elif isinstance(v, DeviceName):
        return "{} (Chrome emulation)".format(v.value)
    elif isinstance(v, IosDeviceName):
        return v.value
    return "Desktop"


@attr.s
class AppEnvironment(object):
    os = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type:Optional[Text]
    hosting_app = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type:Optional[Text]
    display_size = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type:Optional[RectangleSize]
    device_info = attr.ib(
        default=None, converter=_to_device_info, metadata={JsonInclude.NON_NONE: True}
    )  # type:Optional[Text]
    os_info = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type:Optional[Text]
    hosting_app_info = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type:Optional[Text]
    inferred = attr.ib(
        default=None, metadata={JsonInclude.NON_NONE: True}
    )  # type:Optional[Text]

    @classmethod
    def from_inferred(cls, inferred):
        return cls(inferred=inferred)


@attr.s
class SessionStartInfo(object):
    JSON_NAME = "startInfo"
    agent_id = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    session_type = attr.ib(
        type=SessionType, metadata={JsonInclude.THIS: True}
    )  # type: SessionType
    app_id_or_name = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    ver_id = attr.ib(metadata={JsonInclude.THIS: True})  # type: Optional[Text]
    scenario_id_or_name = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    batch_info = attr.ib(metadata={JsonInclude.THIS: True})  # type: BatchInfo
    baseline_env_name = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Text
    environment_name = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    environment = attr.ib(
        type=AppEnvironment, metadata={JsonInclude.THIS: True}
    )  # type: AppEnvironment
    default_match_settings = attr.ib(
        type=ImageMatchSettings, metadata={JsonInclude.THIS: True}
    )  # type: ImageMatchSettings
    branch_name = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    parent_branch_name = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    baseline_branch_name = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    save_diffs = attr.ib(metadata={JsonInclude.THIS: True})  # type: bool
    render = attr.ib(metadata={JsonInclude.THIS: True})  # type: bool
    properties = attr.ib(metadata={JsonInclude.THIS: True})  # type: list
