import os
import typing as tp

if tp.TYPE_CHECKING:
    from applitools.core.metadata import BatchInfo
    from applitools.core.utils.custom_types import ViewPort, SessionType


class Configuration(object):
    # The batch to which the tests belong to. See BatchInfo. None means no batch.
    batch = None  # type: tp.Optional[BatchInfo]
    # A string identifying the branch in which tests are run.
    branch_name = os.environ.get('APPLITOOLS_BRANCH', None)  # type: tp.Optional[tp.Text]
    # A string identifying the parent branch of the branch set by "branch_name".
    parent_branch_name = os.environ.get('APPLITOOLS_PARENT_BRANCH', None)  # type: tp.Optional[tp.Text]
    # A string that, if specified, determines the baseline to compare with and disables automatic baseline
    # inference.
    baseline_branch_name = os.environ.get('APPLITOOLS_BASELINE_BRANCH', None)  # type: tp.Optional[tp.Text]
    # An optional string identifying the current library using the SDK.
    agent_id = None  # type: tp.Optional[tp.Text]
    baseline_env_name = None  # type: tp.Optional[tp.Text]
    environment_name = None  # type: tp.Optional[tp.Text]
    save_diffs = None  # type: bool
    app_name = None  # type: tp.Optional[tp.Text]
    test_name = None  # type: tp.Optional[tp.Text]
    viewport_size = None  # type: tp.Optional[ViewPort]
    session_type = None  # type: tp.Optional[SessionType]
