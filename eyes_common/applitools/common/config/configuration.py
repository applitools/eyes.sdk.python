import os
import uuid
from copy import copy
from datetime import datetime
from typing import Optional, Text

import attr

from applitools.common.geometry import RectangleSize
from applitools.common.match import ImageMatchSettings, MatchLevel
from applitools.common.server import FailureReports, SessionType
from applitools.common.utils import general_utils
from applitools.common.utils.converters import isoformat

__all__ = ("BatchInfo", "Branch", "Configuration")

MINIMUM_MATCH_TIMEOUT = 60  # Milliseconds


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
    )  # # type: Text
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
    DEFAULT_MATCH_TIMEOUT = 2000  # Milliseconds

    batch = attr.ib(default=None)  # type: Optional[BatchInfo]
    branch_name = attr.ib(
        factory=lambda: os.environ.get("APPLITOOLS_BRANCH", None)
    )  # type: Optional[Text]
    parent_branch_name = attr.ib(
        factory=lambda: os.environ.get("APPLITOOLS_PARENT_BRANCH", None)
    )  # type: Optional[Text]
    baseline_branch_name = attr.ib(
        factory=lambda: os.environ.get("APPLITOOLS_BASELINE_BRANCH", None)
    )  # type: Optional[Text]
    agent_id = attr.ib(default=None)  # type: Optional[Text]
    baseline_env_name = attr.ib(default=None)  # type: Optional[Text]
    environment_name = attr.ib(default=None)  # type: Optional[Text]
    save_diffs = attr.ib(default=None)  # type: bool
    app_name = attr.ib(default=None)  # type: Optional[Text]
    test_name = attr.ib(default=None)  # type: Optional[Text]
    viewport_size = attr.ib(
        default=None,
        converter=attr.converters.optional(lambda d: RectangleSize.from_(d)),
    )  # type:Optional[RectangleSize]
    session_type = attr.ib(default=SessionType.SEQUENTIAL)  # type: SessionType
    ignore_baseline = attr.ib(default=None)  # type: Optional[bool]
    ignore_caret = attr.ib(default=False)
    compare_with_parent_branch = attr.ib(default=None)  # type: Optional[bool]
    host_app = attr.ib(default=None)
    host_os = attr.ib(default=None)
    properties = attr.ib(factory=list)
    hide_scrollbars = attr.ib(default=False)
    match_timeout = attr.ib(default=DEFAULT_MATCH_TIMEOUT)
    match_level = attr.ib(default=MatchLevel.STRICT)  # TODO add converter to enum
    is_disabled = attr.ib(default=False)
    save_new_tests = attr.ib(default=True)
    save_failed_tests = attr.ib(default=False)
    fail_on_new_test = attr.ib(default=False)
    failure_reports = attr.ib(default=FailureReports.ON_CLOSE)
    send_dom = attr.ib(default=False)
    use_dom = attr.ib(default=False)
    enable_patterns = attr.ib(default=False)
    default_match_settings = attr.ib(default=ImageMatchSettings())
    hide_caret = attr.ib(init=False, default=None)
    stitching_overlap = attr.ib(init=False, default=50)

    @match_timeout.validator
    def validate1(self, attribute, value):
        if 0 < value < MINIMUM_MATCH_TIMEOUT:
            raise ValueError(
                "Match timeout must be at least {} ms.".format(MINIMUM_MATCH_TIMEOUT)
            )

    @viewport_size.validator
    def validate2(self, attribute, value):
        if value is None:
            return None
        if not isinstance(value, RectangleSize) or not (
            isinstance(value, dict)
            and "width" in value.keys()
            and "height" in value.keys()
        ):
            raise ValueError("Wrong viewport type settled")

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
