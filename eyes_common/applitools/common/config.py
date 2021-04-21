import uuid
from copy import copy, deepcopy
from datetime import datetime
from typing import TYPE_CHECKING, Set

import attr

from applitools.common.accessibility import AccessibilitySettings
from applitools.common.geometry import RectangleSize
from applitools.common.match import ImageMatchSettings, MatchLevel
from applitools.common.server import FailureReports, SessionType
from applitools.common.utils import UTC, argument_guard
from applitools.common.utils.converters import str2bool
from applitools.common.utils.general_utils import get_env_with_prefix
from applitools.common.utils.json_utils import JsonInclude

if TYPE_CHECKING:
    from typing import TYPE_CHECKING, Dict, List, Optional, Text, TypeVar

    from applitools.common.utils.custom_types import ViewPort
    from applitools.core.feature import Feature

    Self = TypeVar("Self", bound="Configuration")  # typedef

__all__ = ("BatchInfo", "Configuration")

MINIMUM_MATCH_TIMEOUT_MS = 600
DEFAULT_MATCH_TIMEOUT_MS = 2000  # type: int
DEFAULT_SERVER_REQUEST_TIMEOUT_MS = 60 * 5 * 1000
DEFAULT_SERVER_URL = "https://eyesapi.applitools.com"


@attr.s(init=False, slots=True)
class BatchInfo(object):
    """
    A batch of tests.
    """

    name = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    started_at = attr.ib(metadata={JsonInclude.THIS: True})  # type: datetime
    sequence_name = attr.ib(
        metadata={JsonInclude.NAME: "batchSequenceName"}
    )  # type: Optional[Text]
    id = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    notify_on_completion = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: bool
    properties = attr.ib(
        metadata={JsonInclude.NON_NONE: True}
    )  # type: List[Dict[Text,Text]]

    def __init__(self, name=None, started_at=None, batch_sequence_name=None):
        # type: (Optional[Text], Optional[datetime], Optional[Text]) -> None
        self.id = get_env_with_prefix(
            "APPLITOOLS_BATCH_ID", str(uuid.uuid4())
        )  # type: Text
        self.name = get_env_with_prefix("APPLITOOLS_BATCH_NAME")  # type: Text
        self.started_at = datetime.now(UTC)  # type: datetime
        self.sequence_name = get_env_with_prefix(
            "APPLITOOLS_BATCH_SEQUENCE"
        )  # type: Optional[Text]
        self.notify_on_completion = str2bool(
            get_env_with_prefix("APPLITOOLS_BATCH_NOTIFY")
        )  # type: bool
        self.properties = []  # type: List[Dict[Text,Text]]

        if name:
            self.name = name
        if started_at:
            self.started_at = started_at
        if batch_sequence_name:
            self.sequence_name = batch_sequence_name

    def with_batch_id(self, id):
        # type: (Text) -> BatchInfo
        argument_guard.not_none(id)
        self.id = str(id)
        return self

    def add_property(self, name, value):
        # type: (Text, Text) -> BatchInfo
        """
        Associates a key/value pair with the Batch. This can be used later for filtering.
        :param name: (string) The property name.
        :param value: (string) The property value
        """
        self.properties.append({"name": name, "value": value})
        return self

    def clear_properties(self):
        # type: () -> BatchInfo
        """
        Clears the list of Batch properties.
        """
        del self.properties[:]
        return self


@attr.s
class Configuration(object):
    batch = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, factory=BatchInfo
    )  # type: BatchInfo
    branch_name = attr.ib(
        metadata={JsonInclude.NON_NONE: True},
        factory=lambda: get_env_with_prefix("APPLITOOLS_BRANCH", None),
    )  # type: Optional[Text]
    parent_branch_name = attr.ib(
        metadata={JsonInclude.NON_NONE: True},
        factory=lambda: get_env_with_prefix("APPLITOOLS_PARENT_BRANCH", None),
    )  # type: Optional[Text]
    baseline_branch_name = attr.ib(
        metadata={JsonInclude.NON_NONE: True},
        factory=lambda: get_env_with_prefix("APPLITOOLS_BASELINE_BRANCH", None),
    )  # type: Optional[Text]
    agent_id = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=None
    )  # type: Optional[Text]
    baseline_env_name = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=None
    )  # type: Optional[Text]
    environment_name = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=None
    )  # type: Optional[Text]
    save_diffs = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=None
    )  # type: bool
    app_name = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=None
    )  # type: Optional[Text]
    test_name = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=None
    )  # type: Optional[Text]
    viewport_size = attr.ib(
        metadata={JsonInclude.NON_NONE: True},
        default=None,
        converter=attr.converters.optional(RectangleSize.from_),
    )  # type: Optional[RectangleSize]
    session_type = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=SessionType.SEQUENTIAL
    )  # type: SessionType
    host_app = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=None
    )  # type: Optional[Text]
    host_os = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=None
    )  # type: Optional[Text]
    properties = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, factory=list
    )  # type: List[Dict[Text, Text]]
    match_timeout = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=DEFAULT_MATCH_TIMEOUT_MS
    )  # type: int # ms
    is_disabled = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=False
    )  # type: bool
    save_new_tests = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=True
    )  # type: bool
    save_failed_tests = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=False
    )  # type: bool
    failure_reports = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=FailureReports.ON_CLOSE
    )  # type: FailureReports
    send_dom = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=True
    )  # type: bool
    default_match_settings = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, factory=ImageMatchSettings
    )  # type: ImageMatchSettings
    stitch_overlap = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, default=5
    )  # type: int
    api_key = attr.ib(
        factory=lambda: get_env_with_prefix("APPLITOOLS_API_KEY", None)
    )  # type: Optional[Text]
    server_url = attr.ib(
        metadata={JsonInclude.NON_NONE: True},
        factory=lambda: get_env_with_prefix(
            "APPLITOOLS_SERVER_URL", DEFAULT_SERVER_URL
        ),
    )  # type: Text
    _timeout = attr.ib(default=DEFAULT_SERVER_REQUEST_TIMEOUT_MS)  # type: int # ms
    features = attr.ib(
        metadata={JsonInclude.NON_NONE: True}, factory=set
    )  # type: Set[Feature]

    @property
    def enable_patterns(self):
        # type: () -> bool
        return self.default_match_settings.enable_patterns

    @enable_patterns.setter
    def enable_patterns(self, enable_patterns):
        # type: (bool) -> None
        self.default_match_settings.enable_patterns = enable_patterns

    @property
    def use_dom(self):
        # type: () -> bool
        return self.default_match_settings.use_dom

    @use_dom.setter
    def use_dom(self, use_dom):
        # type: (bool) -> None
        self.default_match_settings.use_dom = use_dom

    @property
    def match_level(self):
        # type: () -> MatchLevel
        return self.default_match_settings.match_level

    @match_level.setter
    def match_level(self, match_level):
        # type: (MatchLevel) -> None
        self.default_match_settings.match_level = match_level

    @property
    def ignore_displacements(self):
        # type: () -> bool
        return self.default_match_settings.ignore_displacements

    @ignore_displacements.setter
    def ignore_displacements(self, ignore_displacements):
        # type: (bool) -> None
        self.default_match_settings.ignore_displacements = ignore_displacements

    def set_batch(self, batch):
        # type: (Self, BatchInfo) -> Self
        argument_guard.is_a(batch, BatchInfo)
        self.batch = batch
        return self

    def set_branch_name(self, branch_name):
        # type: (Self, Text) -> Self
        self.branch_name = branch_name
        return self

    def set_agent_id(self, agent_id):
        # type: (Self, Text) -> Self
        self.agent_id = agent_id
        return self

    def set_parent_branch_name(self, parent_branch_name):
        # type: (Self, Text) -> Self
        self.parent_branch_name = parent_branch_name
        return self

    def set_baseline_branch_name(self, baseline_branch_name):
        # type: (Self, Text) -> Self
        self.baseline_branch_name = baseline_branch_name
        return self

    def set_baseline_env_name(self, baseline_env_name):
        # type: (Self, Text) -> Self
        self.baseline_env_name = baseline_env_name
        return self

    def set_environment_name(self, environment_name):
        # type: (Self, Text) -> Self
        self.environment_name = environment_name
        return self

    def set_save_diffs(self, save_diffs):
        # type: (Self, bool) -> Self
        self.save_diffs = save_diffs
        return self

    def set_app_name(self, app_name):
        # type: (Self, Text) -> Self
        self.app_name = app_name
        return self

    def set_test_name(self, test_name):
        # type: (Self, Text) -> Self
        self.test_name = test_name
        return self

    def set_viewport_size(self, viewport_size):
        # type: (Self, ViewPort) -> Self
        self.viewport_size = viewport_size
        return self

    def set_session_type(self, session_type):
        # type: (Self, SessionType) -> Self
        self.session_type = session_type
        return self

    @property
    def ignore_caret(self):
        # type: () -> bool
        ignore = self.default_match_settings.ignore_caret
        return True if ignore is None else ignore

    def set_ignore_caret(self, ignore_caret):
        # type: (Self, bool) -> Self
        self.default_match_settings.ignore_caret = ignore_caret
        return self

    def set_host_app(self, host_app):
        # type: (Self, Text) -> Self
        self.host_app = host_app
        return self

    def set_host_os(self, host_os):
        # type: (Self, Text) -> Self
        self.host_os = host_os
        return self

    def set_match_timeout(self, match_timeout):
        # type: (Self, int) -> Self
        self.match_timeout = match_timeout
        return self

    def set_match_level(self, match_level):
        # type: (Self, MatchLevel) -> Self
        self.match_level = match_level
        return self

    def set_ignore_displacements(self, ignore_displacements):
        # type: (Self, bool) -> Self
        self.ignore_displacements = ignore_displacements
        return self

    def set_save_new_tests(self, save_new_tests):
        # type: (Self, bool) -> Self
        self.save_new_tests = save_new_tests
        return self

    def set_save_failed_tests(self, save_failed_tests):
        # type: (Self, bool) -> Self
        self.save_failed_tests = save_failed_tests
        return self

    def set_failure_reports(self, failure_reports):
        # type: (Self, FailureReports) -> Self
        self.failure_reports = failure_reports
        return self

    def set_send_dom(self, send_dom):
        # type: (Self, bool) -> Self
        self.send_dom = send_dom
        return self

    def set_use_dom(self, use_dom):
        # type: (Self, bool) -> Self
        self.use_dom = use_dom
        return self

    def set_enable_patterns(self, enable_patterns):
        # type: (Self, bool) -> Self
        self.enable_patterns = enable_patterns
        return self

    def set_stitch_overlap(self, stitch_overlap):
        # type: (Self, int) -> Self
        self.stitch_overlap = stitch_overlap
        return self

    def set_api_key(self, api_key):
        # type: (Self, Text) -> Self
        self.api_key = api_key
        return self

    def set_server_url(self, server_url):
        # type: (Self, Text) -> Self
        self.server_url = server_url
        return self

    def set_default_match_settings(self, default_match_settings):
        # type: (Self, ImageMatchSettings) -> Self
        self.default_match_settings = default_match_settings
        return self

    @property
    def accessibility_validation(self):
        # type: (Self) -> Optional[AccessibilitySettings]
        return self.default_match_settings.accessibility_settings

    @accessibility_validation.setter
    def accessibility_validation(self, accessibility_settings):
        # type: (Self, Optional[AccessibilitySettings]) -> None
        if accessibility_settings is None:
            self.self.default_match_settings.accessibility_settings = None
            return
        argument_guard.is_a(accessibility_settings, AccessibilitySettings)
        self.default_match_settings.accessibility_settings = accessibility_settings

    def set_accessibility_validation(self, accessibility_settings):
        # type: (Self, Optional[AccessibilitySettings]) -> Self
        self.accessibility_validation = accessibility_settings
        return self

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
        if isinstance(value, RectangleSize) or (
            isinstance(value, dict)
            and "width" in value.keys()
            and "height" in value.keys()
        ):
            return None

        raise ValueError("Wrong viewport type settled")

    @property
    def is_send_dom(self):
        # type: () -> bool
        return self.send_dom

    def clone(self):
        # type: () -> Self
        # TODO: Remove this huck when get rid of Python2
        # deepcopy on python 2 raise an exception so construct manually
        conf = copy(self)
        conf.batch = deepcopy(conf.batch)
        conf.viewport_size = copy(conf.viewport_size)
        conf.properties = deepcopy(conf.properties)
        conf.default_match_settings = deepcopy(conf.default_match_settings)
        conf.features = deepcopy(conf.features)
        return conf

    def add_property(self, name, value):
        # type: (Text, Text) -> Self
        """
        Associates a key/value pair with the test. This can be used later for filtering.
        :param name: (string) The property name.
        :param value: (string) The property value
        """
        self.properties.append({"name": name, "value": value})
        return self

    def clear_properties(self):
        # type: () -> Self
        """
        Clears the list of custom properties.
        """
        del self.properties[:]
        return self

    def set_features(self, *features):
        # type: (*Feature) -> Self
        self.features = set(features)
        return self

    def is_feature_activated(self, feature):
        # type: (Feature) -> bool
        return feature in self.features
