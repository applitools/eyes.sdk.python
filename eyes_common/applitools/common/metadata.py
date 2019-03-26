import typing

import attr

from .config import BatchInfo, Branch
from .match import ImageMatchSettings, MatchLevel
from .server import SessionType
from .utils import general_utils

if typing.TYPE_CHECKING:
    from typing import Optional, Text, List
    from .utils.custom_types import Num
    from .app_output import ExpectedAppOutput, ActualAppOutput

__all__ = (
    "RunningSession",
    "AppEnvironment",
    "StartInfo",
    "SessionStartInfo",
    "SessionResults",
)


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


@attr.s
class AppEnvironment(object):
    os = attr.ib(default=None)
    hosting_app = attr.ib(default=None)
    display_size = attr.ib(default=None)
    device_info = attr.ib(default=None)
    os_info = attr.ib(default=None)
    hosting_app_info = attr.ib(default=None)
    inferred = attr.ib(default=None)

    @classmethod
    def from_inferred(cls, inferred):
        return cls(inferred=inferred)


@attr.s
class StartInfo(object):
    session_type = attr.ib(type=SessionType)  # type: SessionType
    is_transient = attr.ib()  # type: bool
    ignore_baseline = attr.ib()  # type: bool
    app_id_or_name = attr.ib()  # type: Text
    compare_with_parent_branch = attr.ib()
    scenario_id_or_name = attr.ib()  # type: Text
    match_level = attr.ib(validator=attr.validators.in_(MatchLevel))  # type: Text
    agent_id = attr.ib()  # type: Text
    batch_info = attr.ib(type=BatchInfo)  # type: BatchInfo
    environment = attr.ib(type=AppEnvironment)  # type: AppEnvironment
    default_match_settings = attr.ib(
        type=ImageMatchSettings
    )  # type: ImageMatchSettings
    properties = attr.ib(factory=list)  # type: List


@attr.s
class SessionStartInfo(object):
    agent_id = attr.ib()  # type: Text
    session_type = attr.ib(type=SessionType)  # type: SessionType
    app_id_or_name = attr.ib()  # type: Text
    ver_id = attr.ib()  # type: Optional[Text]
    scenario_id_or_name = attr.ib()  # type: Text
    batch_info = attr.ib(type=BatchInfo)  # type: BatchInfo
    baseline_env_name = attr.ib()  # type: Text
    environment_name = attr.ib()  # type: Text
    environment = attr.ib(type=AppEnvironment)  # type: AppEnvironment
    default_match_settings = attr.ib(
        type=ImageMatchSettings
    )  # type: ImageMatchSettings
    branch_name = attr.ib()  # type: Text
    parent_branch_name = attr.ib()  # type: Text
    baseline_branch_name = attr.ib()  # type: Text
    compare_with_parent_branch = attr.ib()  # type: bool
    ignore_baseline = attr.ib()  # type: bool
    save_diffs = attr.ib()  # type: bool
    render = attr.ib()  # type: bool
    properties = attr.ib()  # type: list

    def to_json(self):
        return '{"startInfo": %s}' % (general_utils.to_json(self))


@attr.s
class SessionResults(object):
    id = attr.ib()  # type: Text
    revision = attr.ib()  # type: Num
    running_session_id = attr.ib()  # type: Text
    is_aborted = attr.ib()  # type:bool
    is_starred = attr.ib()  # type:bool
    start_info = attr.ib()  # type: StartInfo
    batch_id = attr.ib()  # type:Text
    secret_token = attr.ib()  # type:Text
    state = attr.ib()  # type:Text
    status = attr.ib()  # type:Text
    is_default_status = attr.ib()  # type:bool
    started_at = attr.ib()  # type:Text
    duration = attr.ib()  # type:Text
    is_different = attr.ib()  # type:bool
    env = attr.ib()  # type: AppEnvironment
    branch = attr.ib()  # type: Branch
    expected_app_output = attr.ib()  # type: ExpectedAppOutput
    actual_app_output = attr.ib()  # type: ActualAppOutput
    baseline_id = attr.ib()  # type: Text
    baseline_rev_id = attr.ib()  # type: Text
    scenario_id = attr.ib()  # type: Text
    scenario_name = attr.ib()  # type: Text
    app_id = attr.ib()  # type: Text
    baseline_model_id = attr.ib()  # type: Text
    baseline_env_id = attr.ib()  # type: Text
    baseline_env = attr.ib()  # type: AppEnvironment
    app_name = attr.ib()  # type: Text
    baseline_branch_name = attr.ib()  # type: Text
    is_new = attr.ib()  # type: bool
