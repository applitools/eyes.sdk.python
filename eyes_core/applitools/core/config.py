import os
import typing as tp

import attr

if tp.TYPE_CHECKING:
    from applitools.core.metadata import BatchInfo
    from applitools.core.utils.custom_types import ViewPort, SessionType


@attr.s
class Configuration(object):
    # The batch to which the tests belong to. See BatchInfo. None means no batch.
    batch = attr.ib(default=None)  # type: tp.Optional[BatchInfo]
    # A string identifying the branch in which tests are run.
    branch_name = attr.ib(
        default=os.environ.get("APPLITOOLS_BRANCH", None)
    )  # type: tp.Optional[tp.Text]
    # A string identifying the parent branch of the branch set by "branch_name".
    parent_branch_name = attr.ib(
        default=os.environ.get("APPLITOOLS_PARENT_BRANCH", None)
    )  # type: tp.Optional[tp.Text]
    # A string that, if specified, determines the baseline to compare with and
    # disables automatic baseline inference.
    baseline_branch_name = attr.ib(
        default=os.environ.get("APPLITOOLS_BASELINE_BRANCH", None)
    )  # type: tp.Optional[tp.Text]
    # An optional string identifying the current library using the SDK.
    agent_id = attr.ib(default=None)  # type: tp.Optional[tp.Text]
    baseline_env_name = attr.ib(default=None)  # type: tp.Optional[tp.Text]
    environment_name = attr.ib(default=None)  # type: tp.Optional[tp.Text]
    save_diffs = attr.ib(default=None)  # type: bool
    app_name = attr.ib(default=None)  # type: tp.Optional[tp.Text]
    test_name = attr.ib(default=None)  # type: tp.Optional[tp.Text]
    viewport_size = attr.ib(default=None)  # type: tp.Optional[ViewPort]
    session_type = attr.ib(default=None)  # type: tp.Optional[SessionType]
