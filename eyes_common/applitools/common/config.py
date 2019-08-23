import os
import uuid
from copy import copy
from datetime import datetime
from typing import Dict, List, Optional, Text, Union

import attr

from applitools.common import logger
from applitools.common.geometry import RectangleSize
from applitools.common.match import ImageMatchSettings, MatchLevel
from applitools.common.server import FailureReports, SessionType
from applitools.common.utils import UTC, argument_guard
from applitools.common.utils.json_utils import JsonInclude

__all__ = ("BatchInfo", "Configuration")

MINIMUM_MATCH_TIMEOUT_MS = 600
DEFAULT_MATCH_TIMEOUT_MS = 2000  # type: int
DEFAULT_SERVER_REQUEST_TIMEOUT_MS = 60 * 5 * 1000
DEFAULT_SERVER_URL = "https://eyesapi.applitools.com"


@attr.s
class BatchInfo(object):
    """
    A batch of tests.
    """

    name = attr.ib(
        factory=lambda: os.getenv("APPLITOOLS_BATCH_NAME"),
        metadata={JsonInclude.THIS: True},
    )  # type: Optional[Text]
    started_at = attr.ib(
        factory=lambda: datetime.now(UTC), metadata={JsonInclude.THIS: True}
    )  # type: Union[datetime, Text]
    sequence_name = attr.ib(
        init=False,
        factory=lambda: os.getenv("APPLITOOLS_BATCH_SEQUENCE"),
        metadata={JsonInclude.NAME: "batchSequenceName"},
    )  # type: Optional[Text]
    id = attr.ib(
        init=False,
        converter=str,
        factory=lambda: os.getenv("APPLITOOLS_BATCH_ID", str(uuid.uuid4())),
        metadata={JsonInclude.THIS: True},
    )  # type: Text

    def with_batch_id(self, id):
        # type: (Union[Text, int]) -> BatchInfo
        argument_guard.not_none(id)
        self.id = str(id)
        return self


@attr.s
class Configuration(object):
    batch = attr.ib(default=None)  # type: Optional[BatchInfo]
    branch_name = attr.ib(
        factory=lambda: os.getenv("APPLITOOLS_BRANCH", None)
    )  # type: Optional[Text]
    parent_branch_name = attr.ib(
        factory=lambda: os.getenv("APPLITOOLS_PARENT_BRANCH", None)
    )  # type: Optional[Text]
    baseline_branch_name = attr.ib(
        factory=lambda: os.getenv("APPLITOOLS_BASELINE_BRANCH", None)
    )  # type: Optional[Text]
    agent_id = attr.ib(default=None)  # type: Optional[Text]
    baseline_env_name = attr.ib(default=None)  # type: Optional[Text]
    environment_name = attr.ib(default=None)  # type: Optional[Text]
    save_diffs = attr.ib(default=None)  # type: bool
    app_name = attr.ib(default=None)  # type: Optional[Text]
    test_name = attr.ib(default=None)  # type: Optional[Text]
    viewport_size = attr.ib(
        default=None, converter=attr.converters.optional(RectangleSize.from_)
    )  # type: Optional[RectangleSize]
    session_type = attr.ib(default=SessionType.SEQUENTIAL)  # type: SessionType
    ignore_baseline = attr.ib(default=None)  # type: Optional[bool]
    ignore_caret = attr.ib(default=False)  # type: bool
    compare_with_parent_branch = attr.ib(default=None)  # type: Optional[bool]
    host_app = attr.ib(default=None)  # type: Optional[Text]
    host_os = attr.ib(default=None)  # type: Optional[Text]
    properties = attr.ib(factory=list)  # type: List[Dict[Text, Text]]
    hide_scrollbars = attr.ib(default=False)  # type: bool
    match_timeout = attr.ib(default=DEFAULT_MATCH_TIMEOUT_MS)  # type: int # ms
    match_level = attr.ib(
        default=MatchLevel.STRICT, converter=MatchLevel
    )  # type: MatchLevel
    is_disabled = attr.ib(default=False)  # type: bool
    save_new_tests = attr.ib(default=True)  # type: bool
    save_failed_tests = attr.ib(default=False)  # type: bool
    fail_on_new_test = attr.ib(default=False)  # type: bool
    failure_reports = attr.ib(default=FailureReports.ON_CLOSE)  # type: FailureReports
    send_dom = attr.ib(default=True)  # type: bool
    use_dom = attr.ib(default=False)  # type: bool
    enable_patterns = attr.ib(default=False)  # type: bool
    default_match_settings = attr.ib(
        default=ImageMatchSettings()
    )  # type: ImageMatchSettings
    hide_caret = attr.ib(init=False, default=None)  # type: Optional[bool]
    stitching_overlap = attr.ib(init=False, default=5)  # type: int

    api_key = attr.ib(
        factory=lambda: os.getenv("APPLITOOLS_API_KEY", None)
    )  # type: Optional[Text]
    server_url = attr.ib(default=DEFAULT_SERVER_URL)  # type: Text
    timeout = attr.ib(default=DEFAULT_SERVER_REQUEST_TIMEOUT_MS)  # type: int # ms

    @match_timeout.validator
    def _validate1(self, attribute, value):
        if 0 < value < MINIMUM_MATCH_TIMEOUT_MS:
            raise ValueError(
                "Match timeout must be at least {} ms.".format(MINIMUM_MATCH_TIMEOUT_MS)
            )

    @viewport_size.validator
    def _validate2(self, attribute, value):
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
        # type: () -> bool
        logger.deprecation("Use is_send_dom instead")
        return self.is_send_dom

    @property
    def is_send_dom(self):
        # type: () -> bool
        return self.send_dom

    def clone(self):
        # type: () -> Configuration
        return copy(self)
