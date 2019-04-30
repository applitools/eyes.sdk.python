import typing

import attr

from .match import ImageMatchSettings
from .server import SessionType
from .utils.json_utils import JsonInclude

if typing.TYPE_CHECKING:
    from applitools.common import DeviceName, BatchInfo
    from typing import Optional, Text

__all__ = ("RunningSession", "AppEnvironment", "SessionStartInfo")


@attr.s
class RunningSession(object):
    """
    Encapsulates data for the session currently running in the agent.
    """

    id = attr.ib()  # type: Text
    session_id = attr.ib()  # type: Text
    batch_id = attr.ib()  # type: Text
    baseline_id = attr.ib()  # type: Text
    url = attr.ib()  # type: Text
    rendering_info = attr.ib(default=None)
    is_new_session = attr.ib(default=False)  # type: bool


def _to_device_info(v):
    # type: (Optional[DeviceName]) -> Text
    return "Desktop" if v is None else "{} (Chrome emulation)".format(v.value)


@attr.s
class AppEnvironment(object):
    os = attr.ib(default=None, metadata={JsonInclude.NON_NONE: True})
    hosting_app = attr.ib(default=None, metadata={JsonInclude.NON_NONE: True})
    display_size = attr.ib(default=None, metadata={JsonInclude.NON_NONE: True})
    device_info = attr.ib(
        default=None, converter=_to_device_info, metadata={JsonInclude.NON_NONE: True}
    )
    os_info = attr.ib(default=None, metadata={JsonInclude.NON_NONE: True})
    hosting_app_info = attr.ib(default=None, metadata={JsonInclude.NON_NONE: True})
    inferred = attr.ib(default=None, metadata={JsonInclude.NON_NONE: True})

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
    compare_with_parent_branch = attr.ib(
        metadata={JsonInclude.THIS: True}
    )  # type: bool
    ignore_baseline = attr.ib(metadata={JsonInclude.THIS: True})  # type: bool
    save_diffs = attr.ib(metadata={JsonInclude.THIS: True})  # type: bool
    render = attr.ib(metadata={JsonInclude.THIS: True})  # type: bool
    properties = attr.ib(metadata={JsonInclude.THIS: True})  # type: list
