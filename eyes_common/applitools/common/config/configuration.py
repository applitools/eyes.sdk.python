import os
import typing
from copy import copy
from typing import Optional, Text

import attr

from applitools.common.metadata import SessionType

from .batch_info import BatchInfo

if typing.TYPE_CHECKING:
    from applitools.common.utils.custom_types import ViewPort


@attr.s
class Configuration(object):
    # The batch to which the tests belong to. See BatchInfo. None means no batch.
    batch = attr.ib(default=None)  # type: Optional[BatchInfo]
    # A string identifying the branch in which tests are run.
    branch_name = attr.ib(
        default=os.environ.get("APPLITOOLS_BRANCH", None)
    )  # type: Optional[Text]
    # A string identifying the parent branch of the branch set by "branch_name".
    parent_branch_name = attr.ib(
        default=os.environ.get("APPLITOOLS_PARENT_BRANCH", None)
    )  # type: Optional[Text]
    # A string that, if specified, determines the baseline to compare with and
    # disables automatic baseline inference.
    baseline_branch_name = attr.ib(
        default=os.environ.get("APPLITOOLS_BASELINE_BRANCH", None)
    )  # type: Optional[Text]
    # An optional string identifying the current library using the SDK.
    agent_id = attr.ib(default=None)  # type: Optional[Text]
    baseline_env_name = attr.ib(default=None)  # type: Optional[Text]
    environment_name = attr.ib(default=None)  # type: Optional[Text]
    save_diffs = attr.ib(default=None)  # type: bool
    app_name = attr.ib(default=None)  # type: Optional[Text]
    test_name = attr.ib(default=None)  # type: Optional[Text]
    _viewport_size = attr.ib(default=None)  # type: Optional[ViewPort]
    session_type = attr.ib(default=None)  # type: Optional[SessionType]

    @property
    def viewport_size(self):
        return self._viewport_size

    @viewport_size.setter
    def viewport_size(self, value):
        self._viewport_size = value

    def clone(self):
        return copy(self)
