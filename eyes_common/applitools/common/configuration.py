import os
import typing
import uuid
from copy import copy
from datetime import datetime
from typing import Optional, Text

import attr

from applitools.common.utils import general_utils
from applitools.common.utils.converters import isoformat

if typing.TYPE_CHECKING:
    from applitools.common.metadata import SessionType
    from applitools.common.utils.custom_types import ViewPort
__all__ = ("BatchInfo", "Branch", "Configuration")


@attr.s
class BatchInfo(object):
    """
    A batch of tests.
    """

    name = attr.ib(
        factory=lambda: os.environ.get("APPLITOOLS_BATCH_NAME")
    )  # type: Optional[Text]
    started_at = attr.ib(
        factory=lambda: datetime.now(general_utils.UTC), converter=isoformat
    )  # # type: ignore
    id = attr.ib(
        factory=lambda: os.environ.get("APPLITOOLS_BATCH_ID", str(uuid.uuid4()))
    )  # type: Text

    @property
    def id_(self):
        # TODO: Remove in this way of initialization in future
        return self.id

    @id_.setter
    def id_(self, value):
        self.id = value


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
    ignore_baseline = attr.ib(default=None)  # type: Optional[bool]
    ignore_caret = attr.ib(default=False)
    send_dom = attr.ib(default=False)
    compare_with_parent_branch = attr.ib(default=None)  # type: Optional[bool]

    @property
    def viewport_size(self):
        return self._viewport_size

    @viewport_size.setter
    def viewport_size(self, value):
        self._viewport_size = value

    @property
    def is_dom_send(self):
        return self.send_dom

    def clone(self):
        return copy(self)


@attr.s
class Branch(object):
    id = attr.ib()
    name = attr.ib()
    is_deleted = attr.ib()
    update_info = attr.ib()
